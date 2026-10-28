# Contributing

## Prerequisites

| Tool | Version source | Install |
| --- | --- | --- |
| Python | `.python-version` (uv installs it for you) | [uv docs](https://docs.astral.sh/uv/getting-started/installation/) |
| uv | `UV_VERSION` in `.github/workflows/ci.yml` | [uv docs](https://docs.astral.sh/uv/getting-started/installation/) |
| Node | `.node-version` (runs the policy checker, jscpd and markdownlint) | [nodejs.org](https://nodejs.org/en/download) |
| Docker | `compose.yaml` pins the Postgres image | [docs.docker.com](https://docs.docker.com/get-docker/) |
| GNU make | any recent version | your package manager; Windows: `winget install ezwinports.make` |
| gitleaks (optional locally) | `GITLEAKS_VERSION` in `.github/workflows/ci.yml` | [gitleaks releases](https://github.com/gitleaks/gitleaks/releases) |

<!-- TEMPLATE-TODO(license): set the copyright holder in LICENSE to your own name or organisation -->

## Set up

```bash
make setup
cp .env.example .env
make up
make db-migrate
```

You should see `Running upgrade  -> 08aacb44d85e, create notes table` on the first migration.

## Daily loop

| Command | When |
| --- | --- |
| `make verify` | After each change. Typecheck, lint, anti-slop and policy. No database needed. |
| `make check` | Before you push. Adds tests, dead code and duplication. Needs Postgres. |

The git hooks run `make verify` and `make test` before a push.

## Add a feature

Use the notes slice as the pattern. Touch files in this order:

1. Model in `src/app/models/`, imported in `src/app/models/__init__.py`.
2. Migration: `make db-revision m="add_thing"`, then read the generated file in `alembic/versions/`.
3. Schemas in `src/app/schemas/`.
4. Endpoints in `src/app/api/v1/endpoints/`. Take `owner_id: OwnerId` and `db: DbSession`, and filter every query by owner.
5. Register the router in `src/app/api/v1/router.py`.
6. Tests in `tests/`: success, validation failure, 401 without identity, and 404 for another owner's row.
7. Docs: add the new helpers to the code map in `ARCHITECTURE.md`, new variables to the table in `README.md`, and new dependencies to `docs/dependencies.md`.

A new directory needs an ADR in `docs/decisions` and an entry in `layout.allow` in `scripts/repo-policy.json`, in the same PR.

## Commits and pull requests

- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat(notes): add search`. The `commit-msg` hook checks the format.
- Do not add AI `Co-Authored-By` trailers. The hook rejects them.
- Fill in the pull request template. Paste the quiet output of `make check`.
- `ci-passed` must be green before merge.

## Where docs go

See [docs/README.md](../docs/README.md).

## Maintainer notes

- **Branch ruleset.** `.github/rulesets/main.json` exports a ruleset for `main`. Import it under Settings, Rules, Rulesets, Import a ruleset. With the GitHub CLI: `gh api repos/OWNER/REPO/rulesets --method POST --input .github/rulesets/main.json`. It requires a pull request and the `ci-passed` check, blocks force pushes and deletion, and requires CodeQL results at high severity or above.
- **Renovate.** `.github/renovate.json` groups non-major updates and reads version comments in the `Makefile` and the workflows. Tool versions in `pyproject.toml` need no comment.
- **Template debt.** `make template-debt` lists the markers a derived repo must resolve. The init workflow opens an issue with that list.
