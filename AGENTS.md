# AGENTS

## Purpose

This repository ships a local tool for extracting open tab URLs and favorites from Microsoft Edge Workspace `.edge` files.
The production implementation is Python and the project currently publishes a CLI plus a Windows executable.

## Read Order

Read these files before making changes:

1. `docs/agent-memory/repo-overview.md`
2. `docs/agent-memory/decision-log.md`
3. `docs/agent-memory/work-log.md`
4. `README.md`

## Mandatory Workflow

1. Start from a GitHub issue or milestone, not from an untracked request.
2. If a request arrives without an issue number, search for an existing matching issue first.
3. If no matching issue exists, create one under the best existing milestone.
4. If no suitable milestone exists, create a new milestone before implementation starts.
5. Create a dedicated branch before editing code.
6. Prefer issue branches named `issue-<number>-<short-slug>`.
7. Use `milestone-<short-slug>` only when the work is truly milestone-wide and not issue-specific.
8. Do not implement directly on `main` or any long-lived integration branch.
9. Update `docs/agent-memory/work-log.md` when work starts, when scope changes, and when work finishes.
10. Record durable architecture, process, or product decisions in `docs/agent-memory/decision-log.md`.
11. Open a pull request when implementation is ready, link the issue, and merge through the PR flow.

If GitHub access is unavailable, do not silently skip the issue and milestone steps. Ask for access or for the user to perform the missing GitHub action.

## Working Rules

- Check `git status --short` before editing anything. The worktree may contain in-flight changes from another task.
- Do not overwrite or revert unrelated user changes.
- Keep user-facing behavior, tests, and docs aligned in the same branch.
- Use the quality gates in `README.md` and `.github/workflows/ci.yml` for the area you touched.

## Durable Memory

- Repository context: `docs/agent-memory/repo-overview.md`
- Decision memo log: `docs/agent-memory/decision-log.md`
- Rolling task handoff log: `docs/agent-memory/work-log.md`

These files are the in-repo memory system for future agents. Keep them current.
