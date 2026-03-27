# Repo Overview

## Mission

`edge-workspaces-url-extractor` extracts open tab URLs and workspace favorites from Microsoft Edge Workspace `.edge` files.
Processing is local-only. The main user-facing outputs are Excel, JSON, and CSV exports.

## Current Product Shape

- Shipped implementation: Python
- Main entry points: CLI script, packaged Windows executable, and a Flutter desktop prototype for cross-platform UI work
- Core value: reliable extraction, explicit reporting, and safe export behavior for mixed or malformed workspace inputs

## Important Directories

- `src/edge_workspace_links_app/`: main Python package for parsing, reporting, exporting, and CLI behavior
- `edge_workspace_links.py`: legacy wrapper/import surface kept for compatibility
- `tests/`: regression tests for parser, CLI, reporting, exporter, and packaging behavior
- `parity/`: synthetic corpus and helpers used to pin parser semantics
- `scripts/`: local validation, smoke tests, and benchmarking helpers
- `rust/edge-workspace-links-rs/`: Rust prototype kept for parity and performance evaluation
- `gui/flutter_app/`: Flutter desktop prototype that calls the Python backend contract
- `docs/`: design notes and evaluation documents

## Known Stable Decisions

- Python remains the shipped implementation.
- Rust is retained as an evaluation prototype and research baseline, not the replacement implementation.
- Flutter desktop builds use a packaged sibling GUI backend executable for release-style runs, with Python source-module fallback kept for local development only.
- Work must be tracked through issues, milestones, branches, and pull requests.

See `docs/agent-memory/decision-log.md` for the durable memo trail.

## Quality Gates

Use the smallest relevant set for the area you touched.

Core regression suite:

```bash
python -m pytest tests/test_parity_cases.py -q
python -m pytest tests/test_edge_workspace_links.py tests/test_cli_quality_gates.py tests/test_gui_backend.py tests/test_gui_backend_smoke.py -q
```

Packaging smoke:

```bash
python -m build --wheel
python scripts/check_wheel_install.py --wheel <wheel-path>
python -m PyInstaller --noconfirm edge-workspace-links.spec
python scripts/smoke_packaged_cli.py --exe dist\edge-workspace-links.exe
python -m PyInstaller --noconfirm edge-workspace-links-gui-backend.spec
python scripts/smoke_gui_backend.py --backend-exe dist\edge-workspace-links-gui-backend.exe
```

Flutter desktop shell:

```bash
cd gui/flutter_app
flutter analyze
flutter test
flutter build windows
```

Release-style Linux and macOS desktop validation must build the same GUI backend artifact on the matching host before running `flutter build linux` or `flutter build macos`.
GitHub Actions now verifies the packaged GUI backend and desktop bundle path on native Windows, Linux, and macOS hosted runners.

Rust parity:

```bash
python scripts/check_rust_parity.py
```

CI definitions live in `.github/workflows/ci.yml`.

## How Agents Should Resume Work

1. Read `AGENTS.md`.
2. Read the latest entries in `docs/agent-memory/work-log.md`.
3. Inspect `git status --short` and the current branch name.
4. Confirm the issue and milestone before adding new implementation work.
5. Update the work log as soon as the task scope is clear and again when the branch is ready for PR.
