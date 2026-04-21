from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.fake_transport import FakeTransport

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def fake_transport() -> FakeTransport:
    return FakeTransport()
