# Learned Lessons

Load this file only when a gate fails or a task matches a pain point. Keep it under 200 lines.

## Pain-point rules

| # | Rule | Owner | Detection |
|---|---|---|---|
| 1 | Never default a missing identity to a shared owner. Return 401. | `src/app/core/auth.py` | `tests/test_identity.py` |
| 2 | Read environment variables only in `src/app/core/config.py`. | `src/app/core/config.py` | ast-grep rule `no-env-outside-config` |
| 3 | A new directory needs an ADR and a `layout.allow` entry in the same PR. | `repo-policy.json` | `make policy` |
| 4 | A new dependency needs a ledger row. | `docs/dependencies.md` | `make policy` |
| 5 | Declare tool versions once: the `dev` group or a variable with a `renovate:` comment. | `pyproject.toml`, `Makefile` | review-only |
| 6 | Docs may cite only paths, make targets and links that exist. | `README.md`, `ARCHITECTURE.md` | `make policy` |

## Incident log

| Date | Task | Mistake | Fix | Detection |
|---|---|---|---|---|
| 2026-10-27 | Fleet remediation | The README said init runs on first push and deletes itself; it is a manual workflow and stays in the repo. | Rewrote the README from the workflow file. | `make policy` docs check |
