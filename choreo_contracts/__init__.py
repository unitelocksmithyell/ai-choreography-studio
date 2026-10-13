"""Shared contracts: plugin API, schemas, config. Imported by host and plugins."""
from choreo_contracts.plugin_api import ChoreoPlugin, PluginCapability
from choreo_contracts.schemas import BeatGrid, ChoreoProject, Move, PoseFrame

__all__ = ["ChoreoPlugin", "PluginCapability", "BeatGrid", "ChoreoProject", "Move", "PoseFrame"]