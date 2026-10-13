"""Path safety: keep user-supplied paths inside the project root."""
from __future__ import annotations

from pathlib import Path


class PathEscapeError(ValueError):
    """Raised when a path resolves outside the allowed root."""


def safe_join(root: Path, user_path: str | Path) -> Path:
    root = root.resolve()
    candidate = (root / user_path).resolve()
    if root != candidate and root not in candidate.parents:
        raise PathEscapeError(f"{user_path!r} escapes {root}")
    return candidate