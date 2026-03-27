#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TAG_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?$")


@dataclass(frozen=True, order=True)
class ReleaseVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> ReleaseVersion | None:
        match = TAG_RE.fullmatch(value.strip())
        if not match:
            return None
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch") or 0),
        )

    def bump(self, bump: str) -> ReleaseVersion:
        if bump == "patch":
            return ReleaseVersion(self.major, self.minor, self.patch + 1)
        if bump == "minor":
            return ReleaseVersion(self.major, self.minor + 1, 0)
        if bump == "major":
            return ReleaseVersion(self.major + 1, 0, 0)
        raise ValueError(f"Unsupported bump type: {bump}")

    @property
    def version(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def tag(self) -> str:
        return f"v{self.version}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute the next release version from existing Git tags."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    next_parser = subparsers.add_parser("next", help="Compute the next release version.")
    next_parser.add_argument(
        "--bump",
        choices=("patch", "minor", "major"),
        default="patch",
        help="Version component to increment.",
    )
    next_parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Explicit tag value to consider. When omitted, tags are read from git.",
    )

    return parser.parse_args(argv)


def load_tags(explicit_tags: list[str]) -> list[str]:
    if explicit_tags:
        return explicit_tags

    completed = subprocess.run(
        ["git", "tag", "--list"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Unable to list git tags.")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def select_latest_tag(tags: list[str]) -> tuple[str | None, ReleaseVersion]:
    parsed: list[tuple[ReleaseVersion, str]] = []
    for tag in tags:
        version = ReleaseVersion.parse(tag)
        if version is not None:
            parsed.append((version, tag))

    if not parsed:
        return None, ReleaseVersion(0, 0, 0)

    version, raw_tag = max(parsed, key=lambda item: item[0])
    return raw_tag, version


def next_release_payload(*, bump: str, tags: list[str]) -> dict[str, str]:
    latest_tag, latest_version = select_latest_tag(tags)
    next_version = latest_version.bump(bump)
    return {
        "latest_tag": latest_tag or "none",
        "version": next_version.version,
        "tag": next_version.tag,
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.command != "next":
        raise ValueError(f"Unsupported command: {args.command}")

    try:
        payload = next_release_payload(bump=args.bump, tags=load_tags(args.tag))
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
