"""Абстракции пагинации для типизированных ответов SDK."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from avito.core.types import JsonPage

type PageFetcher[ItemT] = Callable[[int | None, str | None], JsonPage[ItemT]]


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


__all__ = ("Paginator", "PageFetcher")
