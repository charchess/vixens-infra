# CI gates

Infra gates validate shared service source and its Core dependencies. Stateful lifecycle and restore tests are added with their actual service definitions.

## Enforcement

`Validation Summary` is the required merge gate. It fails closed if a common required job fails, is cancelled, or is unexpectedly skipped. Conditional product jobs may be skipped only when their owned source root is absent; once migrated, they become required by the summary.

## Limits

Repository CI proves repository content. It does not prove BOM composition, ArgoCD ownership handoff, deployment health, storage behavior or production promotion; those remain orchestrator and physical-validation gates.
