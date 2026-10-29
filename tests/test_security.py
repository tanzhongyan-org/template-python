"""Unit tests for the new-dependency check (no network, no database)."""

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_new_deps import (
    PackageNotFound,
    check,
    direct_dependencies,
    first_release_at,
    ledger_names,
)

NOW = datetime(2026, 10, 29, tzinfo=UTC)


def metadata(first_upload: str) -> dict:
    """Build minimal PyPI metadata with one release."""
    return {"releases": {"1.0": [{"upload_time_iso_8601": first_upload}]}}


def test_first_release_picks_earliest() -> None:
    meta = {
        "releases": {
            "2.0": [{"upload_time_iso_8601": "2026-10-01T00:00:00+00:00"}],
            "1.0": [{"upload_time_iso_8601": "2020-01-01T00:00:00+00:00"}],
        }
    }
    assert first_release_at(meta) == datetime(2020, 1, 1, tzinfo=UTC)


def test_first_release_ignores_bad_rows() -> None:
    assert first_release_at({"releases": {"1.0": [{"upload_time_iso_8601": "nope"}]}}) is None
    assert first_release_at({"releases": {}}) is None
    assert first_release_at({}) is None


def test_check_passes_old_listed_package() -> None:
    fetch = lambda name: metadata("2020-01-01T00:00:00+00:00")  # noqa: E731
    assert check(["old-pkg"], {"old-pkg"}, fetch, NOW) == []


def test_check_fails_young_missing_and_gone() -> None:
    def fetch(name: str) -> dict:
        if name == "gone-pkg":
            raise PackageNotFound(name)
        if name == "young-pkg":
            return metadata("2026-10-20T00:00:00+00:00")
        return metadata("2020-01-01T00:00:00+00:00")

    errors = check(["young-pkg", "gone-pkg", "unlisted-pkg"], {"young-pkg", "gone-pkg"}, fetch, NOW)
    assert any("young-pkg" in e and "14 days" in e for e in errors)
    assert any("gone-pkg" in e and "not found" in e for e in errors)
    assert any("unlisted-pkg" in e and "dependencies.md" in e for e in errors)


def test_boundary_exactly_14_days_passes() -> None:
    fetch = lambda name: metadata("2026-10-15T00:00:00+00:00")  # noqa: E731
    assert check(["pkg"], {"pkg"}, fetch, NOW) == []


def test_repo_manifest_matches_ledger() -> None:
    """Every direct dependency in pyproject has a ledger row."""
    missing = set(direct_dependencies()) - ledger_names()
    assert missing == set()
