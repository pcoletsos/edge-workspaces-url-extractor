#!/usr/bin/env python3
"""
Backward-compatible script entry point and API surface for the package layout.
"""

from __future__ import annotations

import sys
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from edge_workspace_links_app import (  # noqa: E402
    CONTROL_CHAR_TRANSLATION,
    FORMULA_PREFIXES,
    GZIP_MAGIC,
    INTERNAL_SCHEMES,
    MAX_PAYLOAD_BYTES,
    NESTED_JSON_HINTS,
    SUCCESS_STATUSES,
    ExportRow,
    ExtractionDiagnostics,
    FileResult,
    LinkRecord,
    PayloadScanResult,
    build_export_rows as _build_export_rows,
    build_summary_rows as _build_summary_rows,
    clean_json_text,
    cli,
    default_input_path,
    extract_favorites_from_content,
    extract_tabs_from_content,
    extract_workspace_data,
    filter_links,
    format_status_message,
    has_workspace_markers,
    iter_content_objects,
    iter_edge_files,
    iter_gzip_offsets,
    iter_json_objects,
    main,
    parse_args,
    process_edge_file as _process_edge_file,
    resolve_output_targets as _resolve_output_targets,
    safe_excel_text,
    safe_hyperlink_target,
    scan_gzip_payloads,
    typed_value,
    unique_by_url,
    validate_output_targets as _validate_output_targets,
    workbook_is_available,
    write_csv_output,
    write_json_output,
    write_output,
)


CONTROL_BYTE_TRANSLATION = CONTROL_CHAR_TRANSLATION
resolve_output_targets = _resolve_output_targets
validate_output_targets = _validate_output_targets


def _legacy_export_row(row: ExportRow) -> dict[str, str]:
    return {
        "workspace_file": row.workspace_file,
        "source": row.source,
        "url": row.url,
        "title": row.title,
    }


def _coerce_export_row(row: ExportRow | dict[str, str]) -> ExportRow:
    if isinstance(row, ExportRow):
        return row
    return ExportRow(
        workspace_file=row["workspace_file"],
        source=row["source"],
        url=row["url"],
        title=row["title"],
    )


def build_export_rows(
    workspace_file: str,
    tabs: list[LinkRecord],
    favorites: list[LinkRecord],
    mode: str,
    exclude_schemes: set[str],
) -> list[dict[str, str]]:
    return [
        _legacy_export_row(row)
        for row in _build_export_rows(
            workspace_file=workspace_file,
            tabs=tabs,
            favorites=favorites,
            mode=mode,
            exclude_schemes=exclude_schemes,
        )
    ]


def build_summary_rows(
    edge_files: list[Path],
    file_rows: list[FileResult],
    rows: list[ExportRow] | list[dict[str, str]],
) -> list[tuple[str, int]]:
    return _build_summary_rows(
        edge_files=edge_files,
        file_rows=file_rows,
        rows=[_coerce_export_row(row) for row in rows],
    )


def process_edge_file(
    path: Path,
    mode: str,
    exclude_schemes: set[str],
) -> tuple[FileResult, list[dict[str, str]]]:
    file_result, rows = _process_edge_file(
        path=path,
        mode=mode,
        exclude_schemes=exclude_schemes,
    )
    return file_result, [_legacy_export_row(row) for row in rows]


def resolve_output_path(
    input_path: Path,
    output: str | None,
    output_format: str = "xlsx",
) -> Path:
    if output:
        return Path(output).expanduser()
    return _resolve_output_targets(input_path, output, output_format)[0]


def validate_output_path(output_path: Path) -> str | None:
    return _validate_output_targets([Path(output_path)])


__all__ = [
    "CONTROL_BYTE_TRANSLATION",
    "CONTROL_CHAR_TRANSLATION",
    "ExportRow",
    "ExtractionDiagnostics",
    "FORMULA_PREFIXES",
    "FileResult",
    "GZIP_MAGIC",
    "INTERNAL_SCHEMES",
    "LinkRecord",
    "MAX_PAYLOAD_BYTES",
    "NESTED_JSON_HINTS",
    "PayloadScanResult",
    "SUCCESS_STATUSES",
    "build_export_rows",
    "build_summary_rows",
    "clean_json_text",
    "cli",
    "default_input_path",
    "extract_favorites_from_content",
    "extract_tabs_from_content",
    "extract_workspace_data",
    "filter_links",
    "format_status_message",
    "has_workspace_markers",
    "iter_content_objects",
    "iter_edge_files",
    "iter_gzip_offsets",
    "iter_json_objects",
    "main",
    "parse_args",
    "process_edge_file",
    "resolve_output_path",
    "resolve_output_targets",
    "safe_excel_text",
    "safe_hyperlink_target",
    "scan_gzip_payloads",
    "typed_value",
    "unique_by_url",
    "validate_output_path",
    "validate_output_targets",
    "workbook_is_available",
    "write_csv_output",
    "write_json_output",
    "write_output",
]


if __name__ == "__main__":
    cli()
