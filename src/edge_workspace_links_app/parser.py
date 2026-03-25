from __future__ import annotations

import hashlib
import json
import zlib
from typing import Any, Iterable

from .models import ExtractionDiagnostics, LinkRecord, PayloadScanResult


GZIP_MAGIC = b"\x1f\x8b"
CONTROL_CHAR_TRANSLATION = bytes.maketrans(bytes(range(32)), b" " * 32)
NESTED_JSON_HINTS = (
    '"content"',
    '"subdirectories"',
    '"tabstripmodel"',
    '"favorites"',
    '"webcontents"',
    '"navigationStack"',
)
MAX_PAYLOAD_BYTES = 64 * 1024 * 1024


def iter_gzip_offsets(data: bytes) -> Iterable[int]:
    start = 0
    while True:
        idx = data.find(GZIP_MAGIC, start)
        if idx == -1:
            return
        yield idx
        start = idx + 1


def scan_gzip_payloads(data: bytes) -> PayloadScanResult:
    payloads: list[bytes] = []
    seen: set[bytes] = set()
    had_gzip_magic = False
    failed_members = 0
    oversized_members = 0

    for idx in iter_gzip_offsets(data):
        had_gzip_magic = True
        try:
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
            out = decompressor.decompress(data[idx:], MAX_PAYLOAD_BYTES + 1)
            if len(out) > MAX_PAYLOAD_BYTES:
                oversized_members += 1
                continue
            if not decompressor.eof or not out:
                failed_members += 1
                continue
            digest = hashlib.sha256(out).digest()
            if digest in seen:
                continue
            seen.add(digest)
            payloads.append(out)
        except zlib.error:
            failed_members += 1

    return PayloadScanResult(
        had_gzip_magic=had_gzip_magic,
        payloads=payloads,
        failed_members=failed_members,
        oversized_members=oversized_members,
    )


def iter_json_objects(text: str) -> Iterable[Any]:
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(text):
        next_object = text.find("{", idx)
        next_array = text.find("[", idx)
        if next_object == -1:
            idx = next_array
        elif next_array == -1:
            idx = next_object
        else:
            idx = min(next_object, next_array)
        if idx == -1:
            return
        try:
            obj, end = decoder.raw_decode(text, idx)
        except json.JSONDecodeError:
            idx += 1
            continue
        yield obj
        idx = end


def iter_content_objects(obj: Any) -> Iterable[dict[str, Any]]:
    stack: list[Any] = [obj]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            content = current.get("content")
            if isinstance(content, dict):
                yield content
            for value in reversed(tuple(current.values())):
                if isinstance(value, (dict, list, str)):
                    stack.append(value)
        elif isinstance(current, list):
            for item in reversed(current):
                if isinstance(item, (dict, list, str)):
                    stack.append(item)
        elif isinstance(current, str):
            if "{" not in current and "[" not in current:
                continue
            candidate = current.strip()
            if not candidate.startswith(("{", "[")):
                continue
            if not any(hint in candidate for hint in NESTED_JSON_HINTS):
                continue
            try:
                nested = json.loads(candidate)
            except Exception:
                continue
            stack.append(nested)


def typed_value(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value:
        return value.get("value")
    return value


def has_workspace_markers(content: dict[str, Any]) -> bool:
    subdirectories = content.get("subdirectories", {})
    return isinstance(subdirectories, dict) and (
        "tabstripmodel" in subdirectories or "favorites" in subdirectories
    )


def extract_tabs_from_content(content: dict[str, Any]) -> list[LinkRecord]:
    links: list[LinkRecord] = []
    webcontents = (
        content.get("subdirectories", {})
        .get("tabstripmodel", {})
        .get("subdirectories", {})
        .get("webcontents", {})
        .get("subdirectories", {})
    )
    if not isinstance(webcontents, dict):
        return links

    for tab_data in webcontents.values():
        if not isinstance(tab_data, dict):
            continue
        storage = tab_data.get("storage", {})
        current_index = typed_value(storage.get("currentNavigationIndex"))
        if current_index is None:
            continue
        nav_stack = (
            tab_data.get("subdirectories", {})
            .get("navigationStack", {})
            .get("subdirectories", {})
        )
        if not isinstance(nav_stack, dict) or not nav_stack:
            continue
        current_key = str(current_index)
        entry = nav_stack.get(current_key)
        if not entry:
            numeric_keys = [int(key) for key in nav_stack.keys() if str(key).isdigit()]
            if numeric_keys:
                entry = nav_stack.get(str(max(numeric_keys)))
        if not entry:
            continue
        entry_storage = entry.get("storage", {})
        url = ""
        for key in ("virtualUrl", "originalRequestUrl", "url"):
            value = typed_value(entry_storage.get(key))
            if isinstance(value, str) and value:
                url = value
                break
        if not url:
            continue
        title_value = typed_value(entry_storage.get("title"))
        title = title_value if isinstance(title_value, str) else ""
        links.append(LinkRecord(url=url, title=title))

    return links


def extract_favorites_from_content(content: dict[str, Any]) -> list[LinkRecord]:
    links: list[LinkRecord] = []
    favorites = content.get("subdirectories", {}).get("favorites", {})
    if not isinstance(favorites, dict):
        return links
    storage = favorites.get("storage", {})
    if not isinstance(storage, dict):
        return links

    for entry in storage.values():
        node = typed_value(entry)
        if not isinstance(node, dict):
            continue
        node_type = node.get("nodeType")
        url = node.get("url")
        if str(node_type) != "1" or not isinstance(url, str) or not url:
            continue
        title = node.get("title")
        links.append(LinkRecord(url=url, title=title if isinstance(title, str) else ""))

    return links


def clean_json_text(payload: bytes) -> str:
    return payload.translate(CONTROL_CHAR_TRANSLATION).decode("utf-8", errors="ignore")


def extract_workspace_data(payloads: Iterable[bytes]) -> ExtractionDiagnostics:
    tabs: list[LinkRecord] = []
    favorites: list[LinkRecord] = []
    json_objects_found = 0
    content_objects_found = 0
    workspace_markers_found = 0

    for payload in payloads:
        clean = clean_json_text(payload)
        for obj in iter_json_objects(clean):
            json_objects_found += 1
            for content in iter_content_objects(obj):
                content_objects_found += 1
                if has_workspace_markers(content):
                    workspace_markers_found += 1
                tabs.extend(extract_tabs_from_content(content))
                favorites.extend(extract_favorites_from_content(content))

    return ExtractionDiagnostics(
        tabs=tabs,
        favorites=favorites,
        json_objects_found=json_objects_found,
        content_objects_found=content_objects_found,
        workspace_markers_found=workspace_markers_found,
    )
