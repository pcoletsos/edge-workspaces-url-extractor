# GEMINI.md

Read `CONTRIBUTING.md` first. It is the canonical workflow contract for this
repository.

Use `AGENTS.md` for the repo map, and treat GitHub as the live source of truth
for issues, milestones, CI, releases, and branch protection.

Shared agent execution protocol: see the `Agent execution protocol` section in `AGENTS.md`.

## CI Action Failure & Guardrail Rules

- On any CI/Action failure, extract logs via `gh run view <run_id> --log-failed`, identify root cause, and implement pre-flight prevention.
- Run `python3 .github/scripts/validate_contribution_guardrails.py` locally to verify PR metadata prior to pushing branches.
