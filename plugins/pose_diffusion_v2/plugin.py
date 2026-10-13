"""Diffusion pose planner. Wraps an ONNX motion-diffusion checkpoint."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from choreo_contracts.plugin_api import ChoreoPlugin, PluginCapability
from choreo_contracts.schemas import BeatGrid, PoseFrame
from choreo_services.model_loader import ModelLoader
from choreo_utils.logging import get_logger

_log = get_logger(__name__)

_STYLE_IDS = {"hiphop": 0, "house": 1, "waacking": 2, "krump": 3, "vogue": 4}


class Plugin(ChoreoPlugin):
    def __init__(self, checkpoint: Path | None = None) -> None:
        self._loader = ModelLoader(cache_dir=Path.home() / ".ai-choreography-studio" / "models")
        self._session = None
        self._checkpoint = checkpoint

    @property
    def capabilities(self) -> frozenset[PluginCapability]:
        return frozenset({PluginCapability.POSE_PLANNING})

    def _ensure_session(self):
        if self._session is None:
            ckpt = self._checkpoint or Path("models/checkpoints/pose_diffusion_v2.onnx")
            self._session = self._loader.load_onnx(ckpt)
        return self._session

    def detect_beats(self, audio_path: Path, bpm_override: float | None = None):  # pragma: no cover
        raise NotImplementedError("pose_diffusion_v2 does not detect beats")

    def plan_poses(self, grid: BeatGrid, style: str, seed: int) -> list[PoseFrame]:
        session = self._ensure_session()
        rng = np.random.default_rng(seed)
        style_id = _STYLE_IDS.get(style, 0)
        frames: list[PoseFrame] = []
        for i, onset in enumerate(grid.beats):
            nxt = grid.beats[i + 1] if i + 1 < len(grid.beats) else grid.duration_s
            noise = rng.standard_normal((1, 64)).astype(np.float32)
            inputs = {"noise": noise, "style": np.array([[style_id]], dtype=np.int64)}
            joints = session.run(None, inputs)[0]
            frames.append(PoseFrame(
                start_s=float(onset),
                end_s=float(nxt