#!/usr/bin/env python3
"""Check new direct dependencies: they exist, are old enough, and are listed.

Every direct dependency in `pyproject.toml` must have a row in
`docs/dependencies.md`, must exist on PyPI, and its first release must be at
least 14 days old (typosquat cooling for newly added packages; routine
version updates are not gated). Makefile-pinned tools are out of scope: their
versions live beside the renovate annotation that updates them.

Usage: uv run python scripts/check_new_deps.py
"""

from __future__ import annotations

import re
import sys
import tomllib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
MIN_AGE_DAYS = 14
PYPI_TIMEOUT_SECONDS = 15


class PackageNotFound(Exception):
    """The package does not exist on the registry."""


def normalize_name(name: str) -> str:
    """Normalize a distribution name the way installers compare them."""
    return (
        re.split(r"[ ;\[<>=!~(\]]", name, maxsplit=1)[0]
        .strip()
        .lower()
        .replace("_", "-")
        .replace(".", "-")
    )


def direct_dependencies() -> list[str]:
    """Read direct dependency names from `pyproject.toml`."""
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    specs: list[str] = list(data["project"]["dependencies"])
    for group in data.get("dependency-groups", {}).values():
        specs.extend(item for item in group if isinstance(item, str))
    return sorted({normalize_name(spec) for spec in specs if normalize_name(spec)})


def ledger_names() -> set[str]:
    """Read first-column package names from the dependency ledger."""
    names: set[str] = set()
    ledger = ROOT / "docs" / "dependencies.md"
    for line in ledger.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
        if match:
            names.add(match.group(1).lower())
    return names


def fetch_metadata(name: str) -> dict:
    """Fetch a package's metadata from PyPI, or raise PackageNotFound."""
    response = httpx.get(f"https://pypi.org/pypi/{name}/json", timeout=PYPI_TIMEOUT_SECONDS)
    if response.status_code == 404:
        raise PackageNotFound(name)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise PackageNotFound(name)
    return data


def first_release_at(metadata: dict) -> datetime | None:
    """Return the earliest upload time across all releases, or None."""
    earliest: datetime | None = None
    releases = metadata.get("releases", {})
    if not isinstance(releases, dict):
        return None
    for files in releases.values():
        if not isinstance(files, list):
            continue
        for file in files:
            stamped = file.get("upload_time_iso_8601") if isinstance(file, dict) else None
            if not stamped:
                continue
            try:
                uploaded = datetime.fromisoformat(stamped)
            except ValueError:
                continue
            if uploaded.tzinfo is None:
                uploaded = uploaded.replace(tzinfo=UTC)
            if earliest is None or uploaded < earliest:
                earliest = uploaded
    return earliest


def check(
    names: list[str],
    ledger: set[str],
    fetch: Callable[[str], dict],
    now: datetime,
) -> list[str]:
    """Return one error per direct dependency that fails the checks."""
    errors: list[str] = []
    for name in names:
        if name not in ledger:
            errors.append(f"{name}: no row in docs/dependencies.md")
        try:
            metadata = fetch(name)
        except PackageNotFound:
            errors.append(f"{name}: not found on PyPI")
            continue
        first = first_release_at(metadata)
        if first is None:
            errors.append(f"{name}: no releases on PyPI")
        elif (now - first).days < MIN_AGE_DAYS:
            errors.append(f"{name}: first release is under {MIN_AGE_DAYS} days old")
    return errors


def main() -> int:
    """Check every direct dependency."""
    try:
        errors = check(direct_dependencies(), ledger_names(), fetch_metadata, datetime.now(UTC))
    except httpx.HTTPError as exc:
        print(f"PyPI request failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("new-dependency check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
