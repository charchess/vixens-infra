# Offline guard contract

This directory is a versioned, local-only contract for the relevant guards in `Validate & Security`. It supplies static evidence for issue #114; it does not change GitHub rulesets, permissions, GitOps, runtime, release, merge or deployment.

## Deterministic applicability

`path-to-guard.json` is the authoritative `changed paths -> required guards` inventory. A control-plane change to the workflow, map, checker or declared lockfile requires every blocking guard. A normal changed path selects the union of every matching rule. A non-match is `not_applicable` only when the checker records the evaluated source SHA, `no_path_rule_matched`, and the SHA-256 digest of the sorted changed-path list.

For an applicable decision, every selected guard must be present and explicitly `success`. `missing`, `skipped`, `cancelled`, `neutral`, `timed_out`, `action_required`, and any other value are non-success. The state value is preserved in evidence; `cancelled` is not relabelled as `skipped`.

## Validation Summary boundary

The workflow Summary enumerates its seven current required workflow jobs and fails when a required job is absent or its `needs.<job>.result` differs from `success`. It is deliberately independent of branch protection or rulesets. The known external limitation remains: required-check/ruleset inspection is unavailable to the App, so the external blocking configuration is not asserted here.

## Fixtures and evidence

Run:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_offline_guard_contract.py -v

The GREEN fixtures cover mapped Kustomization, control-plane, and traced `not_applicable` decisions. The RED fixtures cover required guard `missing`, `skipped`, `cancelled`, `neutral`, `timed_out`, and `action_required` states. `evidence/` contains deterministic checker output for every fixture.

All fixtures record the implementation provenance SHA `dae2acc3a27a623b7cd8ee61a5e1b0a4e4decdbd`. This contract is CI/static evidence only; it makes no runtime claim.
