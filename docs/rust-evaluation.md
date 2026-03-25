# Rust Rewrite Evaluation

## Prototype scope

The Rust prototype in `rust/edge-workspace-links-rs/` is intentionally narrow:

- read `.edge` files from a file or directory input
- scan for gzip members and apply the same 64 MiB payload guardrail used in Python
- parse nested JSON content and extract tabs and favorites
- emit JSON with raw tabs/favorites plus export variants for `both`, `tabs`, `favorites`, and `exclude_internal`

That scope is enough to evaluate parser correctness and runtime without first rebuilding workbook generation or release packaging.

Run the prototype parity check locally with:

```bash
python scripts/check_rust_parity.py
```

## Parity strategy

Behavior is pinned by the committed synthetic corpus in `parity/cases.json`.

- `parity/fixture_builder.py` generates safe `.edge` fixtures from that corpus
- `tests/test_parity_cases.py` proves the current Python implementation matches the expected outputs
- `scripts/check_rust_parity.py` builds the Rust prototype and compares both Python and Rust results against the same expected tabs, favorites, and export rows, plus a mixed-directory `read_error` scenario

This makes semantic drift explicit without requiring manual workbook inspection.

The committed cases currently cover:

- duplicate URL handling across tabs and favorites
- internal-scheme filtering in exports
- nested JSON payload discovery
- out-of-range navigation indices that should fall back to the latest navigation entry
- valid workspaces that contain no extractable links
- decoded payloads that are valid JSON but not Edge Workspace content
- gzip members that fail to decompress and should surface as `parse_error`

## Rust stack choice

The evaluated Rust stack is:

- CLI parsing: `clap`
- gzip decompression: `flate2`
- JSON traversal and output: `serde` + `serde_json`
- proposed XLSX library for a fuller migration: `rust_xlsxwriter`

Packaging direction if the prototype were continued:

- build a native Windows executable with `cargo build --release`
- keep console output enabled so warnings and file statuses remain visible, matching the current Python/exe behavior after M1
- add workbook generation only after parity is stable; `rust_xlsxwriter` is the most plausible path for preserving hyperlink behavior and workbook formatting
- if the project ever pursued a hybrid boundary, the parser would be the first candidate because it is already isolated by parity fixtures and JSON output

Current prototype limitation:

- the Rust JSON output now preserves per-file `read_error` continuation for directory runs, but it still does not implement workbook generation, summary sheets, or the full CLI/output surface of the Python tool

## Measured tradeoff

Repeatable benchmark command:

```bash
python scripts/benchmark_rust_compare.py --release --runs 5 --copies 200
```

Measured on March 26, 2026 in this repository workspace:

- corpus: 1,000 generated `.edge` files (200 copies of each of the 5 committed parity cases)
- Python runtime: 0.3097s mean, 0.1806s median, 0.1717s best
- Rust runtime: 0.1617s mean, 0.1524s median, 0.1471s best
- observed speedup: about 1.2x by median runtime and about 1.9x by mean runtime across 5 runs

The Rust prototype can still provide additional parser speed, but a full migration would also need:

- workbook generation parity
- report/status parity
- release pipeline replacement for the current PyInstaller flow
- ongoing maintenance for two implementations during migration

The benchmark above is intentionally parser-focused. It does not include workbook generation, PyInstaller packaging, or Windows installer concerns, which are exactly the parts that still dominate rewrite risk.
It also does not show an order-of-magnitude win, which is why the migration cost remains hard to justify after M2.

## Decision

Decision: no-go on replacing the Python application with Rust at this time.

Rationale:

- The Python implementation is now fast enough for the current corpus after the M2 optimization work.
- The Rust prototype is faster on parser-only extraction, but the measured gain is incremental rather than transformative once workbook generation, packaging, and release maintenance are included.
- The highest-value Rust outcome today is the parity-checked prototype itself, not a wholesale rewrite of the shipped tool.

Follow-up path:

- keep the Python application as the shipped implementation
- retain the Rust prototype and parity corpus as a research baseline
- revisit Rust only if a future parser bottleneck appears on real-world corpora or packaging requirements change enough to justify the migration cost
