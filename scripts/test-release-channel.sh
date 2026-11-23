#!/usr/bin/env bash
# Static safety contract for repository-local component release workflows.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
dev="$root/.github/workflows/tag-dev.yaml"
prod="$root/.github/workflows/promote-prod.yaml"
workflow="$root/.github/workflows/validate.yaml"

fail() { printf 'release-channel contract failed: %s\n' "$*" >&2; exit 1; }
require() { grep -Fq -- "$2" "$1" || fail "missing '$2' in ${1#$root/}"; }
require_exactly_once() {
  local file=$1 needle=$2 count
  count=$(grep -Fxc -- "$needle" "$file" || true)
  test "$count" = 1 || fail "expected exactly one '$needle' in ${file#$root/}; found $count"
}
forbid() { grep -Fq -- "$2" "$1" && fail "forbidden '$2' in ${1#$root/}" || true; }
forbid_job_if() {
  local file=$1 job=$2
  if awk -v job="$job" '
    $0 == "  " job ":" { in_job=1; next }
    in_job && /^  [a-z0-9-]+:/ { in_job=0 }
    in_job && /^    if:/ { found=1 }
    END { exit found ? 0 : 1 }
  ' "$file"; then
    fail "forbidden if bypass in $job"
  fi
}

for file in "$dev" "$prod" "$workflow"; do
  test -f "$file" || fail "missing ${file#$root/}"
done

require "$dev" 'workflows: [Validate & Security]'
require "$dev" 'branches: [main]'
require "$dev" "github.event.workflow_run.conclusion == 'success'"
require "$dev" "github.event.workflow_run.head_branch == 'main'"
require "$dev" 'contents: write'
require "$dev" 'git config user.name "GitHub Actions"'
require "$dev" 'git config user.email "actions@github.com"'
require "$dev" 'dev-v$(date -u +%Y.%m).${SHA:0:12}'
require "$dev" 'refs/tags/$candidate'
require "$dev" 'git push --force origin refs/tags/dev-latest'
require "$dev" 'git rev-parse '"'"'dev-latest^{commit}'"'"''
forbid "$dev" 'targetRevision'
forbid "$dev" 'kubectl '

require "$prod" 'workflow_dispatch:'
require "$prod" 'candidate_tag:'
require "$prod" 'actions: read'
require "$prod" 'contents: write'
require "$prod" 'git config user.name "GitHub Actions"'
require "$prod" 'git config user.email "actions@github.com"'
require "$prod" 'dev-vYYYY.MM.<identifier>'
require "$prod" 'git merge-base --is-ancestor "$candidate_sha" origin/main'
require "$prod" '.name == "Validate & Security"'
require "$prod" '.conclusion == "success"'
require "$prod" '.head_sha == $sha'
require "$prod" '.head_branch == "main"'
require "$prod" 'prod-v$suffix'
require "$prod" 'git push --force origin refs/tags/prod-stable'
require "$prod" 'git rev-parse '"'"'prod-stable^{commit}'"'"''
forbid "$prod" 'targetRevision'
forbid "$prod" 'kubectl '

require "$workflow" 'release-channel-contract:'
require "$workflow" 'scripts/test-release-channel.sh'
require "$workflow" '      - release-channel-contract'
require "$workflow" 'client0-bootstrap-group-ref-contract:'
require "$workflow" 'Client0 bootstrap group reference contract'
require_exactly_once "$workflow" '        run: node --test apps/60-services/txo-fabric/tenants/hairem/client0-bootstrap-group-ref.test.mjs'
require "$workflow" '      - client0-bootstrap-group-ref-contract'
require "$workflow" '"client0-bootstrap-group-ref-contract"'
forbid_job_if "$workflow" "client0-bootstrap-group-ref-contract"
require "$workflow" 'openbao-fabric-v2-phase1-argo-contract:'
require "$workflow" 'OpenBao Fabric v2 Phase1 Argo contract'
require_exactly_once "$workflow" '        run: python3 -m unittest tests/test_txo_fabric_openbao_v2_phase1_argo.py'
require "$workflow" '      - openbao-fabric-v2-phase1-argo-contract'
require "$workflow" '"openbao-fabric-v2-phase1-argo-contract"'
forbid_job_if "$workflow" "openbao-fabric-v2-phase1-argo-contract"
require "$workflow" 'openbao-fabric-v2-phase2-custody-issuer-contract:'
require "$workflow" 'OpenBao Fabric v2 Phase2 custody issuer contract'
require_exactly_once "$workflow" '        run: python3 -m unittest tests/test_openbao_fabric_v2_phase2_custody_issuer_contract.py'
require "$workflow" '      - openbao-fabric-v2-phase2-custody-issuer-contract'
require "$workflow" '"openbao-fabric-v2-phase2-custody-issuer-contract"'
forbid_job_if "$workflow" "openbao-fabric-v2-phase2-custody-issuer-contract"
forbid "$workflow" 'continue-on-error:'

printf 'release-channel contract: PASS\n'
