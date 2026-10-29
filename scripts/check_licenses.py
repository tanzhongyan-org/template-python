#!/usr/bin/env python3
"""Fail on copyleft or unknown licences in the runtime closure.

Dev-only tools are exempt: only the runtime dependencies from
`pyproject.toml` plus their installed requirements are checked. Banned
licences (GPL, AGPL, SSPL, CC-BY-SA, EUPL, unknown) fail; LGPL, MPL and EPL
need a row in `scripts/license-exceptions.txt`. Regenerates `NOTICE`.

Usage: uv run python scripts/check-licenses.py [--output NOTICE]
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCEPTIONS_FILE = ROOT / "scripts" / "license-exceptions.txt"


def normalize_name(name: str) -> str:
    """Normalize a distribution name the way installers compare them."""
    return (
        re.split(r"[ ;\[<>=!~(\]]", name, maxsplit=1)[0]
        .strip()
        .lower()
        .replace("_", "-")
        .replace(".", "-")
    )


def parse_requirement(spec: str) -> tuple[str, set[str], str]:
    """Split a requirement into (name, extras, marker)."""
    req_part, _, marker = spec.partition(";")
    extras: set[str] = set()
    bracket, _, rest = req_part.partition("[")
    if rest:
        extras = {e.strip().lower() for e in rest.partition("]")[0].split(",") if e.strip()}
    return normalize_name(bracket), extras, marker.strip()


def marker_allows(marker: str, active_extras: set[str]) -> bool:
    """Decide whether a requirement marker keeps the dependency.

    Extra markers are evaluated against the extras requested by the parent;
    environment markers are kept (packages that are not installed are skipped
    later, so keeping them only errs toward checking more).
    """
    if not marker:
        return True
    if "extra" not in marker:
        return True
    wanted = set(re.findall(r"""extra\s*==\s*['"]([^'"]+)['"]""", marker))
    return bool(wanted & active_extras)


def compute_closure(
    roots: dict[str, set[str]],
    get_requires: Callable[[str], list[str] | None],
) -> set[str]:
    """Walk installed requirements from the runtime roots.

    `get_requires` returns the requirement strings for an installed
    distribution, or None when it is not installed.
    """
    extras_for: dict[str, set[str]] = {name: set(e) for name, e in roots.items()}
    closure: set[str] = set()
    stack = list(roots)
    while stack:
        name = stack.pop()
        if name in closure:
            continue
        requires = get_requires(name)
        if requires is None:
            continue
        closure.add(name)
        active = extras_for.get(name, set())
        for spec in requires:
            child, child_extras, marker = parse_requirement(spec)
            if not marker_allows(marker, active):
                continue
            known = extras_for.setdefault(child, set())
            if child_extras - known:
                known.update(child_extras)
                closure.discard(child)
            if child not in closure:
                stack.append(child)
    return closure


def runtime_roots() -> dict[str, set[str]]:
    """Read runtime dependencies and extras from `pyproject.toml`."""
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    roots: dict[str, set[str]] = {}
    for spec in data["project"]["dependencies"]:
        name, extras, _ = parse_requirement(spec)
        roots.setdefault(name, set()).update(extras)
    return roots


def installed_requires(name: str) -> list[str] | None:
    """Return requirement strings for an installed distribution."""
    try:
        dist = importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        return None
    return list(dist.requires or [])


def classify(license_name: str) -> str:
    """Return 'ok', 'banned' or 'exception' for a licence string."""
    text = license_name.upper()
    if "LGPL" in text or ("LESSER" in text and "GENERAL PUBLIC" in text):
        return "exception"
    if (
        "GPL" in text
        or "GENERAL PUBLIC" in text
        or "AFFERO" in text
        or "SSPL" in text
        or "SERVER SIDE PUBLIC" in text
        or "SHAREALIKE" in text
        or "CC-BY-SA" in text
        or "CC BY-SA" in text
        or "EUPL" in text
        or "EUROPEAN UNION PUBLIC" in text
        or text.strip() in {"UNKNOWN", "UNLICENSED", ""}
    ):
        return "banned"
    if "MPL" in text or "MOZILLA PUBLIC" in text or "EPL" in text or "ECLIPSE PUBLIC" in text:
        return "exception"
    return "ok"


def read_exceptions() -> set[str]:
    """Read owner-approved weak-copyleft package names."""
    if not EXCEPTIONS_FILE.exists():
        return set()
    names: set[str] = set()
    for line in EXCEPTIONS_FILE.read_text(encoding="utf-8").splitlines():
        name = normalize_name(line.partition("#")[0])
        if name:
            names.add(name)
    return names


def check(
    report: list[dict[str, str]],
    closure: set[str],
    exceptions: set[str],
    project_name: str,
) -> list[str]:
    """Return one error per runtime package with a bad licence."""
    by_name = {normalize_name(e["Name"]): e for e in report}
    errors: list[str] = []
    for name in sorted(closure - {normalize_name(project_name)}):
        entry = by_name.get(name)
        if entry is None:
            errors.append(f"{name}: no licence data reported")
            continue
        verdict = classify(entry.get("License", "UNKNOWN"))
        if verdict == "banned":
            errors.append(
                f"{name} {entry.get('Version', '?')}: banned licence '{entry['License']}'"
            )
        elif verdict == "exception" and name not in exceptions:
            errors.append(
                f"{name} {entry.get('Version', '?')}: weak-copyleft licence "
                f"'{entry['License']}' needs a row in scripts/license-exceptions.txt"
            )
    return errors


def render_notice(report: list[dict[str, str]], closure: set[str], project_name: str) -> str:
    """Render the NOTICE file for the runtime closure."""
    by_name = {normalize_name(e["Name"]): e for e in report}
    lines = [
        "Third-party Python packages bundled at runtime.",
        "Dev-only tools are exempt and not listed.",
        "",
    ]
    for name in sorted(closure - {normalize_name(project_name)}):
        entry = by_name.get(name, {})
        lines.append(
            f"- {entry.get('Name', name)} {entry.get('Version', '?')} "
            f"({entry.get('License', 'UNKNOWN')}) {entry.get('URL', '')}".rstrip()
        )
    return "\n".join(lines) + "\n"


def project_name() -> str:
    """Read the project name from `pyproject.toml`."""
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["name"])


def main(argv: list[str]) -> int:
    """Check runtime licences and regenerate NOTICE."""
    parser = argparse.ArgumentParser(description="Check runtime dependency licences.")
    parser.add_argument("--output", default="NOTICE", help="NOTICE file to write")
    args = parser.parse_args(argv)

    closure = compute_closure(runtime_roots(), installed_requires)
    completed = subprocess.run(
        [sys.executable, "-m", "piplicenses", "--format=json", "--with-urls"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        print(f"pip-licenses failed:\n{completed.stderr}", file=sys.stderr)
        return 1
    report = json.loads(completed.stdout or "[]")

    errors = check(report, closure, read_exceptions(), project_name())
    Path(args.output).write_text(render_notice(report, closure, project_name()), encoding="utf-8")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"licenses: ok ({len(closure)} runtime packages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
