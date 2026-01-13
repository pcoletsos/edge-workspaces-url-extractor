# Edge Workspaces URL Extractor

Extract tab URLs from Microsoft Edge Workspace `.edge` files.

The `.edge` workspace files store compressed JSON deltas (gzip). This script
scans for gzip members, decompresses them, parses the JSON, and extracts tab
nodes (`nodeType == 1`) with a `url` field.

## Requirements

- Python 3.8+
- No third-party dependencies

## Usage

Run against a directory containing `.edge` files:

```bash
python edge_workspace_links.py --input "F:\OneDrive - Vodafone Group\Apps\Microsoft Edge\Edge Workspaces"
```

Run against a single workspace file:

```bash
python edge_workspace_links.py --input "F:\OneDrive - Vodafone Group\Apps\Microsoft Edge\Edge Workspaces\Advanced Reporting.edge"
```

Write JSON to stdout:

```bash
python edge_workspace_links.py --input "F:\OneDrive - Vodafone Group\Apps\Microsoft Edge\Edge Workspaces" --format json --output -
```

Exclude internal browser schemes:

```bash
python edge_workspace_links.py --input "F:\OneDrive - Vodafone Group\Apps\Microsoft Edge\Edge Workspaces" --exclude-internal
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
