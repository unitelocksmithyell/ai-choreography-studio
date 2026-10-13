"""The plugin contract. Every backend implements ChoreoPlugin."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path

from choreo_contracts.schemas import BeatGrid, PoseFrame


class PluginCapability(StrEnum):
    BEAT_DETECTION = "beat_detection"
    POSE_PLANNING = "pose_planning"
    STYLE_TRANSFER = "style_transfer"
    EXPORT = "export"


class ChoreoPlugin(ABC):
    """Base class for all motion backends.

    Implementations must be stateless across calls or document their state.
    `plan_poses` must be deterministic given (grid, style, seed).
    """

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[PluginCapability]: ...

    @abstractmethod
    def detect_beats(self, audio_path: Path, bpm_override: float | None = None) -> BeatGrid: ...

    @abstractmethod
    def plan_poses(self, grid: BeatGrid, style: str, seed: int) -> list[PoseFrame]: ...

    @abstractmethod
    def retarget(self, frames: list[PoseFrame], style: str) -> list[PoseFrame]: ...