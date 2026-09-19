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

## Mandatory CI and Contribution Rules

### CI failure triage

When any CI check fails on a pull request:

1. pull the failed step logs first with `gh run view <run_id> --log-failed`
2. diagnose the root cause from those logs before changing anything
3. fix, run the relevant local quality gates, and push the fix

Do not guess at CI failures from check names or status icons alone.

### Pre-flight contribution guardrails

Before opening or updating a pull request, validate the contribution
guardrails locally:

1. branch name matches `<actor>/<type>/<scope>/<task>-<id>` using only the
   allowed segment values from `CONTRIBUTING.md`
2. PR title uses `<type>(<scope>): <description>` with the same `type` and
   `scope` as the branch
3. PR body links the branch issue with `Closes #<number>`

Verify with the guardrail script against a synthetic PR event payload:

```powershell
python .github\scripts\validate_contribution_guardrails.py --event-path .\guardrails-event.json
```

```json
{
  "pull_request": {
    "head": { "ref": "local/docs/docs/ci-triage-guardrails-33" },
    "title": "docs(docs): add action failure triage and contribution guardrail rules",
    "body": "Closes #33"
  }
}
```

Adjust the payload to the current branch, PR title, and body.

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
