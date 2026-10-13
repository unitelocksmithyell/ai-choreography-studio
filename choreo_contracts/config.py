"""Host configuration. Loads config/default.toml, overridable by env + CLI."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel


class HostConfig(BaseModel):
    repo_root: Path
    log_level: str = "INFO"
    log_file: Path | None = None
    plugin_api_version: str = "1.0"
    sandbox: str = "in_process"  # in_process | subprocess
    remote_registry: bool = False
    ffmpeg_path: str = "ffmpeg"

    @classmethod
    def load(cls, config_path: Path | None = None) -> "HostConfig":
        repo_root = Path(__file__).resolve().parents[2]
        path = config_path or repo_root / "config" / "default.toml"
        raw: dict = tomllib.loads(path.read_text("utf-8")) if path.is_file() else {}
        if (env_root := os.environ.get("CHOREO_REPO_ROOT")):
            raw["repo_root"] = env_root
        raw.setdefault("repo_root", str(repo_root))
        raw["repo_root"] = Path(raw["repo_root"])
        if raw.get("log_file"):
            raw["log_file"] = Path(raw["log_file"])
        return cls(**raw)