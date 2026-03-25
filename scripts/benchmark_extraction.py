#!/usr/bin/env python3
from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path

import edge_workspace_links as app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark Edge workspace extraction without workbook generation."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a .edge file or directory containing .edge files.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of benchmark runs to execute (default: 3).",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "tabs", "favorites"],
        default="both",
        help="Export mode to simulate during extraction (default: both).",
    )
    parser.add_argument(
        "--exclude-schemes",
        nargs="*",
        default=[],
        help="URL schemes to exclude from the simulated export set.",
    )
    parser.add_argument(
        "--exclude-internal",
        action="store_true",
        help="Exclude internal browser URLs during the benchmark.",
    )
    return parser.parse_args()


def benchmark_once(
    input_path: Path,
    mode: str,
    exclude_schemes: set[str],
) -> tuple[float, int, int, int]:
    edge_files = app.iter_edge_files(input_path)
    start = time.perf_counter()
    processed = 0
    exported_links = 0
    extracted_links = 0

    for path in edge_files:
        file_result, _ = app.process_edge_file(
            path=path,
            mode=mode,
            exclude_schemes=exclude_schemes,
        )
        if file_result.status in app.SUCCESS_STATUSES:
            processed += 1
        exported_links += file_result.exported_link_count
        extracted_links += (
            file_result.extracted_tab_count + file_result.extracted_favorite_count
        )

    elapsed = time.perf_counter() - start
    return elapsed, len(edge_files), processed, exported_links or extracted_links


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser()
    exclude_schemes = {scheme.lower() for scheme in args.exclude_schemes}
    if args.exclude_internal:
        exclude_schemes.update(app.INTERNAL_SCHEMES)

    timings: list[float] = []
    total_files = 0
    processed_files = 0
    extracted_or_exported_links = 0

    for _ in range(args.runs):
        elapsed, total_files, processed_files, extracted_or_exported_links = benchmark_once(
            input_path=input_path,
            mode=args.mode,
            exclude_schemes=exclude_schemes,
        )
        timings.append(elapsed)

    print(f"Input files: {total_files}")
    print(f"Workspace files processed: {processed_files}")
    print(f"Links observed during run: {extracted_or_exported_links}")
    print(f"Runs: {args.runs}")
    print(f"Best: {min(timings):.3f}s")
    print(f"Mean: {statistics.mean(timings):.3f}s")
    print(f"Worst: {max(timings):.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
