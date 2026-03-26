# Decision Log

This file stores durable repository decisions.
Add entries for changes to workflow, architecture, release policy, compatibility policy, or roadmap direction.
Do not use this file for temporary notes or step-by-step task progress.

## ADM-001: Work Must Start From an Issue and Milestone

- Date: 2026-03-26
- Status: accepted

Decision:

New implementation work must start from an existing GitHub issue when possible.
If the request does not already have an issue, create one.
That issue must be assigned to an existing milestone when a suitable one exists.
If no suitable milestone exists, create a new milestone before implementation starts.

Rationale:

- Keeps requests traceable
- Lets future agents find prior context quickly
- Prevents feature work from bypassing planning and roadmap grouping

## ADM-002: All Implementation Work Uses Branches and Pull Requests

- Date: 2026-03-26
- Status: accepted

Decision:

Agents must create a dedicated branch before implementation starts.
Issue-specific work should use `issue-<number>-<short-slug>`.
Milestone-wide work may use `milestone-<short-slug>` when no single issue is sufficient.
When implementation is complete, the agent should open a pull request, link the tracked issue, and merge through the PR flow instead of committing directly to a long-lived branch.

Rationale:

- Preserves reviewability
- Makes partial work safer to resume
- Keeps issue history, code changes, and merge decisions connected

## ADM-003: Python Remains the Shipped Implementation

- Date: 2026-03-26
- Status: accepted

Decision:

The repository continues to ship the Python implementation as the production tool.
The Rust code under `rust/edge-workspace-links-rs/` remains a parity-checked prototype and benchmark baseline, not an approved replacement.

Rationale:

- The measured Rust speedup is incremental, not transformative
- A full migration would still require workbook, packaging, and release parity
- The current Python implementation is already fast enough for the evaluated corpus

Reference:

- `docs/rust-evaluation.md`

## ADM-004: Agent Memory Lives in the Repository

- Date: 2026-03-26
- Status: accepted

Decision:

Repository context, durable decisions, and rolling work state must be stored in versioned repo documents:

- `AGENTS.md`
- `docs/agent-memory/repo-overview.md`
- `docs/agent-memory/decision-log.md`
- `docs/agent-memory/work-log.md`

Rationale:

- Lets a new agent resume work without relying on chat history
- Makes process changes reviewable
- Keeps project memory close to the code it governs

## ADM-005: Cross-Platform Desktop UI Work Uses Flutter First

- Date: 2026-03-26
- Status: accepted

Decision:

Issue `#21` will proceed with Flutter as the desktop UI track for Windows, macOS, and Linux.
The extraction and reporting backend remains Python initially through a JSON-based GUI contract instead of a backend rewrite.

Rationale:

- The roadmap goal is a highly modern desktop UI that can span multiple operating systems
- Flutter gives one visual system across supported desktop targets
- Keeping the existing Python backend avoids coupling the UI decision to a premature language migration

Reference:

- `docs/flutter-ui-evaluation.md`

## ADM-006: Native Path Picking Uses Platform Channels, Not Flutter Picker Plugins

- Date: 2026-03-26
- Status: accepted

Decision:

The Flutter desktop prototype uses small native runner integrations on Windows, macOS, and Linux for file and folder selection.
Do not make native path browsing depend on Flutter picker plugins for the baseline desktop workflow.

Rationale:

- Native path navigation is mandatory for the desktop UX
- Direct platform channels avoid extra plugin and symlink/tooling friction during local desktop development
- The approach keeps manual path entry available as a fallback while preserving native dialogs

Reference:

- `gui/flutter_app/windows/runner/flutter_window.cpp`
- `gui/flutter_app/macos/Runner/MainFlutterWindow.swift`
- `gui/flutter_app/linux/runner/my_application.cc`
