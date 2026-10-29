#!/usr/bin/env python3
"""Fail when the committed OpenAPI spec differs from the app.

Usage: uv run python scripts/check_spec.py
"""

from __future__ import annotations

import difflib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_openapi import SPEC, export  # noqa: E402


def main() -> int:
    """Compare the committed spec against a fresh export."""
    if not SPEC.exists():
        print(f"{SPEC} is missing; run make openapi", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "openapi.json"
        export(fresh)
        committed = SPEC.read_text(encoding="utf-8").splitlines()
        current = fresh.read_text(encoding="utf-8").splitlines()
    if committed != current:
        print(f"{SPEC} is stale; run make openapi and make client", file=sys.stderr)
        print(
            "\n".join(
                difflib.unified_diff(committed, current, "committed", "current", lineterm="")
            ),
            file=sys.stderr,
        )
        return 1
    print("spec-check: openapi.json matches the app")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
