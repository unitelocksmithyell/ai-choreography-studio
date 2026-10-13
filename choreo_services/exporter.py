"""Export a .chg project to video / BVH / caption tracks."""
from __future__ import annotations

import subprocess
from pathlib import Path

from choreo_contracts.schemas import ChoreoProject
from choreo_utils.logging import get_logger

_log = get_logger(__name__)


class Exporter:
    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        self._ffmpeg = ffmpeg_path

    def to_bvh(self, project: ChoreoProject, out: Path) -> Path:
        """Write a minimal BVH skeleton from the move timeline (placeholder joints)."""
        lines = ["HIERARCHY", "ROOT Hips", "{", "  OFFSET 0 0 0", "  CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation"]
        lines += ["  End Site", "  {", "    OFFSET 0 10 0", "  }", "}", "MOTION",
                  f"Frames: {len(project.moves)}", "Frame Time: 0.0333333"]
        for _ in project.moves:
            lines.append("0 0 0 0 0 0")
        out.write_text("\n".join(lines), encoding="utf-8")
        return out

    def to_video(self, project: ChoreoProject, out: Path) -> Path:
        """Invoke ffmpeg with an allowlisted arg list — no shell, no user format strings."""
        cmd = [
            self._ffmpeg, "-y",
            "-i", project.source_audio,
            "-filter_complex", "color=c=black:s=1280x720:d=%.3f" % project.duration_s,
            "-shortest", str(out),
        ]
        _log.info("ffmpeg export -> %s", out.name)
        subprocess.run(cmd, check=True, capture_output=True)
        return out