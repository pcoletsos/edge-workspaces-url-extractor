from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "release_version.py"


def run_release_version(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_next_patch_version_treats_two_part_tags_as_zero_patch() -> None:
    completed = run_release_version(
        "next",
        "--bump",
        "patch",
        "--tag",
        "v0.1",
        "--tag",
        "v0.3",
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload == {
        "latest_tag": "v0.3",
        "version": "0.3.1",
        "tag": "v0.3.1",
    }


def test_next_minor_version_advances_and_resets_patch() -> None:
    completed = run_release_version(
        "next",
        "--bump",
        "minor",
        "--tag",
        "v0.3.1",
        "--tag",
        "v0.2.9",
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload == {
        "latest_tag": "v0.3.1",
        "version": "0.4.0",
        "tag": "v0.4.0",
    }


def test_next_major_version_advances_from_latest_semver_tag() -> None:
    completed = run_release_version(
        "next",
        "--bump",
        "major",
        "--tag",
        "v0.3.1",
        "--tag",
        "v0.10.2",
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload == {
        "latest_tag": "v0.10.2",
        "version": "1.0.0",
        "tag": "v1.0.0",
    }


def test_next_version_ignores_non_semver_tags() -> None:
    completed = run_release_version(
        "next",
        "--bump",
        "patch",
        "--tag",
        "draft-release",
        "--tag",
        "v0.3",
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload == {
        "latest_tag": "v0.3",
        "version": "0.3.1",
        "tag": "v0.3.1",
    }


def test_next_version_starts_from_zero_when_no_semver_tags_exist() -> None:
    completed = run_release_version(
        "next",
        "--bump",
        "patch",
        "--tag",
        "draft-release",
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload == {
        "latest_tag": "none",
        "version": "0.0.1",
        "tag": "v0.0.1",
    }
