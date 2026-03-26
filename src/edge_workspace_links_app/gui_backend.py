from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cli import format_status_message
from .models import ExportRow, FileResult
from .reporting import (
    INTERNAL_SCHEMES,
    SUCCESS_STATUSES,
    build_summary_rows,
    iter_edge_files,
    process_edge_file,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Edge Workspace extraction for a desktop GUI client and emit a machine-readable JSON "
            "payload to stdout."
        )
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to a .edge file or a directory containing .edge files.",
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


def serialize_rows(rows: list[ExportRow]) -> list[dict[str, str]]:
    return [
        {
            "workspace_file": row.workspace_file,
            "source": row.source,
            "url": row.url,
            "title": row.title,
        }
        for row in rows
    ]


def serialize_file_rows(file_rows: list[FileResult]) -> list[dict[str, object]]:
    return [
        {
            "workspace_file": row.workspace_file,
            "status": row.status,
            "detail": row.detail,
            "extracted_tab_count": row.extracted_tab_count,
            "extracted_favorite_count": row.extracted_favorite_count,
            "exported_link_count": row.exported_link_count,
        }
        for row in file_rows
    ]


def result_payload(rows: list[ExportRow], summary_rows: list[tuple[str, int]], file_rows: list[FileResult]) -> dict[str, object]:
    return {
        "links": serialize_rows(rows),
        "summary": {metric: value for metric, value in summary_rows},
        "files": serialize_file_rows(file_rows),
    }


def response_payload(
    *,
    status: str,
    code: str,
    message: str,
    rows: list[ExportRow] | None = None,
    summary_rows: list[tuple[str, int]] | None = None,
    file_rows: list[FileResult] | None = None,
) -> dict[str, object]:
    notices = [format_status_message(row) for row in (file_rows or []) if row.status != "ok"]
    payload: dict[str, object] = {
        "status": status,
        "code": code,
        "message": message,
        "notices": notices,
    }
    if rows is not None and summary_rows is not None and file_rows is not None:
        payload["result"] = result_payload(rows, summary_rows, file_rows)
    else:
        payload["result"] = None
    return payload


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).expanduser()

    try:
        edge_files = iter_edge_files(input_path)
    except FileNotFoundError as exc:
        emit(
            response_payload(
                status="error",
                code="input_not_found",
                message=str(exc),
            )
        )
        return 2

    if not edge_files:
        emit(
            response_payload(
                status="error",
                code="no_edge_files",
                message="No .edge files found in the input path.",
            )
        )
        return 1

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

    summary_rows = build_summary_rows(edge_files=edge_files, file_rows=file_rows, rows=rows)
    successful_rows = [row for row in file_rows if row.status in SUCCESS_STATUSES]

    if not successful_rows:
        emit(
            response_payload(
                status="error",
                code="no_successful_workspaces",
                message="No workspace files were processed successfully.",
                rows=rows,
                summary_rows=summary_rows,
                file_rows=file_rows,
            )
        )
        return 1

    emit(
        response_payload(
            status="ok",
            code="ok",
            message=(
                f"Processed {len(successful_rows)} workspace file(s) and exported {len(rows)} link(s)."
            ),
            rows=rows,
            summary_rows=summary_rows,
            file_rows=file_rows,
        )
    )
    return 0


def cli() -> None:
    raise SystemExit(main(sys.argv[1:]))


if __name__ == "__main__":
    cli()
