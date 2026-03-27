#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_RELEASE_DIR = REPO_ROOT / "gui" / "flutter_app" / "build" / "windows" / "x64" / "runner" / "Release"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "dist" / "edge-workspace-links-ui-windows"
DEFAULT_ZIP_PATH = REPO_ROOT / "dist" / "edge-workspace-links-ui-windows.zip"
LAUNCHER_NAME = "edge_workspace_links_ui.exe"
REQUIRED_ENTRIES = (
    LAUNCHER_NAME,
    "edge-workspace-links-gui-backend.exe",
    "flutter_windows.dll",
    "data",
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the built Windows Flutter desktop UI into a clean distributable folder and zip."
    )
    parser.add_argument(
        "--release-dir",
        default=str(DEFAULT_RELEASE_DIR),
        help="Path to the built Windows Flutter release directory.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to write the clean UI bundle into.",
    )
    parser.add_argument(
        "--zip-path",
        default=str(DEFAULT_ZIP_PATH),
        help="Zip file to create from the copied bundle.",
    )
    return parser.parse_args(argv)


def validate_paths(release_dir: Path, output_dir: Path, zip_path: Path) -> None:
    if not release_dir.is_dir():
        raise FileNotFoundError(f"Windows UI release directory was not found: {release_dir}")

    missing = [name for name in REQUIRED_ENTRIES if not (release_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Windows UI release directory is missing required entries: "
            + ", ".join(sorted(missing))
        )

    release_dir_resolved = release_dir.resolve()
    output_dir_resolved = output_dir.resolve()
    zip_path_resolved = zip_path.resolve()

    if output_dir_resolved == release_dir_resolved or output_dir_resolved.is_relative_to(release_dir_resolved):
        raise ValueError("Output directory must not be the release directory or nested inside it.")

    if zip_path_resolved.is_relative_to(output_dir_resolved):
        raise ValueError("Zip path must not be placed inside the output directory.")


def copy_release_tree(release_dir: Path, output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(release_dir, output_dir)


def write_zip_archive(output_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(output_dir))


def package_bundle(release_dir: Path, output_dir: Path, zip_path: Path) -> tuple[Path, Path, Path]:
    validate_paths(release_dir, output_dir, zip_path)
    copy_release_tree(release_dir, output_dir)
    write_zip_archive(output_dir, zip_path)
    return output_dir, zip_path, output_dir / LAUNCHER_NAME


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    release_dir = Path(args.release_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    zip_path = Path(args.zip_path).resolve()

    try:
        bundle_dir, archive_path, launcher_path = package_bundle(release_dir, output_dir, zip_path)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Packaged Windows UI bundle: {bundle_dir}")
    print(f"Launcher: {launcher_path}")
    print(f"Archive: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
