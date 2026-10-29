"""Unit tests for the licence gate (no network, no database)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_licenses import check, classify, compute_closure, main, render_notice


@pytest.mark.parametrize(
    ("licence", "expected"),
    [
        ("MIT", "ok"),
        ("MIT License", "ok"),
        ("Apache-2.0", "ok"),
        ("BSD-3-Clause", "ok"),
        ("ISC", "ok"),
        ("PSF-2.0", "ok"),
        ("MIT-0", "ok"),
        ("Apache-2.0 OR BSD-3-Clause", "ok"),
        ("GPL-3.0", "banned"),
        ("GNU General Public License", "banned"),
        ("AGPL-3.0", "banned"),
        ("GNU Affero General Public License", "banned"),
        ("SSPL-1.0", "banned"),
        ("Server Side Public License", "banned"),
        ("CC-BY-SA-4.0", "banned"),
        ("Creative Commons Attribution-ShareAlike 4.0", "banned"),
        ("EUPL-1.2", "banned"),
        ("UNKNOWN", "banned"),
        ("LGPL-2.1", "exception"),
        ("GNU Lesser General Public License", "exception"),
        ("Mozilla Public License 2.0 (MPL 2.0)", "exception"),
        ("Mozilla Public License 2.0", "exception"),
        ("EPL-2.0", "exception"),
        ("Eclipse Public License 2.0", "exception"),
    ],
)
def test_classify(licence: str, expected: str) -> None:
    assert classify(licence) == expected


def test_closure_follows_extras_but_skips_test_extras() -> None:
    requires = {
        "web": ["wsgi>=1; extra == 'standard'", "pytest>=1; extra == 'test'"],
        "wsgi": [],
        "pytest": [],
    }
    closure = compute_closure({"web": {"standard"}}, requires.get)
    assert closure == {"web", "wsgi"}


def test_closure_skips_uninstalled() -> None:
    closure = compute_closure({"web": set()}, lambda name: None)
    assert closure == set()


def test_check_fails_banned_and_unknown() -> None:
    report = [
        {"Name": "ok-pkg", "Version": "1.0", "License": "MIT", "URL": ""},
        {"Name": "bad-pkg", "Version": "1.0", "License": "GPL-3.0", "URL": ""},
    ]
    errors = check(report, {"ok-pkg", "bad-pkg", "missing-pkg"}, set(), "my-app")
    assert len(errors) == 2
    assert any("bad-pkg" in e and "banned" in e for e in errors)
    assert any("missing-pkg" in e for e in errors)


def test_check_allows_excepted_weak_copyleft() -> None:
    report = [{"Name": "mpl-pkg", "Version": "1.0", "License": "MPL-2.0", "URL": ""}]
    assert check(report, {"mpl-pkg"}, {"mpl-pkg"}, "my-app") == []
    assert len(check(report, {"mpl-pkg"}, set(), "my-app")) == 1


def test_check_skips_project_itself() -> None:
    report = [{"Name": "my-app", "Version": "0.1.0", "License": "UNKNOWN", "URL": ""}]
    assert check(report, {"my-app"}, set(), "my-app") == []


def test_render_notice_lists_closure() -> None:
    report = [{"Name": "ok-pkg", "Version": "1.0", "License": "MIT", "URL": "https://x"}]
    notice = render_notice(report, {"ok-pkg", "my-app"}, "my-app")
    assert "ok-pkg 1.0 (MIT)" in notice
    assert "my-app" not in notice


def test_gate_passes_on_clean_tree(tmp_path: Path) -> None:
    """The real gate exits 0 and writes NOTICE for this repo."""
    target = tmp_path / "NOTICE"
    assert main(["--output", str(target)]) == 0
    assert "fastapi" in target.read_text(encoding="utf-8")
