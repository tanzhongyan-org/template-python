# API contract

`clients/openapi.json` is the committed contract for this service.
`clients/ts/` is the TypeScript client generated from it with
`@hey-api/openapi-ts`. Frontend products import the client instead of
hand-writing calls.

<!-- TEMPLATE-TODO(contract): publish the client where your frontend reads it -->

## Regenerate

After any route or schema change:

```bash
make openapi
make client
```

`make spec-check` fails in CI when the committed files are stale.

## Layout

| Path | Contents |
| --- | --- |
| `clients/openapi.json` | Exported from the FastAPI app by `scripts/export_openapi.py`. |
| `clients/ts/` | Generated fetch client. Do not edit by hand. |
