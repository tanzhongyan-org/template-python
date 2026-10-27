# 0001. Record architecture decisions

## Context

Choices such as the framework, the database driver and the directory layout outlive the people who made them. Without a record, a new contributor or an agent either repeats the debate or reverses the choice by accident.

## Decision

Write one short record for each irreversible or costly technical choice, in `docs/decisions` as a numbered Markdown file, in the Context, Decision, Consequences format. Records are append-only. To change a decision, add a new record that says `Supersedes: NNNN`.

A new top-level or `src/app` directory counts as a decision and needs a record.

## Consequences

- Reviewers can ask for a record when a PR changes a structural choice.
- The decision history lives in git next to the code.
- Writing a record costs a few minutes per decision.
