"""Абстракции пагинации для типизированных ответов SDK."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import SupportsIndex, overload

from avito.core.types import JsonPage

type PageFetcher[ItemT] = Callable[[int | None, str | None], JsonPage[ItemT]]


class PaginatedList[ItemT](list[ItemT]):
    """Ленивый list-like контейнер для элементов из последовательности страниц.

    Контракт:

    - уже загруженные элементы читаются без повторных запросов;
    - чтение по индексу, slice и частичная итерация подгружают только нужные страницы;
    - `materialize()` выполняет явную полную загрузку всех оставшихся страниц.
    """

    def __init__(
        self,
        fetch_page: PageFetcher[ItemT],
        *,
        start_page: int = 1,
        first_page: JsonPage[ItemT] | None = None,
    ) -> None:
        super().__init__()
        self._fetch_page = fetch_page
        self._known_total: int | None = None
        self._source_total: int | None = None
        self._next_page_number: int | None = start_page
        self._next_cursor: str | None = None
        self._exhausted = False

        if first_page is not None:
            self._consume_page(first_page)

    def __iter__(self) -> Iterator[ItemT]:
        index = 0
        while True:
            if index < super().__len__():
                yield super().__getitem__(index)
                index += 1
                continue
            if self._exhausted:
                return
            self._load_next_page()

    def __len__(self) -> int:
        if self._known_total is not None:
            return self._known_total
        self._ensure_all_loaded()
        return super().__len__()

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> ItemT: ...

    @overload
    def __getitem__(
        self,
        index: slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
        /,
    ) -> list[ItemT]: ...

    def __getitem__(
        self,
        index: SupportsIndex
        | slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
        /,
    ) -> ItemT | list[ItemT]:
        if isinstance(index, slice):
            self._ensure_slice_loaded(index)
            return list(super().__getitem__(index))

        resolved_index = index.__index__()
        if resolved_index < 0:
            self._ensure_all_loaded()
        else:
            self._ensure_loaded_until(resolved_index)
        return super().__getitem__(index)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            self._ensure_all_loaded()
        return super().__eq__(other)

    @property
    def loaded_count(self) -> int:
        """Количество элементов, уже загруженных локально."""

        return super().__len__()

    @property
    def known_total(self) -> int | None:
        """Общее количество элементов, если API вернул достоверный total."""

        return self._known_total

    @property
    def source_total(self) -> int | None:
        """Общий total из API без ограничения локальным limit."""

        return self._source_total

    @property
    def is_materialized(self) -> bool:
        """Показывает, загружены ли все страницы коллекции."""

        return self._exhausted

    def materialize(self) -> list[ItemT]:
        """Явно загружает все страницы и возвращает snapshot-список."""

        self._ensure_all_loaded()
        return list(super().__iter__())

    def _ensure_slice_loaded(self, slice_index: slice) -> None:
        if (
            slice_index.step is not None
            and slice_index.step < 0
            or slice_index.start is not None
            and slice_index.start < 0
            or slice_index.stop is not None
            and slice_index.stop < 0
            or slice_index.stop is None
        ):
            self._ensure_all_loaded()
            return

        stop = slice_index.stop
        if stop is None or stop <= 0:
            return
        self._ensure_loaded_until(stop - 1)

    def _ensure_loaded_until(self, index: int) -> None:
        while super().__len__() <= index and not self._exhausted:
            self._load_next_page()

    def _ensure_all_loaded(self) -> None:
        while not self._exhausted:
            self._load_next_page()

    def _load_next_page(self) -> None:
        if self._exhausted:
            return

        page = self._fetch_page(self._next_page_number, self._next_cursor)
        self._consume_page(page)

    def _consume_page(self, page: JsonPage[ItemT]) -> None:
        super().extend(page.items)
        self._known_total = page.total
        if page.source_total is not None:
            self._source_total = page.source_total

        if not page.has_next:
            self._exhausted = True
            self._next_page_number = None
            self._next_cursor = None
            return

        if page.next_cursor is not None:
            self._next_cursor = page.next_cursor
            self._next_page_number = None
            return

        if page.page is not None:
            self._next_page_number = page.page + 1
            self._next_cursor = None
            return

        if self._next_page_number is not None:
            self._next_page_number += 1
            return

        self._exhausted = True
        self._next_cursor = None


class Paginator[ItemT]:
    """Обходит страницы API и собирает типизированный результат."""

    def __init__(self, fetch_page: PageFetcher[ItemT]) -> None:
        self._fetch_page = fetch_page

    def iter_pages(self, *, start_page: int = 1) -> Iterator[JsonPage[ItemT]]:
        """Итерирует страницы, пока API сообщает о продолжении списка."""

        page_number: int | None = start_page
        cursor: str | None = None
        while True:
            page = self._fetch_page(page_number, cursor)
            yield page
            if not page.has_next:
                return
            if page.next_cursor is not None:
                cursor = page.next_cursor
                page_number = None
                continue
            if page_number is None:
                return
            page_number += 1

    def collect(self, *, start_page: int = 1) -> list[ItemT]:
        """Собирает элементы всех страниц в один список."""

        items: list[ItemT] = []
        for page in self.iter_pages(start_page=start_page):
            items.extend(page.items)
        return items

    def as_list(
        self,
        *,
        start_page: int = 1,
        first_page: JsonPage[ItemT] | None = None,
    ) -> PaginatedList[ItemT]:
        """Возвращает ленивый list-like контейнер поверх последовательности страниц."""

        return PaginatedList(
            self._fetch_page,
            start_page=start_page,
            first_page=first_page,
        )


__all__ = ("PaginatedList", "Paginator", "PageFetcher")
