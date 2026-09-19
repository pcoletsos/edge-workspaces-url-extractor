# GEMINI.md

Read `CONTRIBUTING.md` first. It is the canonical workflow contract for this
repository.

Use `AGENTS.md` for the repo map, and treat GitHub as the live source of truth
for issues, milestones, CI, releases, and branch protection.

Shared agent execution protocol: see the `Agent execution protocol` section in `AGENTS.md`.

## Mandatory CI and Contribution Rules

- CI failure triage: extract failed step logs with
  `gh run view <run_id> --log-failed` and diagnose the root cause before
  changing anything.
- Pre-flight contribution guardrails: before opening or updating a PR,
  validate the branch name, PR title, and issue linkage against
  `CONTRIBUTING.md` with the guardrail script and a synthetic PR event
  payload. See the matching section in `AGENTS.md`.
