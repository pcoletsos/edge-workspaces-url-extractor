#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from importlib import import_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def install_wheel(wheel: Path, target: Path) -> None:
    shutil.rmtree(target, ignore_errors=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            "--target",
            str(target),
            str(wheel),
        ],
        cwd=ROOT,
        check=True,
    )


def verify_legacy_wrapper(target: Path) -> None:
    sys.path.insert(0, str(target.resolve()))
    sys.modules.pop("edge_workspace_links", None)
    module = import_module("edge_workspace_links")

    if not Path(module.__file__).resolve().is_relative_to(target.resolve()):
        raise AssertionError(f"Legacy wrapper was not imported from the installed wheel: {module.__file__}")

    rows = module.build_export_rows(
        "workspace.edge",
        [module.LinkRecord(url="https://tab.example", title="Tab")],
        [module.LinkRecord(url="https://favorite.example", title="Favorite")],
        "both",
        set(),
    )
    if not isinstance(rows[0], dict):
        raise AssertionError(f"Legacy wrapper returned unexpected row shape: {type(rows[0])!r}")

    summary = module.build_summary_rows(
        [Path("workspace.edge")],
        [
            module.FileResult(
                workspace_file="workspace.edge",
                status="ok",
                extracted_tab_count=1,
                extracted_favorite_count=1,
                exported_link_count=2,
            )
        ],
        rows,
    )
    if ("unique_exported_urls", 2) not in summary:
        raise AssertionError(f"Legacy summary rows were not preserved: {summary!r}")


def verify_cli_smoke(target: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "smoke_packaged_cli.py"),
            "--python-module",
            "edge_workspace_links",
            "--python-path",
            str(target),
        ],
        cwd=ROOT,
        check=True,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a built wheel into an isolated target and verify wrapper and CLI behavior."
    )
    parser.add_argument("--wheel", required=True, help="Path to the built wheel file.")
    parser.add_argument(
        "--target",
        default=str(ROOT / "wheel-smoke"),
        help="Installation target directory (default: ./wheel-smoke).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    wheel = Path(args.wheel).resolve()
    target = Path(args.target).resolve()

    install_wheel(wheel, target)
    verify_legacy_wrapper(target)
    verify_cli_smoke(target)

    print(f"Wheel smoke test passed for {wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
