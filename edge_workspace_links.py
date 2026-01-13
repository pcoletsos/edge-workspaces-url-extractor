#!/usr/bin/env python3
"""
Extract tab URLs from Microsoft Edge Workspace .edge files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import zlib
from pathlib import Path
from typing import Any, Iterable


GZIP_MAGIC = b"\x1f\x8b"
INTERNAL_SCHEMES = {"about", "chrome", "edge", "file", "microsoft-edge"}


def default_input_path() -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve().parent)
    return "."


def iter_gzip_offsets(data: bytes) -> Iterable[int]:
    start = 0
    while True:
        idx = data.find(GZIP_MAGIC, start)
        if idx == -1:
            return
        yield idx
        start = idx + 1


def decompress_payloads(data: bytes) -> list[bytes]:
    payloads: list[bytes] = []
    seen: set[bytes] = set()
    for idx in iter_gzip_offsets(data):
        try:
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
            out = decompressor.decompress(data[idx:])
            if not decompressor.eof or not out:
                continue
            digest = hashlib.sha256(out).digest()
            if digest in seen:
                continue
            seen.add(digest)
            payloads.append(out)
        except zlib.error:
            continue
    return payloads


def extract_links_from_payloads(payloads: Iterable[bytes]) -> list[dict[str, str]]:
    text = b"\n".join(payloads).decode("utf-8", errors="ignore")
    clean = "".join(ch if ord(ch) >= 0x20 else " " for ch in text)

    links: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add_link(url: str, title: str | None) -> None:
        key = (url, title or "")
        if key in seen:
            return
        seen.add(key)
        links.append({"url": url, "title": title or ""})

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "nodeType" in obj and "url" in obj:
                node_type = obj.get("nodeType")
                url = obj.get("url")
                if str(node_type) == "1" and isinstance(url, str) and url:
                    add_link(url, obj.get("title"))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, str):
            candidate = obj.strip()
            if candidate.startswith("{") or candidate.startswith("["):
                try:
                    nested = json.loads(candidate)
                except Exception:
                    return
                walk(nested)

    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(clean):
        if clean[idx] not in "{[":
            idx += 1
            continue
        try:
            obj, end = decoder.raw_decode(clean, idx)
            walk(obj)
            idx = end
        except json.JSONDecodeError:
            idx += 1

    return links


def iter_edge_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(input_path.glob("*.edge"))
    raise FileNotFoundError(f"Input path not found: {input_path}")


def filter_links(
    links: list[dict[str, str]], exclude_schemes: set[str]
) -> list[dict[str, str]]:
    if not exclude_schemes:
        return links
    filtered: list[dict[str, str]] = []
    for link in links:
        url = link.get("url", "")
        scheme = url.split(":", 1)[0].lower() if ":" in url else ""
        if scheme in exclude_schemes:
            continue
        filtered.append(link)
    return filtered


def resolve_output_path(input_path: Path, fmt: str, output: str | None) -> str:
    if output:
        return output
    base_dir = input_path if input_path.is_dir() else input_path.parent
    return str(base_dir / f"edge_workspace_links.{fmt}")


def write_output(
    rows: list[dict[str, str]], fmt: str, output_path: str
) -> None:
    if output_path == "-":
        out_file = sys.stdout
        close_file = False
    else:
        out_file = open(output_path, "w", newline="", encoding="utf-8")
        close_file = True

    try:
        if fmt in {"csv", "tsv"}:
            delimiter = "," if fmt == "csv" else "\t"
            writer = csv.DictWriter(
                out_file, fieldnames=["workspace_file", "url", "title"], delimiter=delimiter
            )
            writer.writeheader()
            writer.writerows(rows)
        else:
            json.dump(rows, out_file, indent=2)
            out_file.write("\n")
    finally:
        if close_file:
            out_file.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract tab URLs from Edge Workspace .edge files."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=default_input_path(),
        help=(
            "Path to a .edge file or a directory containing .edge files. "
            "Defaults to the script/exe location."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path. Use '-' to write to stdout.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["csv", "json", "tsv"],
        default="csv",
        help="Output format.",
    )
    parser.add_argument(
        "--exclude-schemes",
        nargs="*",
        default=[],
        help="URL schemes to exclude (example: edge chrome file).",
    )
    parser.add_argument(
        "--exclude-internal",
        action="store_true",
        help="Exclude internal browser URLs (edge, chrome, about, file).",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Sort output rows by workspace file and URL.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).expanduser()

    try:
        edge_files = iter_edge_files(input_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not edge_files:
        print("No .edge files found in the input path.", file=sys.stderr)
        return 1

    exclude_schemes = {s.lower() for s in args.exclude_schemes}
    if args.exclude_internal:
        exclude_schemes.update(INTERNAL_SCHEMES)

    rows: list[dict[str, str]] = []
    for path in edge_files:
        data = path.read_bytes()
        payloads = decompress_payloads(data)
        if not payloads:
            continue
        links = extract_links_from_payloads(payloads)
        links = filter_links(links, exclude_schemes)
        for link in links:
            rows.append(
                {
                    "workspace_file": path.name,
                    "url": link["url"],
                    "title": link["title"],
                }
            )

    if args.sort:
        rows.sort(key=lambda row: (row["workspace_file"], row["url"], row["title"]))

    output_path = resolve_output_path(input_path, args.format, args.output)
    write_output(rows, args.format, output_path)

    target = "stdout" if output_path == "-" else output_path
    print(
        f"Wrote {len(rows)} links from {len(edge_files)} workspace file(s) to {target}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
