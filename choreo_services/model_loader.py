"""Safe loader for motion-model checkpoints (.pt / .onnx / .safetensors)."""
from __future__ import annotations

from pathlib import Path

import onnxruntime as ort
import torch

from choreo_utils.logging import get_logger

_log = get_logger(__name__)

_SUPPORTED = {".pt", ".onnx", ".safetensors"}


class ModelLoader:
    """Loads inference-ready models. Never pickles untrusted data.

    `weights_only=True` is enforced for torch checkpoints — do not relax it.
    ONNX sessions use CPUExecutionProvider unless CUDA is requested.
    """

    def __init__(self, cache_dir: Path) -> None:
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def load_torch(self, path: Path) -> torch.nn.Module:
        self._assert_supported(path)
        _log.info("torch.load %s (weights_only=True)", path.name)
        obj = torch.load(path, map_location="cpu", weights_only=True)
        if not isinstance(obj, torch.nn.Module):
            raise TypeError(f"{path.name}: expected nn.Module, got {type(obj).__name__}")
        obj.eval()
        return obj

    def load_onnx(self, path: Path, use_cuda: bool = False) -> ort.InferenceSession:
        self._assert_supported(path)
        providers = ["CUDAExecutionProvider"] if use_cuda else ["CPUExecutionProvider"]
        return ort.InferenceSession(str(path), providers=providers)

    @staticmethod
    def _assert_supported(path: Path) -> None:
        if path.suffix.lower() not in _SUPPORTED:
            raise ValueError(f"unsupported model format {path.suffix!r}")