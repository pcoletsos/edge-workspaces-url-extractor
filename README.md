# Edge Workspaces URL Extractor

Extract open tab URLs and workspace favorites from Microsoft Edge Workspace `.edge` files.
All processing happens locally.

## Workflow

GitHub is the live source of truth for issues, milestones, CI runs, releases,
and branch protection. Read `CONTRIBUTING.md` before starting non-trivial work.
If markdown snapshots drift from GitHub, GitHub wins.

The `.edge` workspace files store compressed JSON deltas (gzip). This script
scans for gzip members, decompresses them, parses the JSON, and extracts:

- Open tabs (current URL + title per tab)
- Workspace favorites/bookmarks

## Quick start (Windows desktop UI)

Download the latest `edge-workspace-links-ui-windows-vX.Y.Z.zip` asset from GitHub Releases:
https://github.com/pcoletsos/edge-workspaces-url-extractor/releases/latest

1. Extract the zip.
2. Open `edge_workspace_links_ui.exe`.
3. Choose the workspace file or folder you want to analyze.
4. Run the analysis from the desktop UI.

## Quick start (Windows CLI, no Python required)

Download the latest `edge-workspace-links-vX.Y.Z.exe` asset from GitHub Releases:
https://github.com/pcoletsos/edge-workspaces-url-extractor/releases/latest

1. Copy `edge-workspace-links-vX.Y.Z.exe` into the folder with your `.edge` files.
2. Double-click `edge-workspace-links-vX.Y.Z.exe`.
3. The tool writes `edge_workspace_links.xlsx` in the same folder.

> Double-click still works. The packaged executable keeps a console window so warnings and file statuses stay visible.

The CLI executable defaults to the folder it is in. Use `--input` to point to a
different file or folder.

Executable defaults (when double-clicking):

- Input: the folder containing `edge-workspace-links-vX.Y.Z.exe`
- Output: `edge_workspace_links.xlsx` in the input folder
- Mode: `both` (exports open tabs + favorites)
- Filters: none (unless you pass `--exclude-internal` / `--exclude-schemes`)

## Command-line examples (Windows exe)

Run against a directory containing `.edge` files:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces"
```

Run against a single workspace file:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces\Advanced Reporting.edge"
```

Write the Excel output to a custom path:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --output "C:\Temp\edge_workspace_links.xlsx"
```

Write machine-readable JSON instead of Excel:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format json --output "C:\Temp\edge_workspace_links.json"
```

Write CSV tables for automation workflows:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format csv --output "C:\Temp\edge_workspace_links"
```

Exclude internal browser schemes:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --exclude-internal
```

Export only open tabs:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --mode tabs
```

Export only favorites/bookmarks:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --mode favorites
```

