from __future__ import annotations

from pathlib import Path

from .models import ExportRow, FileResult, LinkRecord
from .parser import extract_workspace_data, scan_gzip_payloads


INTERNAL_SCHEMES = {"about", "chrome", "edge", "file", "microsoft-edge"}
SUCCESS_STATUSES = {"ok", "no_links"}


def iter_edge_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(input_path.glob("*.edge"))
    raise FileNotFoundError(f"Input path not found: {input_path}")


def filter_links(links: list[LinkRecord], exclude_schemes: set[str]) -> list[LinkRecord]:
    if not exclude_schemes:
        return links
    filtered: list[LinkRecord] = []
    for link in links:
        scheme = link.url.split(":", 1)[0].lower() if ":" in link.url else ""
        if scheme in exclude_schemes:
            continue
        filtered.append(link)
    return filtered


def unique_by_url(links: list[LinkRecord]) -> dict[str, str]:
    url_to_title: dict[str, str] = {}
    for link in links:
        if not link.url:
            continue
        if link.url not in url_to_title or (not url_to_title[link.url] and link.title):
            url_to_title[link.url] = link.title
    return url_to_title


def build_export_rows(
    workspace_file: str,
    tabs: list[LinkRecord],
    favorites: list[LinkRecord],
    mode: str,
    exclude_schemes: set[str],
) -> list[ExportRow]:
    filtered_tabs = filter_links(tabs, exclude_schemes)
    filtered_favorites = filter_links(favorites, exclude_schemes)

    tab_urls = unique_by_url(filtered_tabs) if mode in {"both", "tabs"} else {}
    favorite_urls = unique_by_url(filtered_favorites) if mode in {"both", "favorites"} else {}

    combined_urls: dict[str, tuple[str, str]] = {}
    for url, title in favorite_urls.items():
        combined_urls[url] = ("favorite", title)
    for url, title in tab_urls.items():
        if url in combined_urls:
            continue
        combined_urls[url] = ("tab", title)

    return [
        ExportRow(
            workspace_file=workspace_file,
            source=source,
            url=url,
            title=title,
        )
        for url, (source, title) in combined_urls.items()
    ]


def process_edge_file(
    path: Path,
    mode: str,
    exclude_schemes: set[str],
) -> tuple[FileResult, list[ExportRow]]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        return (
            FileResult(
                workspace_file=path.name,
                status="read_error",
                detail=f"Could not read file: {exc}",
            ),
            [],
        )

    try:
        payload_scan = scan_gzip_payloads(data)
        if not payload_scan.had_gzip_magic:
            return (
                FileResult(
                    workspace_file=path.name,
                    status="not_workspace",
                    detail="No gzip workspace payloads were found.",
                ),
                [],
            )
        if not payload_scan.payloads:
            detail = "Found gzip members but could not decompress a workspace payload."
            if payload_scan.oversized_members:
                detail = "Found gzip members, but all decoded payloads exceeded the size guardrail."
            return (
                FileResult(
                    workspace_file=path.name,
                    status="parse_error",
                    detail=detail,
                ),
                [],
            )

        diagnostics = extract_workspace_data(payload_scan.payloads)
    except Exception as exc:
        return (
            FileResult(
                workspace_file=path.name,
                status="parse_error",
                detail=f"Could not parse workspace data: {exc}",
            ),
            [],
        )

    if diagnostics.json_objects_found == 0:
        return (
            FileResult(
                workspace_file=path.name,
                status="parse_error",
                detail="Decompressed payloads did not yield readable JSON objects.",
            ),
            [],
        )

    if diagnostics.workspace_markers_found == 0:
        return (
            FileResult(
                workspace_file=path.name,
                status="not_workspace",
                detail="Decoded payloads did not contain Edge Workspace content.",
            ),
            [],
        )

    export_rows = build_export_rows(
        workspace_file=path.name,
        tabs=diagnostics.tabs,
        favorites=diagnostics.favorites,
        mode=mode,
        exclude_schemes=exclude_schemes,
    )
    extracted_tab_count = len(diagnostics.tabs)
    extracted_favorite_count = len(diagnostics.favorites)
    exported_link_count = len(export_rows)

    if extracted_tab_count == 0 and extracted_favorite_count == 0:
        detail = "Workspace metadata was found, but no tabs or favorites were extracted."
        if payload_scan.failed_members:
            detail += f" {payload_scan.failed_members} gzip member(s) were skipped."
        if payload_scan.oversized_members:
            detail += f" {payload_scan.oversized_members} oversized gzip member(s) were skipped."
        return (
            FileResult(
                workspace_file=path.name,
                status="no_links",
                detail=detail,
                extracted_tab_count=extracted_tab_count,
                extracted_favorite_count=extracted_favorite_count,
                exported_link_count=exported_link_count,
            ),
            export_rows,
        )

    detail = "Workspace processed successfully."
    if exported_link_count == 0:
        detail = "Workspace processed successfully, but mode/filters exported no links."
    elif payload_scan.failed_members:
        detail += f" {payload_scan.failed_members} gzip member(s) were skipped."
    if payload_scan.oversized_members:
        detail += f" {payload_scan.oversized_members} oversized gzip member(s) were skipped."

    return (
        FileResult(
            workspace_file=path.name,
            status="ok",
            detail=detail,
            extracted_tab_count=extracted_tab_count,
            extracted_favorite_count=extracted_favorite_count,
            exported_link_count=exported_link_count,
        ),
        export_rows,
    )


def build_summary_rows(
    edge_files: list[Path], file_rows: list[FileResult], rows: list[ExportRow]
) -> list[tuple[str, int]]:
    successful_rows = [row for row in file_rows if row.status in SUCCESS_STATUSES]
    files_with_tabs = sum(1 for row in successful_rows if row.extracted_tab_count > 0)
    files_with_favorites = sum(1 for row in successful_rows if row.extracted_favorite_count > 0)
    files_with_extracted_links = sum(
        1 for row in successful_rows if (row.extracted_tab_count + row.extracted_favorite_count) > 0
    )
    files_with_exported_links = sum(1 for row in successful_rows if row.exported_link_count > 0)
    no_link_workspaces = sum(1 for row in file_rows if row.status == "no_links")
    read_errors = sum(1 for row in file_rows if row.status == "read_error")
    parse_errors = sum(1 for row in file_rows if row.status == "parse_error")
    not_workspace_files = sum(1 for row in file_rows if row.status == "not_workspace")
    tabs_total = sum(row.extracted_tab_count for row in successful_rows)
    favorites_total = sum(row.extracted_favorite_count for row in successful_rows)
    links_total = len(rows)
    unique_urls = len({row.url for row in rows})

    return [
        ("input_files_found", len(edge_files)),
        ("workspace_files_processed", len(successful_rows)),
        ("workspace_files_with_tabs_extracted", files_with_tabs),
        ("workspace_files_with_favorites_extracted", files_with_favorites),
        ("workspace_files_with_extracted_links", files_with_extracted_links),
        ("workspace_files_with_exported_links", files_with_exported_links),
        ("no_link_workspaces", no_link_workspaces),
        ("not_workspace_files", not_workspace_files),
        ("read_error_files", read_errors),
        ("parse_error_files", parse_errors),
        ("extracted_tabs_total", tabs_total),
        ("extracted_favorites_total", favorites_total),
        ("exported_links_total", links_total),
        ("unique_exported_urls", unique_urls),
    ]
