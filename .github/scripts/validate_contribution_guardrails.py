#!/usr/bin/env python3
"""Validate the repo contribution contract for pull requests."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BRANCH_RE = re.compile(
    r"^(?P<actor>codex|claude|copilot|gemini|local|human)/"
    r"(?P<type>feat|fix|refactor|chore|docs|test|perf)/"
    r"(?P<scope>cli|ui|parser|release|docs|shared)/"
    r"(?P<task>[a-z0-9]+(?:-[a-z0-9]+)*)-(?P<issue>\d+)$"
)
PR_TITLE_RE = re.compile(
    r"^(?P<type>feat|fix|refactor|chore|docs|test|perf)"
    r"\((?P<scope>cli|ui|parser|release|docs|shared)\): .+"
)
ISSUE_REF_RE = re.compile(r"(?i)\b(?:closes|fixes|resolves)\s+#(?P<issue>\d+)\b")


@dataclass(frozen=True)
class BranchInfo:
    actor: str
    change_type: str
    scope: str
    task: str
    issue: int


class GuardrailError(RuntimeError):
    pass


def load_event(event_path: Path | None) -> dict[str, Any]:
    raw_path = event_path or os.environ.get("GITHUB_EVENT_PATH")
    if not raw_path:
        raise GuardrailError("GitHub event payload was not found.")
    resolved = Path(raw_path)
    if not resolved.exists():
        raise GuardrailError(f"GitHub event payload was not found at {resolved}.")
    return json.loads(resolved.read_text(encoding="utf-8"))


def parse_branch(branch: str) -> BranchInfo:
    match = BRANCH_RE.match(branch)
    if not match:
        raise GuardrailError(
            "Branch name must follow <actor>/<type>/<scope>/<task>-<id>, "
            "for example codex/chore/shared/contribution-os-28."
        )
    return BranchInfo(
        actor=match.group("actor"),
        change_type=match.group("type"),
        scope=match.group("scope"),
        task=match.group("task"),
        issue=int(match.group("issue")),
    )


def get_pull_request_payload(event: dict[str, Any]) -> dict[str, Any]:
    pr = event.get("pull_request")
    if not pr:
        raise GuardrailError("This workflow only validates pull request events.")
    return pr


def validate_pr_title(title: str, branch: BranchInfo) -> None:
    match = PR_TITLE_RE.match(title or "")
    if not match:
        raise GuardrailError(
            "PR title must use Conventional Commit format: "
            f"{branch.change_type}({branch.scope}): description"
        )
    if match.group("type") != branch.change_type or match.group("scope") != branch.scope:
        raise GuardrailError(
            "PR title type and scope must match the branch name. "
            f"Expected {branch.change_type}({branch.scope})."
        )


def validate_issue_link(body: str, issue_number: int) -> None:
    match = ISSUE_REF_RE.search(body or "")
    if not match:
        raise GuardrailError(f"PR body must link the issue with 'Closes #{issue_number}'.")
    referenced_issue = int(match.group("issue"))
    if referenced_issue != issue_number:
        raise GuardrailError(
            f"PR body links #{referenced_issue}, but the branch is scoped to #{issue_number}."
        )


def validate_event(event: dict[str, Any]) -> BranchInfo:
    pr = get_pull_request_payload(event)
    branch = parse_branch(pr["head"]["ref"])
    validate_pr_title(pr.get("title", ""), branch)
    validate_issue_link(pr.get("body", ""), branch.issue)
    return branch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event-path",
        type=Path,
        default=None,
        help="Path to the GitHub event payload JSON file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        event = load_event(args.event_path)
        branch = validate_event(event)
    except GuardrailError as exc:
        print(f"Contribution guardrails failed: {exc}", file=sys.stderr)
        return 1
    print(
        "Contribution guardrails passed for "
        f"{branch.actor}/{branch.change_type}/{branch.scope}/{branch.task}-{branch.issue}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