Exclude specific schemes:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --exclude-schemes edge chrome file
```

Sort output by workspace file and URL:

```bash
edge-workspace-links-vX.Y.Z.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --sort
```

Default input path:

- Windows executable: the folder containing `edge-workspace-links-vX.Y.Z.exe`.
- Python script: current working directory.

Common options:

- `--output PATH` (`.xlsx` / `.json` file path, or CSV base name)
- `--format xlsx|csv|json` (default: `xlsx`)
- `--exclude-internal`
- `--exclude-schemes edge chrome file`
- `--mode both|tabs|favorites` (default: `both`)
- `--sort`

## Python usage (optional)

Python requirements:

- Python 3.10+
- `openpyxl`

Install the dependency:

```bash
pip install openpyxl
```

For local development and tests:

```bash
pip install -e .[dev]
pytest
```

Use the same examples as above, but replace `edge-workspace-links.exe` with:

```bash
python edge_workspace_links.py
```

## Output

Default output is `edge_workspace_links.xlsx` in the input directory with three sheets:

- `Links`: `workspace_file`, `source`, `url`, `title` (`source` is `tab` or `favorite`)
- `Summary Report`: `metric`, `value` (includes extracted totals, exported totals, and file status counters)
- `Per File Report`: `workspace_file`, `status`, `detail`, `extracted_tab_count`, `extracted_favorite_count`, `exported_link_count`

Alternative formats:

- `--format json` writes one JSON document with `links`, `summary`, and `files` sections.
- `--format csv` writes three sibling files: `_links.csv`, `_summary.csv`, and `_files.csv`.

Workbook safety and reporting behavior:

- Formula-like text in filenames, URLs, and titles is written as literal text so Excel does not evaluate it.
- Hyperlinks stay clickable for normal URLs.
- `--mode tabs` or `--mode favorites` only changes what is exported to `Links`; extracted tab/favorite counts still appear in reports.
- Non-workspace `.edge` files are reported explicitly instead of looking like empty workspaces.
- Decoded payloads that exceed the built-in size guardrail are skipped and reported clearly instead of consuming unbounded memory.

## Notes and limitations

- This exports both open tabs and workspace favorites by default.
- De-duplication rules (per workspace file):
  - If a URL exists as both a tab and a favorite, only the favorite is kept.
  - If a URL exists on multiple tabs, it is written once.
- Workspace share links are not stored as a simple URL in these files.

## Local build paths (development only)

```bash
py -3 -m PyInstaller edge-workspace-links.spec
```

The executable is written to `dist\edge-workspace-links.exe`.
The tracked spec keeps `console=True` so normal double-click runs still surface warnings and file statuses.
Official GitHub releases do not rely on this local step.

Benchmark extraction performance on a local workspace corpus:

```bash
python scripts/benchmark_extraction.py --input test-files --runs 5
```

Use any `.edge` file or directory in place of `test-files`. The benchmark focuses on
the extraction path and skips workbook generation so parser changes remain measurable.

## Quality gates

Use these checks before merging parser, reporting, exporter, CLI, or packaging changes.

Core regression suite:

```bash
python -m pytest tests/test_parity_cases.py -q
python -m pytest tests/test_edge_workspace_links.py tests/test_cli_quality_gates.py tests/test_gui_backend.py tests/test_gui_backend_smoke.py -q
```

Wheel packaging smoke:

```bash
python -m build --wheel
python scripts/check_wheel_install.py --wheel (Get-ChildItem dist\*.whl | Select-Object -First 1).FullName
```

Windows executable smoke:

```bash
py -3 -m PyInstaller edge-workspace-links.spec
python scripts/smoke_packaged_cli.py --exe dist\edge-workspace-links.exe
```

The smoke checks exercise the documented CLI path end to end, including workbook creation,
`--exclude-internal`, sorting, and the legacy wrapper/import surface used by older callers.

Packaged GUI backend smoke:

```bash
python -m PyInstaller --noconfirm edge-workspace-links-gui-backend.spec
python scripts/smoke_gui_backend.py --backend-exe dist\edge-workspace-links-gui-backend.exe
```

Flutter desktop bundles:

```bash
cd gui/flutter_app
flutter analyze
flutter test
flutter build windows
```

Package the Windows desktop UI into a cleaner distributable folder and zip from the repository root:

```bash
python scripts/package_windows_ui_bundle.py
```

That command writes:

- `dist\edge-workspace-links-ui-windows\edge_workspace_links_ui.exe`
- `dist\edge-workspace-links-ui-windows.zip`

For Linux or macOS release-style validation, build the GUI backend on that host first:

```bash
python -m PyInstaller --noconfirm edge-workspace-links-gui-backend.spec
cd gui/flutter_app
flutter build linux   # Linux host
flutter build macos   # macOS host
```

The desktop shell prefers the packaged sibling `edge-workspace-links-gui-backend` binary when it is bundled with the app and falls back to the Python module only during development. GitHub Actions verifies the Windows, Linux, and macOS desktop bundle paths on native hosted runners.

## GitHub-hosted releases

Official releases are built and published by GitHub Actions, not from a local workstation.

Maintainer flow:

1. Merge the release-ready changes into `main`.
2. Open the `Release` workflow in GitHub Actions and run it on `main`.
3. Choose the bump type: `patch`, `minor`, or `major`.
4. Wait for the workflow to rerun the quality gates and publish the assets.

The release workflow:

- reruns the shared CI quality gates on GitHub-hosted runners
- computes the next tag from the latest release tag
- treats legacy tags such as `v0.3` as `0.3.0` for the next increment
- builds the Windows CLI executable and Windows desktop UI bundle on GitHub-hosted Windows runners
- publishes the release assets to GitHub Releases only if those checks succeed

Release assets currently include:

- `edge-workspace-links-vX.Y.Z.exe`
- `edge-workspace-links-ui-windows-vX.Y.Z.zip`
- `edge-workspace-links-vX.Y.Z-sha256.txt`

## Rust evaluation

Milestone M4 evaluates a possible Rust rewrite without changing the shipped Python tool.

Run the parity check for the Rust prototype:

```bash
python scripts/check_rust_parity.py
```

Benchmark the committed parity corpus across Python and Rust:

```bash
python scripts/benchmark_rust_compare.py --release --runs 5 --copies 200
```

On the committed parity corpus, the Rust prototype is measurably faster for parser-only extraction, but the gain is not large enough to justify replacing the shipped Python tool.

The current decision is `no-go` on replacing Python with Rust. The parser prototype,
benchmark command, packaging notes, and decision rationale are recorded in
`docs/rust-evaluation.md`.

## Troubleshooting

- If you get zero results, confirm the input path contains `.edge` files and
  that they are Edge Workspace files (not other Edge data).
- Invalid output paths are reported before workbook generation starts.
- Mixed input folders can succeed partially; check `Per File Report` and stderr for `not_workspace`, `read_error`, `parse_error`, or `no_links` statuses.

## License

See `LICENSE`.
