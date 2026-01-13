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

> No terminal needed. Just double-click.

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

- `--output PATH` (output `.xlsx` file path)
- `--exclude-internal`
- `--exclude-schemes edge chrome file`
- `--mode both|tabs|favorites` (default: `both`)
- `--sort`

## Python usage (optional)

Python requirements:

- Python 3.8+
- `openpyxl`

Install the dependency:

```bash
pip install openpyxl
```

Use the same examples as above, but replace `edge-workspace-links.exe` with:

```bash
python edge_workspace_links.py
```

## Output

Default output is `edge_workspace_links.xlsx` in the input directory with three sheets:

- `Links`: `workspace_file`, `source`, `url`, `title` (`source` is `tab` or `favorite`)
- `Summary Report`: `metric`, `value` (includes totals for tabs, favorites, and overall unique URLs)
- `Per File Report`: `workspace_file`, `open_tab_count`, `favorite_count`, `links_written`

## Notes and limitations

- This exports both open tabs and workspace favorites by default.
- De-duplication rules (per workspace file):
  - If a URL exists as both a tab and a favorite, only the favorite is kept.
  - If a URL exists on multiple tabs, it is written once.
- Workspace share links are not stored as a simple URL in these files.

## Build an executable (developers)

```bash
py -3 -m PyInstaller --onefile --name edge-workspace-links edge_workspace_links.py
```

The executable is written to `dist\edge-workspace-links.exe`.

## Troubleshooting

- If you get zero results, confirm the input path contains `.edge` files and
  that they are Edge Workspace files (not other Edge data).

## License

See `LICENSE`.
