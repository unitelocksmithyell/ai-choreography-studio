"""Filesystem plugin loader: scans roots, validates manifests, registers plugins."""
from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path
from types import ModuleType

from choreo_contracts.plugin_api import ChoreoPlugin
from choreo_host.registry import PluginRegistry
from choreo_utils.logging import get_logger

_log = get_logger(__name__)

_MANIFEST_NAME = "manifest.toml"


class PluginLoadError(RuntimeError):
    """Raised when a plugin folder cannot be turned into a live plugin."""


class PluginLoader:
    def __init__(self, registry: PluginRegistry, api_version: str) -> None:
        self._registry = registry
        self._api_version = api_version

    def load_tree(self, root: Path) -> int:
        loaded = 0
        for manifest in sorted(root.glob(f"*/{_MANIFEST_NAME}")):
            try:
                self._load_one(manifest.parent)
                loaded += 1
            except PluginLoadError as exc:
                _log.error("skipping %s: %s", manifest.parent.name, exc)
        return loaded

    def _load_one(self, plugin_dir: Path) -> None:
        manifest = tomllib.loads((plugin_dir / _MANIFEST_NAME).read_text("utf-8"))
        api_version = manifest.get("api_version", "")
        if api_version != self._api_version:
            raise PluginLoadError(f"api_version {api_version!r} != host {self._api_version!r}")

        entrypoint = manifest.get("entrypoint", "plugin:Plugin")
        module_name, _, attr = entrypoint.partition(":")
        module = self._import_module(plugin_dir, module_name)
        try:
            plugin_cls = getattr(module, attr)
        except AttributeError as exc:
            raise PluginLoadError(f"entrypoint {entrypoint!r} not found") from exc

        if not issubclass(plugin_cls, ChoreoPlugin):
            raise PluginLoadError(f"{attr} does not implement ChoreoPlugin")
        instance = plugin_cls()
        self._registry.register(instance, manifest=manifest)

    @staticmethod
    def _import_module(plugin_dir: Path, module_name: str) -> ModuleType:
        py_file = plugin_dir / f"{module_name}.py"
        if not py_file.is_file():
            raise PluginLoadError(f"missing module file {py_file.name}")
        spec = importlib.util.spec_from_file_location(
            f"choreo_plugins.{plugin_dir.name}.{module_name}", py_file
        )
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"could not build import spec for {py_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module