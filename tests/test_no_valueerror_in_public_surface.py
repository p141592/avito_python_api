from __future__ import annotations

from pathlib import Path


def test_public_domain_and_client_surface_does_not_raise_valueerror() -> None:
    root = Path(__file__).resolve().parent.parent / "avito"
    offenders: list[str] = []

    for path in root.glob("*/domain.py"):
        text = path.read_text(encoding="utf-8")
        if "raise ValueError" in text:
            offenders.append(path.as_posix())

    for path in root.glob("*/client.py"):
        text = path.read_text(encoding="utf-8")
        if "raise ValueError" in text:
            offenders.append(path.as_posix())

    assert offenders == []
