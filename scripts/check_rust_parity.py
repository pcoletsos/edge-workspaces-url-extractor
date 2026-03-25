from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from parity.fixture_builder import load_cases, write_case_file

import edge_workspace_links as py_impl


DEFAULT_MANIFEST = ROOT / "rust" / "edge-workspace-links-rs" / "Cargo.toml"


def export_view(rows):
    payload = []
    for row in rows:
        if isinstance(row, dict):
            payload.append(
                {
                    "source": row["source"],
                    "url": row["url"],
                    "title": row["title"],
                }
            )
            continue
        payload.append({"source": row.source, "url": row.url, "title": row.title})
    return payload


def link_view(links):
    return [{"url": link.url, "title": link.title} for link in links]


def binary_path(manifest_path: Path, release: bool) -> Path:
    profile = "release" if release else "debug"
    suffix = ".exe" if os.name == "nt" else ""
    return manifest_path.parent / "target" / profile / f"edge-workspace-links-rs{suffix}"


def ensure_binary(manifest_path: Path, release: bool) -> Path:
    target = binary_path(manifest_path, release)
    if target.exists():
        return target
    command = ["cargo", "build", "--manifest-path", str(manifest_path)]
    if release:
        command.append("--release")
    subprocess.run(command, check=True, cwd=ROOT)
    return target


def rust_case_view(binary: Path, edge_path: Path) -> dict:
    completed = subprocess.run(
        [str(binary), "--input", str(edge_path)],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    return payload["files"][0]


def rust_directory_view(binary: Path, input_path: Path) -> dict[str, dict]:
    completed = subprocess.run(
        [str(binary), "--input", str(input_path)],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    return {entry["workspace_file"]: entry for entry in payload["files"]}


def empty_exports() -> dict[str, list[dict[str, str]]]:
    return {
        "both": [],
        "tabs": [],
        "favorites": [],
        "exclude_internal": [],
    }


def python_case_view(edge_path: Path) -> dict:
    file_result, both_rows = py_impl.process_edge_file(edge_path, "both", set())
    _, tab_rows = py_impl.process_edge_file(edge_path, "tabs", set())
    _, favorite_rows = py_impl.process_edge_file(edge_path, "favorites", set())
    _, filtered_rows = py_impl.process_edge_file(edge_path, "both", py_impl.INTERNAL_SCHEMES)
    payload_scan = py_impl.scan_gzip_payloads(edge_path.read_bytes())
    diagnostics = py_impl.extract_workspace_data(payload_scan.payloads)

    return {
        "status": file_result.status,
        "tabs": link_view(diagnostics.tabs),
        "favorites": link_view(diagnostics.favorites),
        "exports": {
            "both": export_view(both_rows),
            "tabs": export_view(tab_rows),
            "favorites": export_view(favorite_rows),
            "exclude_internal": export_view(filtered_rows),
        },
    }


def python_directory_view(input_path: Path) -> dict[str, dict]:
    payload: dict[str, dict] = {}
    for path in py_impl.iter_edge_files(input_path):
        if path.is_file():
            payload[path.name] = python_case_view(path)
            continue

        file_result, both_rows = py_impl.process_edge_file(path, "both", set())
        _, tab_rows = py_impl.process_edge_file(path, "tabs", set())
        _, favorite_rows = py_impl.process_edge_file(path, "favorites", set())
        _, filtered_rows = py_impl.process_edge_file(path, "both", py_impl.INTERNAL_SCHEMES)
        payload[path.name] = {
            "status": file_result.status,
            "tabs": [],
            "favorites": [],
            "exports": {
                "both": export_view(both_rows),
                "tabs": export_view(tab_rows),
                "favorites": export_view(favorite_rows),
                "exclude_internal": export_view(filtered_rows),
            },
        }
    return payload


def compare_case(name: str, actual: dict, expected: dict, source: str) -> list[str]:
    failures = []
    if actual["status"] != expected["status"]:
        failures.append(f"{source}:{name}: status {actual['status']} != {expected['status']}")
    if actual["tabs"] != expected["tabs"]:
        failures.append(f"{source}:{name}: tabs mismatch")
    if actual["favorites"] != expected["favorites"]:
        failures.append(f"{source}:{name}: favorites mismatch")
    for key in ("both", "tabs", "favorites", "exclude_internal"):
        if actual["exports"][key] != expected["exports"][key]:
            failures.append(f"{source}:{name}: exports.{key} mismatch")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run parity checks for the Rust prototype.")
    parser.add_argument(
        "--manifest-path",
        default=str(DEFAULT_MANIFEST),
        help="Path to the Rust Cargo.toml manifest.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Use a release build instead of the default debug build.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest_path).resolve()
    binary = ensure_binary(manifest_path, args.release)
    cases = load_cases()
    failures: list[str] = []
    case_by_name = {case["name"]: case for case in cases}

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for case in cases:
            edge_path = write_case_file(case, temp_path)
            expected = case["expected"]
            failures.extend(compare_case(case["name"], python_case_view(edge_path), expected, "python"))
            failures.extend(compare_case(case["name"], rust_case_view(binary, edge_path), expected, "rust"))

        write_case_file(case_by_name["dedupe_and_filters"], temp_path)
        unreadable_entry = temp_path / "unreadable.edge"
        unreadable_entry.mkdir()
        expected_directory = {
            "dedupe_and_filters.edge": case_by_name["dedupe_and_filters"]["expected"],
            "unreadable.edge": {
                "status": "read_error",
                "tabs": [],
                "favorites": [],
                "exports": empty_exports(),
            },
        }
        python_directory = python_directory_view(temp_path)
        rust_directory = rust_directory_view(binary, temp_path)
        for file_name, expected in expected_directory.items():
            failures.extend(
                compare_case(f"mixed_directory:{file_name}", python_directory[file_name], expected, "python")
            )
            failures.extend(
                compare_case(f"mixed_directory:{file_name}", rust_directory[file_name], expected, "rust")
            )

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(
        f"Rust parity passed for {len(cases)} case(s) plus mixed-directory read_error checks using {binary}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
