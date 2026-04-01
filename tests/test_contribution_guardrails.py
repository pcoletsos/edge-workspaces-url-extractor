from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / ".github" / "scripts" / "validate_contribution_guardrails.py"
)
SPEC = importlib.util.spec_from_file_location("validate_contribution_guardrails", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_parse_branch_accepts_canonical_branch() -> None:
    branch = MODULE.parse_branch("codex/chore/shared/contribution-os-28")

    assert branch.actor == "codex"
    assert branch.change_type == "chore"
    assert branch.scope == "shared"
    assert branch.task == "contribution-os"
    assert branch.issue == 28


def test_parse_branch_rejects_noncanonical_branch() -> None:
    with pytest.raises(MODULE.GuardrailError):
        MODULE.parse_branch("issue-28-contribution-os")


def test_validate_event_accepts_linked_issue_and_matching_title() -> None:
    event = {
        "pull_request": {
            "head": {"ref": "codex/chore/shared/contribution-os-28"},
            "title": "chore(shared): adopt repo contribution operating system",
            "body": "Closes #28",
        }
    }

    validated = MODULE.validate_event(event)

    assert validated.issue == 28


def test_validate_event_rejects_missing_issue_link() -> None:
    event = {
        "pull_request": {
            "head": {"ref": "codex/chore/shared/contribution-os-28"},
            "title": "chore(shared): adopt repo contribution operating system",
            "body": "Tracked in backlog",
        }
    }

    with pytest.raises(MODULE.GuardrailError):
        MODULE.validate_event(event)


def test_validate_pr_title_rejects_scope_mismatch() -> None:
    branch = MODULE.parse_branch("codex/chore/shared/contribution-os-28")

    with pytest.raises(MODULE.GuardrailError):
        MODULE.validate_pr_title("chore(cli): adopt repo contribution operating system", branch)
