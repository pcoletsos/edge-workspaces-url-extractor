from __future__ import annotations

from parity.fixture_builder import load_cases, write_case_file

import edge_workspace_links as mod


def export_view(rows):
    payload = []
    for row in rows:
        if isinstance(row, dict):
            payload.append(
                {
                    "source": row["source"],
                    "url": row["url"],
                    "title": row["title"],
                }
            )
            continue
        payload.append({"source": row.source, "url": row.url, "title": row.title})
    return payload


def link_view(links):
    return [{"url": link.url, "title": link.title} for link in links]


def test_python_parity_cases_match_expected_outputs(tmp_path):
    cases = load_cases()

    for case in cases:
        edge_path = write_case_file(case, tmp_path)

        file_result, both_rows = mod.process_edge_file(edge_path, "both", set())
        _, tab_rows = mod.process_edge_file(edge_path, "tabs", set())
        _, favorite_rows = mod.process_edge_file(edge_path, "favorites", set())
        _, filtered_rows = mod.process_edge_file(edge_path, "both", mod.INTERNAL_SCHEMES)

        payload_scan = mod.scan_gzip_payloads(edge_path.read_bytes())
        diagnostics = mod.extract_workspace_data(payload_scan.payloads)

        assert file_result.status == case["expected"]["status"]
        assert link_view(diagnostics.tabs) == case["expected"]["tabs"]
        assert link_view(diagnostics.favorites) == case["expected"]["favorites"]
        assert export_view(both_rows) == case["expected"]["exports"]["both"]
        assert export_view(tab_rows) == case["expected"]["exports"]["tabs"]
        assert export_view(favorite_rows) == case["expected"]["exports"]["favorites"]
        assert export_view(filtered_rows) == case["expected"]["exports"]["exclude_internal"]
