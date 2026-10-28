# Security policy

<!-- TEMPLATE-TODO(security): confirm private vulnerability reporting is enabled and add a backup contact -->

## Report a vulnerability

Report vulnerabilities through GitHub private vulnerability reporting:
[open a private advisory](https://github.com/tanzhongyan-org/template-python/security/advisories/new).
Do not open a public issue for a security problem.

## Supported versions

Only the `main` branch is supported. Fixes land on `main`; there are no backport branches.

## Response targets

| Step | Target |
| --- | --- |
| Acknowledge your report | 3 business days |
| Triage and severity decision | 10 business days |

## How this repository is scanned

| Layer | Tool | Runs |
| --- | --- | --- |
| Static analysis in lint | Ruff `S` (bandit) rules | `make lint`, every PR |
| Static analysis across the codebase | CodeQL, `security-extended` queries, Python and Actions | PR, push, weekly |
| Secrets | gitleaks, full history | `security` CI job and the pre-commit hook |
| Dependency vulnerabilities | `uv audit`; dependency review on PRs (fails on high severity) | `security` and `dependency-review` CI jobs |
| Workflow security | zizmor | `security` CI job |
| Dynamic testing | Schemathesis against `/openapi.json` | weekly and on demand (`.github/workflows/dast.yml`) |
