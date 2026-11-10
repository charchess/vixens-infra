# Offline guard contract

This directory is a versioned, local-only contract for the repository's current CI guards. It is **not** wired into GitHub Actions by this issue and it does not change `.github/workflows/validate.yaml`, workflows, rulesets, GitOps, or runtime.

## Inventory, ownership, and baseline

- `inventory.json` inventories every current blocking guard with its implementation, libraries, fixtures (none existed at the baseline), pins/lockfiles, watched paths, and blocking status. Ariane owns implementation and map qualification; Verity owns review of evidence sufficiency.
- `baseline.json` records the exact observed `Validate & Security` baseline: source SHA `691eda72bc83b872b9ec2d69f7b3a6ebab3e969e`, successful run `42531098811`, and all eight job IDs/conclusions.
- The only repository lockfile found at the baseline is the vendored CloudNativePG `Chart.lock`; the inventory also records action, linter, Kustomize, and Helm pins because they affect guard behavior.

## Applicability map

`path-to-guard.json` is the authoritative path-to-guard map. Its own changes, the fixture contract, the future checker, `validate.yaml`, and the Chart lockfile are control-plane changes: they select every required offline guard. Normal paths select every matching listed rule. A non-match produces a `not_applicable` result with the baseline SHA, a SHA-256 digest of the sorted changed-path list, and `no_path_rule_matched`; it is never represented as an opaque GitHub skip.

The checker is intentionally offline: it reads only versioned JSON and its fixture argument, and calls no cluster, secret store, cloud API, or mutable remote dependency.

## Fixtures and evidence

Run the local contract test suite:

```bash
python3 -m unittest tests/test_offline_guard_contract.py -v
```

The fixtures demonstrate:

| Fixture | Expected result |
| --- | --- |
| `green-mapped-kustomize.json` | A mapped Kustomization path selects the Kustomize render guard and related YAML guards. |
| `green-control-change.json` | A mapping/control change selects every required guard. |
| `green-not-applicable.json` | An unmapped path has an explicit, traced `not_applicable` result. |
| `red-broken-fixture.json` | A deliberately invalid fixture fails. |
| `red-missing-required-guard.json` | A missing required guard fails; skipped/cancelled are treated identically by the checker. |

`evidence/` is the checked-in stdout for each fixture; the test suite verifies it exactly. RED fixtures intentionally return exit code 1. These artifacts are review evidence for a future, separately approved CI integration, not a release verdict.
