from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.helpers import PROJECT_ROOT


def test_gui_backend_smoke_script_runs_against_module(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "smoke_gui_backend.py"),
            "--python-module",
            "edge_workspace_links_app.gui_backend",
            "--python-path",
            str(PROJECT_ROOT / "src"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Backend smoke test passed" in result.stdout
