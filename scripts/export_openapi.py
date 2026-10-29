#!/usr/bin/env python3
"""Export the FastAPI OpenAPI document to clients/openapi.json.

Usage: uv run python scripts/export_openapi.py [--output clients/openapi.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "clients" / "openapi.json"


def export(output: Path) -> None:
    """Write the app's OpenAPI document to `output`."""
    from app.main import app

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    """Export the OpenAPI document."""
    parser = argparse.ArgumentParser(description="Export the OpenAPI document.")
    parser.add_argument("--output", default=str(SPEC), help="Spec file to write")
    args = parser.parse_args(argv)
    export(Path(args.output))
    print(f"openapi: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
