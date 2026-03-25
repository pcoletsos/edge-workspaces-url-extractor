from __future__ import annotations

import pytest
from openpyxl import load_workbook

from tests.helpers import edge_bytes, workspace_document, write_edge_file


def test_decompress_payloads_and_extract_workspace_data(edge_workspace_links):
    first = workspace_document(
        tabs=[
            {"url": "https://example.com/a", "title": "Alpha"},
            {"url": "edge://settings", "title": "Internal"},
            {"url": "https://example.com/a", "title": "Alpha duplicate"},
        ],
        favorites=[
            {"url": "https://example.com/a", "title": "Alpha favorite"},
            {"url": "https://example.com/b", "title": "Bravo"},
        ],
    )
    second = workspace_document(
        tabs=[{"url": "https://example.com/c", "title": "Charlie"}],
        favorites=[{"url": "https://example.com/d", "title": "Delta"}],
    )
    blob = edge_bytes(first, first, second, prefix=b"noise", suffix=b"tail")

    payloads = edge_workspace_links.decompress_payloads(blob)
    tabs, favorites = edge_workspace_links.extract_workspace_data(payloads)

    assert len(payloads) == 2
    assert tabs == [
        {"url": "https://example.com/a", "title": "Alpha"},
        {"url": "edge://settings", "title": "Internal"},
        {"url": "https://example.com/a", "title": "Alpha duplicate"},
        {"url": "https://example.com/c", "title": "Charlie"},
    ]
    assert favorites == [
        {"url": "https://example.com/a", "title": "Alpha favorite"},
        {"url": "https://example.com/b", "title": "Bravo"},
        {"url": "https://example.com/d", "title": "Delta"},
    ]


def test_filter_links_excludes_explicit_schemes(edge_workspace_links):
    links = [
        {"url": "https://example.com", "title": "One"},
        {"url": "chrome://settings", "title": "Two"},
        {"url": "file:///tmp/test.txt", "title": "Three"},
    ]

    assert edge_workspace_links.filter_links(links, {"chrome", "file"}) == [
        {"url": "https://example.com", "title": "One"}
    ]


def test_main_exports_tabs_and_favorites_with_expected_dedupe(edge_workspace_links, tmp_path):
    edge_file = write_edge_file(
        tmp_path / "sample.edge",
        workspace_document(
            tabs=[
                {"url": "https://example.com/shared", "title": "Tab title"},
                {"url": "https://example.com/shared", "title": "Tab title duplicate"},
                {"url": "https://example.com/tab-only", "title": "Tab only"},
            ],
            favorites=[
                {"url": "https://example.com/shared", "title": "Favorite title"},
                {"url": "https://example.com/favorite-only", "title": "Favorite only"},
            ],
        ),
    )
    output = tmp_path / "out.xlsx"

    exit_code = edge_workspace_links.main(["--input", str(edge_file), "--output", str(output)])

    assert exit_code == 0
    workbook = load_workbook(output)
    assert workbook.sheetnames == ["Links", "Summary Report", "Per File Report"]

    links = workbook["Links"]
    assert [links.cell(row=1, column=idx).value for idx in range(1, 5)] == [
        "workspace_file",
        "source",
        "url",
        "title",
    ]
    assert [links.cell(row=2, column=idx).value for idx in range(1, 5)] == [
        "sample.edge",
        "favorite",
        "https://example.com/shared",
        "Favorite title",
    ]
    assert links["C2"].hyperlink.target == "https://example.com/shared"
    assert [links.cell(row=3, column=idx).value for idx in range(1, 5)] == [
        "sample.edge",
        "favorite",
        "https://example.com/favorite-only",
        "Favorite only",
    ]
    assert [links.cell(row=4, column=idx).value for idx in range(1, 5)] == [
        "sample.edge",
        "tab",
        "https://example.com/tab-only",
        "Tab only",
    ]

    summary = workbook["Summary Report"]
    rows = {
        summary.cell(row=row, column=1).value: summary.cell(row=row, column=2).value
        for row in range(2, summary.max_row + 1)
    }
    assert rows == {
        "files_found": 1,
        "files_with_any_links": 1,
        "files_with_tabs": 1,
        "files_with_favorites": 1,
        "tabs_total": 2,
        "favorites_total": 2,
        "links_total": 3,
        "unique_urls": 3,
    }

    per_file = workbook["Per File Report"]
    assert [per_file.cell(row=2, column=idx).value for idx in range(1, 5)] == [
        "sample.edge",
        2,
        2,
        3,
    ]


@pytest.mark.xfail(reason="M1 issue #1: workbook output still needs formula hardening", strict=False)
def test_write_output_neutralizes_formula_like_text(edge_workspace_links, tmp_path):
    output = tmp_path / "formula.xlsx"
    rows = [
        {
            "workspace_file": "=evil.edge",
            "source": "tab",
            "url": "=HYPERLINK(\"https://example.com\")",
            "title": "@malicious",
        }
    ]

    edge_workspace_links.write_output(
        rows,
        [("files_found", 1)],
        [{"workspace_file": "=evil.edge", "open_tab_count": 1, "favorite_count": 0, "links_written": 1}],
        str(output),
    )

    workbook = load_workbook(output)
    sheet = workbook["Links"]
    assert sheet["A2"].data_type == "s"
    assert sheet["A2"].value == "'=evil.edge"
    assert sheet["C2"].data_type == "s"
    assert sheet["C2"].value == '\'=HYPERLINK("https://example.com")'
    assert sheet["D2"].data_type == "s"
    assert sheet["D2"].value == "'@malicious"
