# Offline guard contract

This local-only contract maps changed paths to required validation guards. It makes no GitHub ruleset, permission, GitOps, runtime, release, merge or deployment change.

## Candidate provenance and applicability

The checker requires `--source-sha` for every evaluation. Tests resolve it from `git rev-parse HEAD`; each output therefore records the exact candidate head evaluated, the matching rule, and a SHA-256 digest of sorted changed paths. A no-match is `not_applicable` only with `no_path_rule_matched`, that candidate SHA and digest.

Control-plane changes require all blocking guards. A `.github/workflows/**` diff requires `actionlint`, `yaml-lint` and `scope-boundary`; other rules are in `path-to-guard.json`. Every required guard must be explicitly `success`; missing, skipped, cancelled, neutral, timed_out, action_required and unknown states fail, preserving their actual state in output.

## Evidence

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_offline_guard_contract.py -v`. GREEN fixtures cover mapped, control-plane, workflow, and not_applicable decisions. RED fixtures cover all relevant non-success states, including a workflow actionlint skip. The current branch head is the evaluated candidate; no static fixture embeds a stale predecessor SHA.

External branch protection/rulesets remain unverified by design; Validation Summary is independently fail-closed.
