"""Reference beat detector. Onset-strength envelope + peak picking."""
from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from choreo_contracts.plugin_api import ChoreoPlugin, PluginCapability
from choreo_contracts.schemas import BeatGrid
from choreo_services.audio_io import load_audio_mono
from choreo_utils.logging import get_logger

_log = get_logger(__name__)


class Plugin(ChoreoPlugin):
    @property
    def capabilities(self) -> frozenset[PluginCapability]:
        return frozenset({PluginCapability.BEAT_DETECTION})

    def detect_beats(self, audio_path: Path, bpm_override: float | None = None) -> BeatGrid:
        y, sr = load_audio_mono(audio_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env, sr=sr, bpm=bpm_override, units="frames"
        )
        bpm = float(bpm_override) if bpm_override else float(np.atleast_1d(tempo)[0])
        beats = librosa.frames_to_time(beat_frames, sr=sr).tolist()
        return BeatGrid(bpm=bpm, duration_s=float(librosa.get_duration(y=y, sr=sr)), beats=beats)

    def plan_poses(self, grid: BeatGrid, style: str, seed: int):  # pragma: no cover
        raise NotImplementedError("beat_onset_energy does not plan poses")

    def retarget(self, frames, style: str):  # pragma: no cover
        raise NotImplementedError("beat_onset_energy does not retarget")