# AGENTS

Read `CONTRIBUTING.md` first. It is the canonical workflow contract for this
repository.

## Repo Map

- `README.md`: user-facing product and usage guide
- `docs/agent-memory/repo-overview.md`: repo map and stable context
- `docs/agent-memory/decision-log.md`: durable architecture and workflow decisions
- `docs/agent-memory/work-log.md`: rolling handoff log

## Live Source of Truth

GitHub is the live source of truth for:

- issues and milestones
- CI, release, and smoke-test runs
- releases and branch protection

If a number or milestone in markdown does not match GitHub, GitHub wins.

## Before You Edit

For any non-trivial task:

1. search for an existing GitHub issue
2. reuse it or create a new one
3. ensure the issue has a milestone
4. use `Backlog` when no thematic milestone fits
5. create a branch before editing
6. follow the canonical branch format from `CONTRIBUTING.md`

Do not implement non-trivial work directly on `main`.

## Working Rules

- Check `git status --short` before editing anything.
- Do not overwrite or revert unrelated user changes.
- Keep user-facing behavior, tests, and docs aligned in the same branch.
- Use the quality gates in `README.md` and `.github/workflows/ci.yml` for the
  area you touched.

## Durable Memory

Keep these files current when the workflow or repo posture changes:

- `docs/agent-memory/repo-overview.md`
- `docs/agent-memory/decision-log.md`
- `docs/agent-memory/work-log.md`

## Agent execution protocol

Agent-managed issues on the owner-scope GitHub Project #3 ("Portfolio Workspace and
Site Readiness") follow the shared **agent execution protocol**: the `Agent State`
lifecycle (`Agent Todo → Agent Working → Agent Needs Input | Agent Review | Agent Done`),
idempotent receipt comments (`AGENT CLAIMED` / `AGENT BLOCKED` / `AGENT DONE`), and the
`needs-input` hard stop. Drive state with the receipt scripts, not ad-hoc project edits.

Canonical spec and tooling live in `koletsos-portfolio`:
- Protocol: https://github.com/pcoletsos/koletsos-portfolio/blob/main/docs/agent-execution-protocol.md
- Scripts: https://github.com/pcoletsos/koletsos-portfolio/tree/main/scripts
  (`github-agent-receipt.ps1`, `github-agent-needs-input.ps1`, `github-agent-queue.ps1`)
