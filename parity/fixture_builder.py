from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any


CASES_PATH = Path(__file__).with_name("cases.json")
GZIP_MAGIC = b"\x1f\x8b"


def load_cases() -> list[dict[str, Any]]:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    return payload["cases"]


def build_workspace_content(builder: dict[str, Any]) -> dict[str, Any]:
    tab_entries: dict[str, Any] = {}
    for tab_index, tab in enumerate(builder.get("tabs", [])):
        navigations = {
            str(entry["index"]): {
                "storage": {
                    "virtualUrl": {"value": entry["url"]},
                    "title": {"value": entry.get("title", "")},
                }
            }
            for entry in tab.get("navigations", [])
        }
        tab_entries[f"tab-{tab_index}"] = {
            "storage": {
                "currentNavigationIndex": {"value": tab.get("current_index", 0)},
            },
            "subdirectories": {
                "navigationStack": {
                    "subdirectories": navigations,
                }
            },
        }

    favorite_entries = {
        str(index): {
            "value": {
                "nodeType": "1",
                "url": favorite["url"],
                "title": favorite.get("title", ""),
            }
        }
        for index, favorite in enumerate(builder.get("favorites", []))
    }

    return {
        "subdirectories": {
            "tabstripmodel": {
                "subdirectories": {
                    "webcontents": {
                        "subdirectories": tab_entries,
                    }
                }
            },
            "favorites": {"storage": favorite_entries},
        }
    }


def build_workspace_document(case: dict[str, Any]) -> dict[str, Any]:
    builder = case["builder"]
    content = build_workspace_content(builder)
    kind = builder.get("kind", "direct")
    if kind == "nested_json":
        return {
            "payload": {
                "snapshots": [
                    {"raw": json.dumps({"content": content}, separators=(",", ":"))}
                ]
            }
        }
    return {"payload": {"content": content}}


def wrap_gzip_payload(document: dict[str, Any]) -> bytes:
    payload = json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return b"fixture" + gzip.compress(payload) + b"tail"


def build_edge_bytes(case: dict[str, Any]) -> bytes:
    builder = case["builder"]
    kind = builder.get("kind", "direct")
    if kind == "non_workspace":
        return wrap_gzip_payload({"payload": {"metadata": {"label": case["name"]}}})
    if kind == "invalid_gzip":
        return b"fixture" + GZIP_MAGIC + b"broken-member" + b"tail"

    document = build_workspace_document(case)
    return wrap_gzip_payload(document)


def write_case_file(case: dict[str, Any], directory: Path) -> Path:
    target = directory / f"{case['name']}.edge"
    target.write_bytes(build_edge_bytes(case))
    return target
