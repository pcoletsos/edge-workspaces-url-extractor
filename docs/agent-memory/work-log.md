# Work Log

This file is the rolling handoff log for future agents.
Append or update entries when work starts, when direction changes, and when a branch is ready for PR.
Keep entries factual and brief.

Recommended fields:

- Date
- Status
- Issue
- Milestone
- Branch
- Scope
- Files or areas touched
- Next step
- PR or merge reference

## 2026-03-27

- Status: issue_20_merged
- Issue: `#20` and `#21`
- Milestone: `M5` for `#20`, `M6` for `#21`
- Branch: `issue-20-release-grade-tests`, `issue-21-flutter-eval`
- Scope: split the previously stacked review flow, fix the installed-wheel smoke coverage bug found during review, merge `#20`, and restore `#21` to a draft PR against `main`
- Files or areas touched:
  - `#20` branch: `scripts/smoke_packaged_cli.py`, `src/edge_workspace_links.py`
  - `#21` branch: GitHub PR metadata and this work log entry
- Next step: continue `#21` from PR `#22`, focusing on the remaining packaged-backend release gap noted in `docs/flutter-ui-evaluation.md`
- PR or merge reference: PR `#23` merged into `main`; issue `#20` closed; PR `#22` retargeted back to `main`

## 2026-03-26

- Status: ready_for_pr
- Issue: `#20` and `#21`
- Milestone: `M5` for `#20`, `M6` for `#21`
- Branch: `issue-21-flutter-eval`
- Scope: stack `#20` release-grade validation work under `#21` Flutter desktop evaluation and prototype work
- Files or areas touched:
  - Release validation: `.github/workflows/ci.yml`, `README.md`, `scripts/check_wheel_install.py`, `scripts/smoke_packaged_cli.py`, `tests/test_cli_quality_gates.py`
  - GUI backend: `pyproject.toml`, `src/edge_workspace_links_app/__init__.py`, `src/edge_workspace_links_app/gui_backend.py`, `tests/test_gui_backend.py`
  - Flutter UI: `gui/flutter_app/`, `docs/flutter-ui-evaluation.md`
  - Repo process memory: `AGENTS.md`, `docs/agent-memory/`, `.github/PULL_REQUEST_TEMPLATE.md`
- Next step: push `issue-21-flutter-eval`, open a PR into `main`, and link both issues while noting that Windows was built locally and the macOS/Linux native picker code was added but not compiled on this Windows host
- PR or merge reference: pending

## 2026-03-26

- Status: completed
- Issue: repository-level evaluation work
- Milestone: `M4` per `docs/rust-evaluation.md`
- Branch: unknown from local repo state
- Scope: evaluate whether the Rust prototype should replace the shipped Python implementation
- Files or areas touched: `rust/edge-workspace-links-rs/`, `scripts/check_rust_parity.py`, `scripts/benchmark_rust_compare.py`, `docs/rust-evaluation.md`, `parity/`
- Next step: keep the Rust prototype as a research baseline only; do not plan a replacement migration unless future data changes the tradeoff
- PR or merge reference: see repository history for the merge that introduced `docs/rust-evaluation.md`
