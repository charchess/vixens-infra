# Workflow

## Canonical path

```text
GitHub Issue → branch → Pull Request → required CI → merge to main
```

This repository has no independent deployment authority. Until an approved Argo CD handoff exists, `main` is source preparation only.

## Local component release tags

This repository may create and move only its own component-release tags. A successful `Validate & Security` run on `main` creates an immutable `dev-vYYYY.MM.<short-sha>` tag and moves local `dev-latest`. Production promotion is an explicit human-dispatched workflow: it accepts one exact immutable development tag, requires that exact commit to be an ancestor of `main` and to have a successful `Validate & Security` run, creates an immutable `prod-v...` tag, and moves only local `prod-stable`.

A component tag is release evidence, not deployment authority. Human physical/platform validation remains required before production promotion. These tags do not update any Argo CD Application, `targetRevision`, release BOM, Terraform, Talos, cluster object, or separate Argo handoff.

## Required review questions

1. Does the change stay within this repository's responsibility?
2. Are any new platform/service requirements declared through the contract model?
3. Does it alter an active Argo CD owner, a release BOM, stateful identity, or a security boundary? If yes, stop and use the dedicated orchestration/migration issue.
4. Are all applicable CI checks green, with no unexpected skipped required job?
