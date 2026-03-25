"""
Installed compatibility wrapper that preserves the legacy ``edge_workspace_links`` import.
"""

from __future__ import annotations

from pathlib import Path

from edge_workspace_links_app import (
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
    build_summary_rows,
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
    process_edge_file,
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


def build_export_rows(
    workspace_file: str,
    tabs: list[LinkRecord],
    favorites: list[LinkRecord],
    mode: str,
    exclude_schemes: set[str],
) -> list[dict[str, str]]:
    return [
        {
            "workspace_file": row.workspace_file,
            "source": row.source,
            "url": row.url,
            "title": row.title,
        }
        for row in _build_export_rows(
            workspace_file=workspace_file,
            tabs=tabs,
            favorites=favorites,
            mode=mode,
            exclude_schemes=exclude_schemes,
        )
    ]


def resolve_output_path(
    input_path: Path,
    output: str | None,
    output_format: str = "xlsx",
) -> Path:
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
