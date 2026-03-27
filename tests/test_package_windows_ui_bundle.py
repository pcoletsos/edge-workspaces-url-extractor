from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "package_windows_ui_bundle.py"


def create_release_tree(root: Path, *, include_backend: bool = True) -> Path:
    release_dir = root / "Release"
    (release_dir / "data" / "flutter_assets").mkdir(parents=True)
    (release_dir / "edge_workspace_links_ui.exe").write_text("ui", encoding="utf-8")
    (release_dir / "flutter_windows.dll").write_text("dll", encoding="utf-8")
    (release_dir / "data" / "icudtl.dat").write_text("icu", encoding="utf-8")
    (release_dir / "data" / "flutter_assets" / "AssetManifest.bin").write_text(
        "asset-manifest",
        encoding="utf-8",
    )
    if include_backend:
        (release_dir / "edge-workspace-links-gui-backend.exe").write_text(
            "backend",
            encoding="utf-8",
        )
    return release_dir


def test_package_windows_ui_bundle_copies_release_tree_and_writes_zip(tmp_path: Path) -> None:
    release_dir = create_release_tree(tmp_path)
    output_dir = tmp_path / "dist" / "edge-workspace-links-ui-windows"
    zip_path = tmp_path / "dist" / "edge-workspace-links-ui-windows.zip"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--release-dir",
            str(release_dir),
            "--output-dir",
            str(output_dir),
            "--zip-path",
            str(zip_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert (output_dir / "edge_workspace_links_ui.exe").is_file()
    assert (output_dir / "edge-workspace-links-gui-backend.exe").is_file()
    assert (output_dir / "flutter_windows.dll").is_file()
    assert (output_dir / "data" / "flutter_assets" / "AssetManifest.bin").is_file()
    assert zip_path.is_file()

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())

    assert "edge_workspace_links_ui.exe" in names
    assert "edge-workspace-links-gui-backend.exe" in names
    assert "flutter_windows.dll" in names
    assert "data/flutter_assets/AssetManifest.bin" in names


def test_package_windows_ui_bundle_fails_when_required_backend_is_missing(tmp_path: Path) -> None:
    release_dir = create_release_tree(tmp_path, include_backend=False)
    output_dir = tmp_path / "dist" / "edge-workspace-links-ui-windows"
    zip_path = tmp_path / "dist" / "edge-workspace-links-ui-windows.zip"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--release-dir",
            str(release_dir),
            "--output-dir",
            str(output_dir),
            "--zip-path",
            str(zip_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "edge-workspace-links-gui-backend.exe" in completed.stderr
