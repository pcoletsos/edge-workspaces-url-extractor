from __future__ import annotations

import gzip
import importlib.util
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "edge_workspace_links.py"


def load_module():
    spec = importlib.util.spec_from_file_location("edge_workspace_links", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def workspace_content(
    *,
    tabs: list[dict[str, Any]] | None = None,
    favorites: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tab_entries = {}
    for index, tab in enumerate(tabs or []):
        tab_entries[str(index)] = {
            "storage": {
                "currentNavigationIndex": {"value": 0},
            },
            "subdirectories": {
                "navigationStack": {
                    "subdirectories": {
                        "0": {
                            "storage": {
                                "virtualUrl": {"value": tab["url"]},
                                "title": {"value": tab.get("title", "")},
                            }
                        }
                    }
                }
            },
        }

    favorite_entries = {}
    for index, favorite in enumerate(favorites or []):
        favorite_entries[str(index)] = {
            "value": {
                "nodeType": "1",
                "url": favorite["url"],
                "title": favorite.get("title", ""),
            }
        }

    content = {
        "subdirectories": {
            "tabstripmodel": {"subdirectories": {"webcontents": {"subdirectories": tab_entries}}},
            "favorites": {"storage": favorite_entries},
        }
    }
    if extra:
        content.update(extra)
    return content


def workspace_document(*, tabs=None, favorites=None, extra=None) -> dict[str, Any]:
    return {
        "payload": {
            "content": workspace_content(tabs=tabs, favorites=favorites, extra=extra),
        }
    }


def gzip_member(document: dict[str, Any]) -> bytes:
    payload = json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return gzip.compress(payload)


def edge_bytes(*documents: dict[str, Any], prefix: bytes = b"", suffix: bytes = b"") -> bytes:
    chunks = [prefix]
    for document in documents:
        chunks.append(gzip_member(document))
    chunks.append(suffix)
    return b"".join(chunks)


def write_edge_file(path: Path, *documents: dict[str, Any], prefix: bytes = b"", suffix: bytes = b"") -> Path:
    path.write_bytes(edge_bytes(*documents, prefix=prefix, suffix=suffix))
    return path
