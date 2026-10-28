# Pull request

## What and why

<!-- One or two sentences. What changes, and what problem does it solve? -->

Closes #

## How it was verified

<!-- Paste the quiet output of `make check`, or the failing-then-passing test for a bug fix. -->

```text

```

## Risk and rollback

<!-- What could break? How do you undo this change? -->

## Checklist

- [ ] Tests cover the new behaviour at its public entry point
- [ ] Docs are updated in this PR (`ARCHITECTURE.md` code map, `README.md` tables)
- [ ] No new dependency without a row in `docs/dependencies.md`
- [ ] No new directory without an ADR and a `layout.allow` change in `scripts/repo-policy.json`
