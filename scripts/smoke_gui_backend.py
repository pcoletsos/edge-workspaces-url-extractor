#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def workspace_document() -> dict[str, object]:
    return {
        "payload": {
            "content": {
                "subdirectories": {
                    "tabstripmodel": {
                        "subdirectories": {
                            "webcontents": {
                                "subdirectories": {
                                    "0": {
                                        "storage": {
                                            "currentNavigationIndex": {"value": 0},
                                        },
                                        "subdirectories": {
                                            "navigationStack": {
                                                "subdirectories": {
                                                    "0": {
                                                        "storage": {
                                                            "virtualUrl": {
                                                                "value": "https://example.com/tab-only"
                                                            },
                                                            "title": {"value": "Tab only"},
                                                        }
                                                    },
                                                    "1": {
                                                        "storage": {
                                                            "virtualUrl": {"value": "edge://settings"},
                                                            "title": {"value": "Internal settings"},
                                                        }
                                                    },
                                                }
                                            }
                                        },
                                    }
                                }
                            }
                        }
                    },
                    "favorites": {
                        "storage": {
                            "0": {
                                "value": {
                                    "nodeType": "1",
                                    "url": "https://example.com/favorite-only",
                                    "title": "Favorite only",
                                }
                            }
                        }
                    },
                }
            }
        }
    }


def write_edge_fixture(path: Path) -> Path:
    payload = json.dumps(workspace_document(), separators=(",", ":")).encode("utf-8")
    path.write_bytes(b"fixture" + gzip.compress(payload) + b"tail")
    return path


def build_command(args: argparse.Namespace) -> list[str]:
    if args.backend_exe:
        return [str(Path(args.backend_exe).resolve())]
    return [sys.executable, "-m", args.python_module]


def build_env(args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    if args.python_path:
        injected = [str(Path(path).resolve()) for path in args.python_path]
        existing = env.get("PYTHONPATH")
        if existing:
            injected.append(existing)
        env["PYTHONPATH"] = os.pathsep.join(injected)
    return env


def run_smoke(command: list[str], env: dict[str, str]) -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        input_dir = root / "input"
        input_dir.mkdir()
        write_edge_fixture(input_dir / "workspace.edge")

        completed = subprocess.run(
            command + ["--input", str(input_dir), "--exclude-internal", "--sort"],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
        )

        if completed.returncode != 0:
            raise AssertionError(
                "Backend smoke command failed:\n"
                f"command={command!r}\n"
                f"stdout={completed.stdout}\n"
                f"stderr={completed.stderr}"
            )

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                "Backend smoke command did not emit JSON.\n"
                f"stdout={completed.stdout}\n"
                f"stderr={completed.stderr}"
            ) from exc

        if payload.get("status") != "ok" or payload.get("code") != "ok":
            raise AssertionError(f"Unexpected backend smoke payload: {payload!r}")

        result = payload.get("result")
        if not isinstance(result, dict):
            raise AssertionError(f"Missing backend smoke result payload: {payload!r}")

        links = result.get("links")
        if links != [
            {
                "workspace_file": "workspace.edge",
                "source": "favorite",
                "url": "https://example.com/favorite-only",
                "title": "Favorite only",
            },
            {
                "workspace_file": "workspace.edge",
                "source": "tab",
                "url": "https://example.com/tab-only",
                "title": "Tab only",
            },
        ]:
            raise AssertionError(f"Unexpected backend smoke links: {links!r}")

        summary = result.get("summary")
        if not isinstance(summary, dict):
            raise AssertionError(f"Missing backend smoke summary payload: {payload!r}")

        expected_summary = {
            "workspace_files_processed": 1,
            "extracted_tabs_total": 1,
            "extracted_favorites_total": 1,
            "exported_links_total": 2,
        }
        for metric, value in expected_summary.items():
            if summary.get(metric) != value:
                raise AssertionError(f"Unexpected summary metric {metric!r}: {summary.get(metric)!r}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an end-to-end smoke test for the JSON backend executable."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--backend-exe", help="Path to the packaged GUI backend executable.")
    target.add_argument(
        "--python-module",
        help="Python module to invoke with `python -m`, for example edge_workspace_links_app.gui_backend.",
    )
    parser.add_argument(
        "--python-path",
        action="append",
        default=[],
        help="Additional path to prepend to PYTHONPATH before invoking --python-module.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    run_smoke(build_command(args), build_env(args))
    target = args.backend_exe or args.python_module
    print(f"Backend smoke test passed for {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
