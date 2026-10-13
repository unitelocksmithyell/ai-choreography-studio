# Contributing to ai-choreography-studio

Thanks for wanting to help train, tune, and ship the tater's dance brain.
This repo is a **plugin host** for AI choreography: a core host process,
extension modules, a loader, a registry, and shared contracts.

## Ground rules

- Python 3.12+ for host + plugins. C++/C#/Java bindings are allowed only
  through the documented FFI bridge (`choreo_host/ffi/`).
- One plugin = one folder under `plugins/`. No cross-plugin imports.
- Every plugin must implement `ChoreoPlugin` from `choreo_contracts.plugin_api`.
- New beat-detection, pose-estimation, or style-transfer backends go in
  `plugins/` — never inside `choreo_host/`.

## Dev setup

```bash
python -m venv .venv
. .venv/Scripts/activate      # Windows
pip install -e ".[dev]"
pre-commit install
pytest -q
```

## Plugin checklist

1. Folder: `plugins/<your_plugin_name>/`
2. Files: `__init__.py`, `plugin.py`, `manifest.toml`
3. Manifest fields: `name`, `version`, `api_version`, `entrypoint`,
   `capabilities`, `requires`.
4. Register via `PluginRegistry.register()` — do not touch the loader.
5. Add a test under `tests/plugins/`.

## Style

- `ruff` + `black`, line length 100.
- Type hints everywhere; `mypy --strict` on `choreo_host/` and `choreo_contracts/`.
- No prints in library code — use `choreo_utils.logging.get_logger`.

## Commit messages

`<area>: <imperative summary>` — e.g. `beat: add onset-energy fallback`.

## Code of conduct

Be a decent tater. Roast code, not people.