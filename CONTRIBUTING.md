# Contributing to Edge Workspaces URL Extractor

`CONTRIBUTING.md` is the canonical workflow contract for this repository.
Agent-specific files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and
`.github/copilot-instructions.md` point here instead of redefining the process.

## Source of Truth

- GitHub is the live source of truth for issues, milestones, pull requests,
  branch protection, CI runs, and releases.
- `README.md` is the user-facing product and usage guide.
- `docs/agent-memory/repo-overview.md` is the repo map.
- `docs/agent-memory/decision-log.md` records durable workflow or architecture
  decisions.
- `docs/agent-memory/work-log.md` is the rolling handoff log.

If a number or milestone in markdown differs from GitHub, GitHub wins.

## Non-Trivial Work Is Issue-First

Treat the following as non-trivial and route them through a GitHub issue
before implementation:

- parser, CLI, UI, release, docs, or shared workflow changes
- packaging, smoke tests, CI, or release automation
- repo governance, contribution workflow, or branch protection changes
- refactors and tooling work that affect delivery

Use a GitHub issue for every normal change. Maintainer overrides are reserved
for exceptional admin or emergency work.

### Required Workflow

1. Search GitHub issues and milestones first.
2. Reuse an existing issue if it already covers the work.
3. If no matching issue exists, create one before implementation starts.
4. Every non-trivial issue must have a milestone:
   - Use an existing thematic milestone when it clearly fits.
   - Use `Backlog` when no thematic milestone fits.
   - Create a new milestone only for a genuine new workstream or roadmap bucket.
5. Create a work branch from `main` using the canonical naming scheme.
6. Implement the change and run the relevant validation.
7. Open a pull request with the required template fields completed.
8. Merge with squash as the normal path. Rebase is a maintainer-only exception.

Do not implement non-trivial work directly on `main`.

## Quick Agent Prompts

These are shorthand prompts you can use with coding agents. They are not shell
commands.

- `start <task>`: reuse or create the GitHub issue, ensure it has a milestone,
  create a correctly named branch, and begin implementation.
- `record it`: commit the current changes on the current branch.
- `publish it`: push the current branch to `origin`.
- `propose it`: open a PR for the current branch or update the existing PR.
- `land it`: squash-merge the current PR after required checks and approval.
- `ship it`: `record it` + `publish it` + `propose it`.
- `finish it`: `record it` + `publish it` + `propose it` + `land it`.
- `finish it for #<id>`: canonical full-flow shorthand tied to a GitHub issue.

## Branch Naming

Canonical branch format:

```text
<actor>/<type>/<scope>/<task>-<id>
```

Rules:

- all segments must be lowercase and kebab-case
- `<id>` is mandatory
- keep names concise
- use `shared` only when no single domain clearly dominates the work

Allowed values:

| Segment | Allowed values |
|---|---|
| `actor` | `codex`, `claude`, `copilot`, `gemini`, `local`, `human` |
| `type` | `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf` |
| `scope` | `cli`, `ui`, `parser`, `release`, `docs`, `shared` |

Examples:

- `codex/chore/shared/contribution-os-28`
- `human/fix/cli/path-normalization-12`

## Commits and Pull Requests

Intermediate commit messages are not a blocking policy surface.

The enforced Conventional Commit format applies to:

- the pull request title
- the final squash commit message

Required format:

```text
<type>(<scope>): <description>
```

Allowed `type` and `scope` values match the branch naming tables above.

### PR Requirements

Every normal PR must include:

- a linked issue
- a short summary of what changed and why
- the affected scope
- the validation that was run

Conditionally required:

- screenshots or preview evidence for visible UI changes
- release impact for packaging or publication changes
- docs impact when behavior or contributor flow changed
- rollback notes for risky or production-impacting changes

## Merge and Release Policy

- `main` is the integration branch.
- Squash merge is the normal and documented merge path.
- Rebase merge remains available only as a maintainer exception.
- Merge commits should stay disabled.
- Official releases are built and published by GitHub Actions.
- Plain pushes to `main` do not publish releases.

## Required Checks

The branch protection baseline is:

- `Contribution guardrails`
- `test (ubuntu-latest, 3.10)`
- `test (ubuntu-latest, 3.12)`
- `test (windows-latest, 3.10)`
- `test (windows-latest, 3.12)`
- `wheel-smoke`
- `pyinstaller-smoke`
- `rust-parity`
- `flutter-desktop (windows)`
- `flutter-desktop (linux)`
- `flutter-desktop (macos)`

If GitHub branch protection disagrees with this file, GitHub wins.

## Repo-Specific Engineering Constraints

- Processing is local-only; do not introduce network dependencies into the
  extraction path.
- Python remains the shipped implementation.
- The packaged GUI backend executable is the release-style desktop contract.
- GitHub issues and milestones drive planning; `Backlog` is the fallback bucket.
- `@pcoletsos` is the initial sole code owner.

## Useful Commands

```bash
# Parser and CLI regression suite
python -m pytest tests/test_parity_cases.py -q
python -m pytest tests/test_edge_workspace_links.py tests/test_cli_quality_gates.py tests/test_gui_backend.py tests/test_gui_backend_smoke.py -q

# Packaging smoke
python -m build --wheel
python scripts/check_wheel_install.py --wheel <wheel-path>
python -m PyInstaller --noconfirm edge-workspace-links.spec
python scripts/smoke_packaged_cli.py --exe dist\edge-workspace-links.exe
python -m PyInstaller --noconfirm edge-workspace-links-gui-backend.spec
python scripts/smoke_gui_backend.py --backend-exe dist\edge-workspace-links-gui-backend.exe

# Live GitHub state
gh issue list --repo pcoletsos/edge-workspaces-url-extractor --state open
gh api repos/pcoletsos/edge-workspaces-url-extractor/milestones --paginate
```
