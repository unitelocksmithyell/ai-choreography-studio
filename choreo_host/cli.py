"""`choreo` CLI — entrypoint for Windows desktop and headless use."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from choreo_host.bootstrap import bootstrap
from choreo_host.pipeline import ChoreoPipeline

app = typer.Typer(add_completion=False, help="AI dance / choreography generator (plugin host).")
console = Console()


@app.command()
def generate(
    track: Annotated[Path, typer.Argument(help="Input audio file (.wav/.mp3/.flac).")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Output .chg project path.")],
    style: Annotated[str, typer.Option("--style", "-s")] = "hiphop",
    bpm: Annotated[float | None, typer.Option("--bpm")] = None,
    seed: Annotated[int, typer.Option("--seed")] = 6767,
) -> None:
    """Generate a choreography project from an audio track."""
    config, registry = bootstrap()
    pipeline = ChoreoPipeline(config=config, registry=registry)
    project = pipeline.run(audio_path=track, style=style, bpm_override=bpm, seed=seed)
    project.save(out)
    console.print(f"[green]wrote[/] {out}  ({len(project.moves)} moves, {project.duration_s:.1f}s)")


@app.command("list-plugins")
def list_plugins() -> None:
    """List every plugin the host loaded."""
    _, registry = bootstrap()
    for name in registry.names():
        spec = registry.get(name)
        console.print(f"{name:<24} v{spec.version:<8} api={spec.api_version}  {spec.description}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()