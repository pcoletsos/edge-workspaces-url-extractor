from __future__ import annotations

import json
import sys
from pathlib import Path

from tests.helpers import PROJECT_ROOT, write_edge_file, workspace_document

sys.path.insert(0, str(PROJECT_ROOT / "src"))
import edge_workspace_links_app.gui_backend as gui_backend


def read_payload(capsys) -> dict[str, object]:
    stdout = capsys.readouterr().out
    return json.loads(stdout)


def test_gui_backend_returns_machine_readable_success_payload(tmp_path: Path, capsys) -> None:
    write_edge_file(
        tmp_path / "workspace.edge",
        workspace_document(
            tabs=[
                {"url": "edge://settings", "title": "Internal"},
                {"url": "https://example.com/tab-only", "title": "Tab only"},
            ],
            favorites=[{"url": "https://example.com/favorite-only", "title": "Favorite only"}],
        ),
    )

    exit_code = gui_backend.main(
        [
            "--input",
            str(tmp_path),
            "--exclude-internal",
            "--sort",
        ]
    )

    payload = read_payload(capsys)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["code"] == "ok"
    assert payload["result"]["summary"]["extracted_tabs_total"] == 2
    assert payload["result"]["summary"]["exported_links_total"] == 2
    assert [row["url"] for row in payload["result"]["links"]] == [
        "https://example.com/favorite-only",
        "https://example.com/tab-only",
    ]


def test_gui_backend_returns_error_payload_for_missing_input(capsys) -> None:
    exit_code = gui_backend.main(["--input", "missing-input"])

    payload = read_payload(capsys)

    assert exit_code == 2
    assert payload == {
        "status": "error",
        "code": "input_not_found",
        "message": "Input path not found: missing-input",
        "notices": [],
        "result": None,
    }


def test_gui_backend_returns_file_results_when_all_inputs_fail(tmp_path: Path, capsys) -> None:
    (tmp_path / "broken.edge").write_text("not a workspace", encoding="utf-8")

    exit_code = gui_backend.main(["--input", str(tmp_path)])

    payload = read_payload(capsys)

    assert exit_code == 1
    assert payload["status"] == "error"
    assert payload["code"] == "no_successful_workspaces"
    assert payload["result"]["summary"]["not_workspace_files"] == 1
    assert payload["result"]["files"][0]["status"] == "not_workspace"
    assert payload["notices"] == [
        "broken.edge: not_workspace - No gzip workspace payloads were found."
    ]
