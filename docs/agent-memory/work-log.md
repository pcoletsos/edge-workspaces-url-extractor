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

## 2026-04-01

- Status: ready_for_pr
- Issue: `#28`
- Milestone: `Backlog`
- Branch: `codex/chore/shared/contribution-os-28`
- Scope: adopt the repository contribution operating system with canonical docs, agent adapters, GitHub issue templates, guardrails, and branch-protection friendly checks
- Files or areas touched: `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/`, `README.md`, `docs/agent-memory/`
- Next step: open a PR for `#28` when ready; the branch already has the contribution guardrails, labels, and `main` protection in place
- PR or merge reference: pending

## 2026-03-27

- Status: in_progress
- Issue: `#25`
- Milestone: `M7`
- Branch: `issue-25-release-publish-fix`
- Scope: fix the first GitHub-hosted release run so the publish job creates the GitHub Release from a checked-out repository context after the build artifacts have already succeeded
- Files or areas touched: `.github/workflows/release.yml`, `docs/agent-memory/work-log.md`
- Next step: add the missing checkout step to `publish-release`, merge the fix, and rerun the `Release` workflow for `v0.3.1`
- PR or merge reference: pending

- Status: in_progress
- Issue: `#25`
- Milestone: `M7`
- Branch: `issue-25-github-release-automation`
- Scope: replace the local release packaging path with a GitHub-hosted release workflow that reruns quality gates, builds the Windows app assets in Actions, publishes GitHub Release assets, and increments release versions from prior tags
- Files or areas touched: `.github/workflows/`, `scripts/`, `tests/`, `README.md`, `gui/flutter_app/README.md`, `docs/agent-memory/`
- Next step: add reusable CI support, implement the release/versioning workflow and scripts, update release docs and durable memory, then validate the non-build script coverage locally
- PR or merge reference: pending

- Status: ready_for_pr
- Issue: `#25`
- Milestone: `M7`
- Branch: `issue-25-github-release-automation`
- Scope: made GitHub Actions the official release path by adding a manual release workflow, reusable CI quality gates, release version computation from prior tags, and docs for the GitHub-hosted asset publishing flow
- Files or areas touched: `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `scripts/release_version.py`, `tests/test_release_version.py`, `pyproject.toml`, `README.md`, `gui/flutter_app/README.md`, `docs/agent-memory/`
- Next step: push the branch, let PR checks validate the reusable CI path, merge into `main`, then trigger the `Release` workflow to publish the first GitHub-hosted versioned assets
- PR or merge reference: pending

- Status: in_progress
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-ui-bundle`
- Scope: turn the ad-hoc local Windows UI bundle packaging step into a reproducible tracked repo workflow with a helper script, docs, and regression coverage
- Files or areas touched: `scripts/`, `tests/`, `README.md`, `gui/flutter_app/README.md`, `docs/agent-memory/work-log.md`
- Next step: add the packaging helper and test, document the clean bundle output path, then validate and publish the branch
- PR or merge reference: pending

- Status: completed
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-ui-bundle`
- Scope: added a reproducible Windows UI bundle helper, documented the clean bundle output path, and validated the packaged backend plus launcher path
- Files or areas touched: `scripts/package_windows_ui_bundle.py`, `tests/test_package_windows_ui_bundle.py`, `README.md`, `gui/flutter_app/README.md`, `docs/agent-memory/work-log.md`
- Next step: commit and publish `issue-21-ui-bundle`, open a PR into `main`, merge it, then delete the branch
- PR or merge reference: pending

- Status: in_progress
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-ui-bundle`
- Scope: assemble a cleaner local Windows desktop UI bundle folder from the Flutter release output so the packaged UI can be launched without navigating the deep build tree
- Files or areas touched: `dist/`, `docs/agent-memory/work-log.md`
- Next step: copy the Windows Flutter release payload into a dedicated `dist` bundle folder, smoke-check the UI launcher, then record the finished artifact path
- PR or merge reference: pending

- Status: completed
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-ui-bundle`
- Scope: packaged the existing Windows Flutter release output into a cleaner local bundle folder and zip for direct use outside the nested build tree
- Files or areas touched: `dist/edge-workspace-links-ui-windows/`, `dist/edge-workspace-links-ui-windows.zip`, `docs/agent-memory/work-log.md`
- Next step: use `dist\edge-workspace-links-ui-windows\edge_workspace_links_ui.exe` as the desktop launcher or distribute the zip as the local Windows UI bundle
- PR or merge reference: local artifact only; no PR opened

- Status: ready_for_pr
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-flutter-eval`
- Scope: address pre-merge review findings by restoring clean Flutter dev-build fallback when the packaged backend artifact is absent and correcting the preview badge tone for normal `tab` and `favorite` rows
- Files or areas touched: `gui/flutter_app/windows/runner/CMakeLists.txt`, `gui/flutter_app/linux/CMakeLists.txt`, `gui/flutter_app/linux/runner/CMakeLists.txt`, `gui/flutter_app/macos/Runner.xcodeproj/project.pbxproj`, `gui/flutter_app/lib/features/run_analysis/run_analysis_page.dart`, `docs/agent-memory/work-log.md`
- Next step: push the review-fix commit, let PR `#22` checks rerun, then merge if the PR stays clean
- PR or merge reference: PR `#22`

- Status: ready_for_pr
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-flutter-eval`
- Scope: finish packaged GUI backend integration for Flutter desktop builds across Windows, Linux, and macOS, and add OS-native GitHub Actions verification for those bundle paths
- Files or areas touched: `.github/workflows/ci.yml`, `README.md`, `docs/flutter-ui-evaluation.md`, `docs/agent-memory/`, `edge-workspace-links-gui-backend.spec`, `scripts/smoke_gui_backend.py`, `tests/test_gui_backend_smoke.py`, `gui/flutter_app/lib/services/backend_runner.dart`, `gui/flutter_app/lib/features/run_analysis/run_analysis_page.dart`, `gui/flutter_app/windows/runner/CMakeLists.txt`, `gui/flutter_app/linux/CMakeLists.txt`, `gui/flutter_app/linux/runner/CMakeLists.txt`, `gui/flutter_app/macos/Runner.xcodeproj/project.pbxproj`
- Next step: push the refreshed `issue-21-flutter-eval` branch, keep PR `#22` in draft until reviewers are satisfied with the desktop packaging scope, and use the new native CI jobs as the merge gate for Windows, Linux, and macOS bundle verification
- PR or merge reference: PR `#22` draft

- Status: ready_for_pr
- Issue: `#21`
- Milestone: `M6`
- Branch: `issue-21-flutter-eval`
- Scope: add the packaged GUI backend artifact and JSON smoke tooling for all desktop OS builds
- Files or areas touched: `edge-workspace-links-gui-backend.spec`, `scripts/smoke_gui_backend.py`, `src/edge_workspace_links_app/gui_backend.py`, `tests/test_gui_backend_smoke.py`
- Next step: wire this backend artifact into the Flutter desktop bundles and CI in a follow-up slice
- PR or merge reference: PR `#22`

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
