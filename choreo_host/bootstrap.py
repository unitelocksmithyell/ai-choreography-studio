"""Bootstrap sequence: config -> logging -> plugin discovery -> registry."""
from __future__ import annotations

import sys
from pathlib import Path

from choreo_contracts.config import HostConfig
from choreo_host.plugin_loader import PluginLoader
from choreo_host.registry import PluginRegistry
from choreo_utils.logging import configure_logging, get_logger

_log = get_logger(__name__)


def discover_plugin_roots(repo_root: Path) -> list[Path]:
    """Return plugin search roots in precedence order (later wins on name clash)."""
    roots = [
        repo_root / "plugins",
        Path.home() / ".ai-choreography-studio" / "plugins",
    ]
    return [r for r in roots if r.is_dir()]


def bootstrap(config_path: Path | None = None) -> tuple[HostConfig, PluginRegistry]:
    config = HostConfig.load(config_path)
    configure_logging(level=config.log_level, log_file=config.log_file)

    registry = PluginRegistry()
    loader = PluginLoader(registry, api_version=config.plugin_api_version)

    roots = discover_plugin_roots(config.repo_root)
    if not roots:
        _log.warning("no plugin roots found under %s", config.repo_root)
    for root in roots:
        loaded = loader.load_tree(root)
        _log.info("loaded %d plugin(s) from %s", loaded, root)

    if not registry.names():
        _log.error("registry empty — host has no motion backends; aborting")
        sys.exit(2)
    return config, registry