"""Audio ingest: decode to mono float32 at a fixed sample rate."""
from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from choreo_utils.logging import get_logger

_log = get_logger(__name__)

TARGET_SR = 22_050


def load_audio_mono(path: Path, sr: int = TARGET_SR) -> tuple[np.ndarray, int]:
    """Return (samples_float32_mono, sample_rate).

    Uses librosa's soundfile backend first; falls back to audioread for
    codecs soundfile can't open (some mp3 variants on Windows).
    """
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        y, sr_out = librosa.load(path, sr=sr, mono=True)
    except Exception as exc:  # noqa: BLE001 — backend variety is the point
        _log.warning("soundfile failed on %s (%s); retrying via audioread", path.name, exc)
        y, sr_out = librosa.load(path, sr=sr, mono=True, res_type="kaiser_fast")
    return y.astype(np.float32, copy=False), int(sr_out)