from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LinkRecord:
    url: str
    title: str


@dataclass(frozen=True)
class ExportRow:
    workspace_file: str
    source: str
    url: str
    title: str


@dataclass(frozen=True)
class PayloadScanResult:
    had_gzip_magic: bool
    payloads: list[bytes]
    failed_members: int = 0
    oversized_members: int = 0


@dataclass(frozen=True)
class ExtractionDiagnostics:
    tabs: list[LinkRecord]
    favorites: list[LinkRecord]
    json_objects_found: int = 0
    content_objects_found: int = 0
    workspace_markers_found: int = 0


@dataclass(frozen=True)
class FileResult:
    workspace_file: str
    status: str
    detail: str = ""
    extracted_tab_count: int = 0
    extracted_favorite_count: int = 0
    exported_link_count: int = 0
