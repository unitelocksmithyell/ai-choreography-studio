"""Wall-clock + perf counters for pipeline stages."""
from __future__ import annotations

import time
from contextlib import contextmanager
from collections.abc import Iterator

from choreo_utils.logging import get_logger

_log = get_logger(__name__)


@contextmanager
def stage(name: str) -> Iterator[None]:
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = (time.perf_counter() - t0) * 1000.0
        _log.info("stage %-20s %8.1f ms", name, dt)