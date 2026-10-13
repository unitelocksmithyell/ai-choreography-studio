"""Pydantic schemas for the .chg project format and intermediate data."""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class BeatGrid(BaseModel):
    bpm: float = Field(gt=0)
    duration_s: float = Field(gt=0)
    beats: list[float]  # onset times in seconds, ascending


class PoseFrame(BaseModel):
    start_s: float
    end_s: float
    skeleton_name: str
    joints: dict[str, tuple[float, float, float]] = Field(default_factory=dict)


class Move(BaseModel):
    index: int
    start_s: float
    end_s: float
    label: str


class ChoreoProject(BaseModel):
    schema_version: int = 1
    source_audio: str
    style: str
    bpm: float
    duration_s: float
    seed: int
    moves: list[Move]

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.model_dump(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ChoreoProject":
        return cls.model_validate_json(path.read_text(encoding="utf-8"))