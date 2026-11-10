# Disposable CNPG DR target — human-gated runbook

This is a **template only**. It is intentionally outside every active Argo Application and does not execute a restore.

## Gate 0 — mandatory human authorization
Before any rendering, credential creation, or apply, a human incident commander and data owner must record: the run-id, approved source backup, retention window, deletion owner, target storage class, and confirmation that ObjectStore credentials are **read-only**. Stop if any item is missing.

## Safety invariants
- Substitute `REPLACE_RUN_ID` with a DNS-safe, unique identifier before review.
- Namespace, Cluster, Service and PVC names retain that run-id; never reuse the source identity.
- `default-deny` is installed before any allow policy. This template intentionally contains no allow policy.
- The ObjectStore Secret is external to this template and must be independently proven read-only.
- No Argo Application, ExternalSecret, backup, restore, failover, restart, sync, PVC/PV mutation, or credential is created by this directory.

## Execution boundary
A separate, explicitly approved incident procedure may render and apply a reviewed copy. This runbook deliberately provides no executable command. After inspection, deletion of the dedicated namespace is a separately authorized cleanup action.
