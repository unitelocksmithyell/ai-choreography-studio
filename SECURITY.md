# Security Policy — ai-choreography-studio

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Email `security@ai-choreography-studio.dev` with:
- affected version + plugin name,
- minimal repro (a `.chg` project file is ideal),
- impact (RCE, sandbox escape, model poisoning, path traversal).

We acknowledge within 72h, patch within 30 days for high severity.

## Threat model

The host loads **third-party plugins** and **third-party motion models**.
That is the attack surface. Specifically:

- **Plugin loader** — plugins run in-process by default. Use
  `--sandbox=subprocess` to isolate. Sandbox mode is opt-in; treat any
  plugin from an untrusted source as arbitrary code.
- **Model files** — `.pt` / `.onnx` / `.safetensors` are code-adjacent.
  `torch.load` with `weights_only=True` is enforced in
  `choreo_services/model_loader.py`. Do not disable it.
- **Project files (`.chg`)** — parsed with a strict schema. No `eval`,
  no pickle, no remote includes.
- **Export pipeline** — FFmpeg is invoked with an allowlisted argument
  list; user-supplied paths are validated against the project root.

## Hardening checklist for distributors

- Ship with `--sandbox=subprocess` in the default launcher.
- Pin plugin hashes in `config/plugin_allowlist.toml`.
- Disable `remote_registry` in `config/default.toml` for air-gapped installs.

## Out of scope

- Malicious plugins you installed yourself.
- GPU driver CVEs.
- The fact that your dance still looks like a dad at a wedding.