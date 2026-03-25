#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import statistics
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import edge_workspace_links as app


def wrap_value(value: str | int) -> dict[str, str | int]:
    return {"value": value}


def make_tab(url: str, title: str, current_index: int) -> dict[str, object]:
    return {
        "storage": {"currentNavigationIndex": wrap_value(current_index)},
        "subdirectories": {
            "navigationStack": {
                "subdirectories": {
                    str(current_index): {
                        "storage": {
                            "virtualUrl": wrap_value(url),
                            "title": wrap_value(title),
                        }
                    }
                }
            }
        },
    }


def make_favorite(url: str, title: str) -> dict[str, object]:
    return {"value": {"nodeType": "1", "url": url, "title": title}}


def make_workspace_payload(
    *,
    file_index: int,
    payload_index: int,
    tab_count: int,
    favorite_count: int,
    nested_json_layers: int,
) -> dict[str, object]:
    webcontents: dict[str, object] = {}
    for tab_index in range(tab_count):
        url = f"https://tabs.example/{file_index}/{payload_index}/{tab_index}"
        title = f"Tab {file_index}-{payload_index}-{tab_index}"
        webcontents[f"tab-{tab_index}"] = make_tab(url, title, tab_index)

    favorite_storage: dict[str, object] = {}
    for favorite_index in range(favorite_count):
        url = f"https://favorites.example/{file_index}/{payload_index}/{favorite_index}"
        title = f"Favorite {file_index}-{payload_index}-{favorite_index}"
        favorite_storage[f"favorite-{favorite_index}"] = make_favorite(url, title)

    payload: dict[str, object] = {
        "content": {
            "subdirectories": {
                "tabstripmodel": {
                    "subdirectories": {
                        "webcontents": {
                            "subdirectories": webcontents,
                        }
                    }
                },
                "favorites": {
                    "storage": favorite_storage,
                },
            }
        }
    }

    wrapped: dict[str, object] = payload
    for _ in range(nested_json_layers):
        wrapped = {
            "envelope": [
                {"metadata": f"file-{file_index}-payload-{payload_index}"},
                {"embedded": json.dumps(wrapped)},
            ]
        }
    return wrapped


def make_edge_bytes(payloads: list[dict[str, object]], corrupt_members: int) -> bytes:
    data = bytearray(b"header")
    for payload in payloads:
        data.extend(gzip.compress(json.dumps(payload).encode("utf-8")))
    for member_index in range(corrupt_members):
        data.extend(f"corrupt-{member_index}".encode("utf-8"))
        data.extend(app.GZIP_MAGIC + b"broken-member")
    data.extend(b"tail")
    return bytes(data)


def write_synthetic_corpus(
    root: Path,
    *,
    files: int,
    payloads_per_file: int,
    tab_count: int,
    favorite_count: int,
    nested_json_layers: int,
    corrupt_members: int,
) -> list[Path]:
    paths: list[Path] = []
    for file_index in range(files):
        payloads = [
            make_workspace_payload(
                file_index=file_index,
                payload_index=payload_index,
                tab_count=tab_count,
                favorite_count=favorite_count,
                nested_json_layers=nested_json_layers,
            )
            for payload_index in range(payloads_per_file)
        ]
        path = root / f"synthetic-{file_index:02d}.edge"
        path.write_bytes(make_edge_bytes(payloads, corrupt_members=corrupt_members))
        paths.append(path)
    return paths


def benchmark_once(paths: list[Path], *, mode: str) -> tuple[float, int, int, dict[str, int]]:
    start = time.perf_counter()
    exported_links = 0
    statuses: dict[str, int] = {}
    for path in paths:
        file_result, _ = app.process_edge_file(
            path=path,
            mode=mode,
            exclude_schemes=set(),
        )
        statuses[file_result.status] = statuses.get(file_result.status, 0) + 1
        exported_links += file_result.exported_link_count
    elapsed = time.perf_counter() - start
    return elapsed, len(paths), exported_links, statuses


def benchmark_paths(paths: list[Path], *, runs: int, mode: str) -> dict[str, object]:
    timings: list[float] = []
    total_files = 0
    exported_links = 0
    statuses: dict[str, int] = {}

    for _ in range(runs):
        elapsed, total_files, exported_links, statuses = benchmark_once(paths, mode=mode)
        timings.append(elapsed)

    return {
        "files": total_files,
        "input_bytes": sum(path.stat().st_size for path in paths),
        "runs": runs,
        "best_seconds": round(min(timings), 4),
        "mean_seconds": round(statistics.mean(timings), 4),
        "median_seconds": round(statistics.median(timings), 4),
        "exported_links": exported_links,
        "statuses": statuses,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark Edge workspace extraction without workbook generation."
    )
    parser.add_argument(
        "--input",
        help="Optional .edge file or directory to benchmark instead of synthetic fixtures.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of benchmark runs to execute (default: 5).",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "tabs", "favorites"],
        default="both",
        help="Export mode to simulate during extraction (default: both).",
    )
    parser.add_argument(
        "--files",
        type=int,
        default=4,
        help="Synthetic .edge files to generate when --input is omitted.",
    )
    parser.add_argument(
        "--payloads",
        type=int,
        default=6,
        help="Synthetic gzip payloads per file.",
    )
    parser.add_argument(
        "--tabs",
        type=int,
        default=2000,
        help="Synthetic tabs per payload.",
    )
    parser.add_argument(
        "--favorites",
        type=int,
        default=500,
        help="Synthetic favorites per payload.",
    )
    parser.add_argument(
        "--nested-json-layers",
        type=int,
        default=1,
        help="Nested JSON-string wrappers per payload.",
    )
    parser.add_argument(
        "--corrupt-members",
        type=int,
        default=0,
        help="Corrupt gzip members to append per file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.input:
        paths = app.iter_edge_files(Path(args.input).expanduser())
        scenario = str(Path(args.input).expanduser())
        summary = benchmark_paths(paths, runs=args.runs, mode=args.mode)
    else:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = write_synthetic_corpus(
                root,
                files=args.files,
                payloads_per_file=args.payloads,
                tab_count=args.tabs,
                favorite_count=args.favorites,
                nested_json_layers=args.nested_json_layers,
                corrupt_members=args.corrupt_members,
            )
            scenario = "synthetic"
            summary = benchmark_paths(paths, runs=args.runs, mode=args.mode)

    summary.update({"mode": args.mode, "scenario": scenario})
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
