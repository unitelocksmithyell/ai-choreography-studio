"""In-memory plugin registry. Name-unique, capability-indexed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from choreo_contracts.plugin_api import ChoreoPlugin, PluginCapability


@dataclass(slots=True)
class PluginSpec:
    name: str
    version: str
    api_version: str
    description: str
    capabilities: frozenset[PluginCapability]
    manifest: dict[str, Any] = field(default_factory=dict)


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, ChoreoPlugin] = {}
        self._specs: dict[str, PluginSpec] = {}

    def register(self, plugin: ChoreoPlugin, manifest: dict[str, Any]) -> None:
        name = manifest.get("name") or type(plugin).__name__
        if name in self._plugins:
            raise ValueError(f"duplicate plugin name {name!r}")
        self._plugins[name] = plugin
        self._specs[name] = PluginSpec(
            name=name,
            version=str(manifest.get("version", "0.0.0")),
            api_version=str(manifest.get("api_version", "")),
            description=str(manifest.get("description", "")),
            capabilities=frozenset(plugin.capabilities),
            manifest=manifest,
        )

    def get(self, name: str) -> ChoreoPlugin:
        return self._plugins[name]

    def spec(self, name: str) -> PluginSpec:
        return self._specs[name]

    def by_capability(self, cap: PluginCapability) -> list[ChoreoPlugin]:
        return [p for n, p in self._plugins.items() if cap in self._specs[n].capabilities]

    def names(self) -> list[str]:
        return sorted(self._plugins)