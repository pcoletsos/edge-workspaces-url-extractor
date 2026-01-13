# Edge Workspaces URL Extractor

Extract tab URLs from Microsoft Edge Workspace `.edge` files.

The `.edge` workspace files store compressed JSON deltas (gzip). This script
scans for gzip members, decompresses them, parses the JSON, and extracts tab
nodes (`nodeType == 1`) with a `url` field.

## Requirements

- Windows executable: none
- Python script: Python 3.8+ with no third-party dependencies

## Usage

Standalone Windows executable (no Python needed):

1. Copy `edge-workspace-links.exe` into the folder with your `.edge` files.
2. Double-click `edge-workspace-links.exe`.
3. The tool writes `edge_workspace_links.csv` in the same folder.

Run against a directory containing `.edge` files (Python):

```bash
python edge_workspace_links.py --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces"
```

Run against a single workspace file:

```bash
python edge_workspace_links.py --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces\Advanced Reporting.edge"
```

Write JSON to stdout:

```bash
python edge_workspace_links.py --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --format json --output -
```

Exclude internal browser schemes:

```bash
python edge_workspace_links.py --input "C:\Users\YourUser\OneDrive\Apps\Microsoft Edge\Edge Workspaces" --exclude-internal
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

## Troubleshooting

- If you get zero results, confirm the input path contains `.edge` files and
  that they are Edge Workspace files (not other Edge data).
