# Docs

Documents live where their lifespan says. Put each new document in one place only.

| Document | Where | Lifespan | What happens when work completes |
| --- | --- | --- | --- |
| Architecture | `ARCHITECTURE.md` at the repo root | Permanent | Update it in the same PR as the code. |
| Decision records | numbered files in `docs/decisions` | Permanent, append-only | Never edit. A change needs a new record that says `Supersedes: NNNN`. |
| Dependency ledger | `docs/dependencies.md` | Permanent | Add or remove a row with the dependency. |
| Functional specs | the `specs` folder under `docs` | One feature | Fold the rules into `ARCHITECTURE.md`, then move the spec to `archive`. |
| Plans | the `plans` folder under `docs` | One PR | Commit the plan, then `git rm` it when the PR merges. |
| Archive | the `archive` folder under `docs` | Reference | Old specs. Agents skip it. |

Create `specs`, `plans` and `archive` when you first need them. `make policy` checks that every directory is listed in `repo-policy.json`.
