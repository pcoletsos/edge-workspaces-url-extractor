# Edge Workspaces URL Extractor

Extract tab URLs from Microsoft Edge Workspace `.edge` files.
All processing happens locally.

The `.edge` workspace files store compressed JSON deltas (gzip). This script
scans for gzip members, decompresses them, parses the JSON, and extracts tab
nodes (`nodeType == 1`) with a `url` field.

## Quick start (Windows, no Python required)

Download the latest `edge-workspace-links.exe` from GitHub Releases:
https://github.com/TsoliasPN/edge-workspaces-url-extractor/releases/latest

1. Copy `edge-workspace-links.exe` into the folder with your `.edge` files.
2. Double-click `edge-workspace-links.exe`.
3. The tool writes `edge_workspace_links.csv` in the same folder.

> No terminal needed. Just double-click.

The executable defaults to the folder it is in. Use `--input` to point to a
different file or folder.

## Command-line examples (Windows exe)

Run against a directory containing `.edge` files:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces"
```

Run against a single workspace file:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces\Advanced Reporting.edge"
```

Write JSON to stdout:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format json --output -
```

Write TSV to a custom output file:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format tsv --output "C:\Temp\edge_workspace_links.tsv"
```

Exclude internal browser schemes:

```bash
edge-workspace-links.exe --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --exclude-internal
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

- `--format csv|json|tsv`
- `--output PATH` (use `-` for stdout)
- `--exclude-internal`
- `--exclude-schemes edge chrome file`
- `--sort`

## Python usage (optional)

Python requirements:

- Python 3.8+
- No third-party dependencies

Use the same examples as above, but replace `edge-workspace-links.exe` with:

```bash
python edge_workspace_links.py
```

## Output

Default output is `edge_workspace_links.csv` in the input directory with:

- `workspace_file`
- `url`
- `title`

Use `--format json` or `--format tsv` to change the output format.

## Notes and limitations

- This extracts tab URLs (nodeType 1) and titles only.
- Workspace share links are not stored as a simple URL in these files.
- Entries are de-duplicated per workspace by `(url, title)`.

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
