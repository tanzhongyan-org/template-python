# 0003. OpenAPI-first contract with a generated TypeScript client

## Context

Frontend products need typed calls for this API. A hand-written client drifts
from the routes, and nothing fails when it does.

## Decision

- Export the FastAPI document to `clients/openapi.json` with `make openapi`.
- Generate a fetch client into `clients/ts` with `@hey-api/openapi-ts`
  (`make client`). TypeScript stays on 5.x because the generator crashes on 6/7.
- Gate both in CI: `make spec-check` fails when the committed spec or client
  differs from a fresh generation, and `make check` runs it.

## Consequences

- Route changes need `make openapi` and `make client` in the same PR.
- The new top-level `clients` directory is listed in `layout.allow` in
  `scripts/repo-policy.json`.
- Derived frontends vendor or publish `clients/ts` instead of writing calls.
