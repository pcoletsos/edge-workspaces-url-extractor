# Edge Workspaces URL Extractor

Extract open tab URLs and workspace favorites from Microsoft Edge Workspace `.edge` files.
All processing happens locally.

The `.edge` workspace files store compressed JSON deltas (gzip). This script
scans for gzip members, decompresses them, parses the JSON, and extracts:

- Open tabs (current URL + title per tab)
- Workspace favorites/bookmarks

## Quick start (Windows, no Python required)

Download the latest `edge-workspace-links.exe` from GitHub Releases:
https://github.com/TsoliasPN/edge-workspaces-url-extractor/releases/latest

1. Copy `edge-workspace-links.exe` into the folder with your `.edge` files.
2. Double-click `edge-workspace-links.exe`.
3. The tool writes `edge_workspace_links.xlsx` in the same folder.

> Double-click still works. The packaged executable keeps a console window so warnings and file statuses stay visible.

The executable defaults to the folder it is in. Use `--input` to point to a
different file or folder.

Executable defaults (when double-clicking):

- Input: the folder containing `edge-workspace-links.exe`
- Output: `edge_workspace_links.xlsx` in the input folder
- Mode: `both` (exports open tabs + favorites)
- Filters: none (unless you pass `--exclude-internal` / `--exclude-schemes`)

## Command-line examples (Windows exe)

Run against a directory containing `.edge` files:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces"
```

Run against a single workspace file:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces\Advanced Reporting.edge"
```

Write the Excel output to a custom path:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --output "C:\Temp\edge_workspace_links.xlsx"
```

Write machine-readable JSON instead of Excel:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format json --output "C:\Temp\edge_workspace_links.json"
```

Write CSV tables for automation workflows:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format csv --output "C:\Temp\edge_workspace_links"
```

Exclude internal browser schemes:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --exclude-internal
```

Export only open tabs:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --mode tabs
```

Export only favorites/bookmarks:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --mode favorites
```

Exclude specific schemes:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --exclude-schemes edge chrome file
```

Sort output by workspace file and URL:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --sort
```

Default input path:

- Windows executable: the folder containing `edge-workspace-links.exe`.
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

## Build an executable (developers)

```bash
py -3 -m PyInstaller edge-workspace-links.spec
```

The executable is written to `dist\edge-workspace-links.exe`.
The tracked spec keeps `console=True` so normal double-click runs still surface warnings and file statuses.

Benchmark extraction performance on a local workspace corpus:

```bash
python scripts/benchmark_extraction.py --input test-files --runs 5
```

Use any `.edge` file or directory in place of `test-files`. The benchmark focuses on
the extraction path and skips workbook generation so parser changes remain measurable.

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
