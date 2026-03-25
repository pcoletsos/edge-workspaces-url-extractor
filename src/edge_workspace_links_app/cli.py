from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .exporters import workbook_is_available, write_csv_output, write_json_output, write_output
from .models import ExportRow, FileResult
from .reporting import (
    INTERNAL_SCHEMES,
    SUCCESS_STATUSES,
    build_summary_rows,
    iter_edge_files,
    process_edge_file,
)


def default_input_path() -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve().parent)
    return "."


def default_output_base(input_path: Path) -> Path:
    base_dir = input_path if input_path.is_dir() else input_path.parent
    return base_dir / "edge_workspace_links"


def resolve_output_targets(input_path: Path, output: str | None, output_format: str) -> list[Path]:
    raw_output = Path(output).expanduser() if output else default_output_base(input_path)
    if output and raw_output.exists() and raw_output.is_dir() and output_format in {"xlsx", "json"}:
        return [raw_output]
    if output_format == "xlsx":
        return [raw_output if raw_output.suffix else raw_output.with_suffix(".xlsx")]
    if output_format == "json":
        return [raw_output if raw_output.suffix else raw_output.with_suffix(".json")]

    if raw_output.exists() and raw_output.is_dir():
        base = raw_output / "edge_workspace_links"
    else:
        base = raw_output.with_suffix("") if raw_output.suffix else raw_output
    return [
        base.parent / f"{base.name}_links.csv",
        base.parent / f"{base.name}_summary.csv",
        base.parent / f"{base.name}_files.csv",
    ]


def validate_output_targets(output_targets: list[Path]) -> str | None:
    for output_path in output_targets:
        parent = output_path.parent if output_path.parent != Path("") else Path(".")
        if not parent.exists():
            return f"Output directory not found: {parent}"
        if not parent.is_dir():
            return f"Output path parent is not a directory: {parent}"
        if output_path.exists() and output_path.is_dir():
            return f"Output path is a directory: {output_path}"
    return None


def format_status_message(file_result: FileResult) -> str:
    message = f"{file_result.workspace_file}: {file_result.status}"
    if file_result.detail:
        message += f" - {file_result.detail}"
    return message


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract open tab URLs and workspace favorites from Edge Workspace .edge files."
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
        help=(
            "Output path. For xlsx/json this is a single file path. "
            "For csv this is treated as the output base name."
        ),
    )
    parser.add_argument(
        "--format",
        choices=["xlsx", "csv", "json"],
        default="xlsx",
        help="Output format to write (default: xlsx).",
    )
    parser.add_argument(
        "--exclude-schemes",
        nargs="*",
        default=[],
        help="URL schemes to exclude from exported links (example: edge chrome file).",
    )
    parser.add_argument(
        "--exclude-internal",
        action="store_true",
        help="Exclude internal browser URLs (about, chrome, edge, file, microsoft-edge).",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "tabs", "favorites"],
        default="both",
        help="What to export (default: both). Reports still show extracted tab and favorite counts.",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Sort exported links and per-file rows by workspace file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.format == "xlsx" and not workbook_is_available():
        print(
            "Missing dependency 'openpyxl'. Install with: pip install openpyxl",
            file=sys.stderr,
        )
        return 2

    input_path = Path(args.input).expanduser()

    try:
        edge_files = iter_edge_files(input_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not edge_files:
        print("No .edge files found in the input path.", file=sys.stderr)
        return 1

    output_targets = resolve_output_targets(input_path, args.output, args.format)
    output_target_error = validate_output_targets(output_targets)
    if output_target_error:
        print(output_target_error, file=sys.stderr)
        return 2

    exclude_schemes = {s.lower() for s in args.exclude_schemes}
    if args.exclude_internal:
        exclude_schemes.update(INTERNAL_SCHEMES)

    rows: list[ExportRow] = []
    file_rows: list[FileResult] = []
    for path in edge_files:
        file_result, export_rows = process_edge_file(
            path=path,
            mode=args.mode,
            exclude_schemes=exclude_schemes,
        )
        file_rows.append(file_result)
        rows.extend(export_rows)

    if args.sort:
        rows.sort(
            key=lambda row: (
                row.workspace_file,
                0 if row.source == "favorite" else 1,
                row.url,
                row.title,
            )
        )
        file_rows = sorted(file_rows, key=lambda row: row.workspace_file)

    for file_result in file_rows:
        if file_result.status != "ok":
            print(format_status_message(file_result), file=sys.stderr)

    successful_rows = [row for row in file_rows if row.status in SUCCESS_STATUSES]
    if not successful_rows:
        print("No workspace files were processed successfully.", file=sys.stderr)
        return 1

    summary_rows = build_summary_rows(edge_files=edge_files, file_rows=file_rows, rows=rows)

    try:
        if args.format == "xlsx":
            write_output(rows=rows, summary_rows=summary_rows, file_rows=file_rows, output_path=output_targets[0])
        elif args.format == "json":
            write_json_output(
                rows=rows,
                summary_rows=summary_rows,
                file_rows=file_rows,
                output_path=output_targets[0],
            )
        else:
            write_csv_output(
                rows=rows,
                summary_rows=summary_rows,
                file_rows=file_rows,
                output_paths=output_targets,
            )
    except OSError as exc:
        print(f"Could not write output: {exc}", file=sys.stderr)
        return 2

    destinations = ", ".join(str(path) for path in output_targets)
    print(
        f"Wrote {len(rows)} exported link(s) from {len(successful_rows)} workspace file(s) to {destinations}",
        file=sys.stderr,
    )
    return 0


def cli() -> None:
    raise SystemExit(main(sys.argv[1:]))
