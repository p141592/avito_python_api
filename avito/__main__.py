"""Точка входа модуля для локальной smoke-проверки."""

from avito.client import AvitoClient


def main() -> None:
    """Создает фасад, чтобы `python -m avito` работал как smoke-проверка."""

    AvitoClient()


if __name__ == "__main__":
    main()
