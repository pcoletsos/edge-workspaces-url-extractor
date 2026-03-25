#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import edge_workspace_links as py_impl
from parity.fixture_builder import build_edge_bytes, load_cases
from scripts.check_rust_parity import DEFAULT_MANIFEST, ensure_binary


def write_corpus(target_dir: Path, copies: int) -> list[Path]:
    cases = load_cases()
    paths: list[Path] = []
    for repeat_index in range(copies):
        for case in cases:
            path = target_dir / f"{case['name']}-{repeat_index:03d}.edge"
            path.write_bytes(build_edge_bytes(case))
            paths.append(path)
    return paths


def python_once(paths: list[Path]) -> dict[str, object]:
    start = time.perf_counter()
    status_counts: dict[str, int] = {}
    extracted_tabs = 0
    extracted_favorites = 0
    exported_links = 0
    for path in paths:
        file_result, export_rows = py_impl.process_edge_file(path, "both", set())
        status_counts[file_result.status] = status_counts.get(file_result.status, 0) + 1
        extracted_tabs += file_result.extracted_tab_count
        extracted_favorites += file_result.extracted_favorite_count
        exported_links += len(export_rows)
    return {
        "seconds": time.perf_counter() - start,
        "files": len(paths),
        "status_counts": status_counts,
        "extracted_tabs": extracted_tabs,
        "extracted_favorites": extracted_favorites,
        "exported_links": exported_links,
    }


def rust_once(binary: Path, input_dir: Path) -> dict[str, object]:
    start = time.perf_counter()
    completed = subprocess.run(
        [str(binary), "--input", str(input_dir)],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    status_counts: dict[str, int] = {}
    extracted_tabs = 0
    extracted_favorites = 0
    exported_links = 0
    for file_result in payload["files"]:
        status = file_result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        extracted_tabs += len(file_result["tabs"])
        extracted_favorites += len(file_result["favorites"])
        exported_links += len(file_result["exports"]["both"])
    return {
        "seconds": time.perf_counter() - start,
        "files": len(payload["files"]),
        "status_counts": status_counts,
        "extracted_tabs": extracted_tabs,
        "extracted_favorites": extracted_favorites,
        "exported_links": exported_links,
    }


def summarize(samples: list[dict[str, object]]) -> dict[str, object]:
    timings = [sample["seconds"] for sample in samples]
    baseline = samples[-1].copy()
    baseline["best_seconds"] = round(min(timings), 4)
    baseline["mean_seconds"] = round(statistics.mean(timings), 4)
    baseline["median_seconds"] = round(statistics.median(timings), 4)
    baseline["seconds"] = round(baseline["seconds"], 4)
    return baseline


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark the committed parity corpus against the Python and Rust implementations."
    )
    parser.add_argument(
        "--manifest-path",
        default=str(DEFAULT_MANIFEST),
        help="Path to the Rust Cargo.toml manifest.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Use a release build of the Rust prototype.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of benchmark runs to execute per implementation.",
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=200,
        help="Copies of each committed parity case to generate.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    manifest_path = Path(args.manifest_path).resolve()
    binary = ensure_binary(manifest_path, args.release)

    with tempfile.TemporaryDirectory() as temp_dir:
        corpus_dir = Path(temp_dir)
        paths = write_corpus(corpus_dir, args.copies)

        python_samples = [python_once(paths) for _ in range(args.runs)]
        rust_samples = [rust_once(binary, corpus_dir) for _ in range(args.runs)]

    summary = {
        "scenario": "parity_corpus",
        "runs": args.runs,
        "copies_per_case": args.copies,
        "build_profile": "release" if args.release else "debug",
        "python": summarize(python_samples),
        "rust": summarize(rust_samples),
        "rust_binary": os.fspath(binary),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
