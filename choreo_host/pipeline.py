"""Generation pipeline: audio -> beats -> pose plan -> moves -> .chg project."""
from __future__ import annotations

from pathlib import Path

from choreo_contracts.config import HostConfig
from choreo_contracts.plugin_api import PluginCapability
from choreo_contracts.schemas import BeatGrid, ChoreoProject, Move, PoseFrame
from choreo_host.registry import PluginRegistry
from choreo_utils.logging import get_logger

_log = get_logger(__name__)


class ChoreoPipeline:
    def __init__(self, config: HostConfig, registry: PluginRegistry) -> None:
        self._config = config
        self._registry = registry

    def run(
        self,
        audio_path: Path,
        style: str,
        bpm_override: float | None,
        seed: int,
    ) -> ChoreoProject:
        beat_plugin = self._first(PluginCapability.BEAT_DETECTION)
        pose_plugin = self._first(PluginCapability.POSE_PLANNING)
        style_plugin = self._first(PluginCapability.STYLE_TRANSFER)

        grid: BeatGrid = beat_plugin.detect_beats(audio_path, bpm_override=bpm_override)
        _log.info("beat grid: %d beats, %.1f bpm", len(grid.beats), grid.bpm)

        frames: list[PoseFrame] = pose_plugin.plan_poses(grid, style=style, seed=seed)
        frames = style_plugin.retarget(frames, style=style)

        moves = [Move(index=i, start_s=f.start_s, end_s=f.end_s, label=f.skeleton_name)
                 for i, f in enumerate(frames)]
        return ChoreoProject(
            source_audio=str(audio_path),
            style=style,
            bpm=grid.bpm,
            duration_s=grid.duration_s,
            seed=seed,
            moves=moves,
        )

    def _first(self, cap: PluginCapability):
        matches = self._registry.by_capability(cap)
        if not matches:
            raise RuntimeError(f"no plugin provides capability {cap.value}")
        return matches[0]