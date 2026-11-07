#!/usr/bin/env bash
# Static safety contract for repository-local component release workflows.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
dev="$root/.github/workflows/tag-dev.yaml"
prod="$root/.github/workflows/promote-prod.yaml"
workflow="$root/.github/workflows/validate.yaml"

fail() { printf 'release-channel contract failed: %s\n' "$*" >&2; exit 1; }
require() { grep -Fq -- "$2" "$1" || fail "missing '$2' in ${1#$root/}"; }
forbid() { grep -Fq -- "$2" "$1" && fail "forbidden '$2' in ${1#$root/}" || true; }

for file in "$dev" "$prod" "$workflow"; do
  test -f "$file" || fail "missing ${file#$root/}"
done

require "$dev" 'workflows: [Validate & Security]'
require "$dev" 'branches: [main]'
require "$dev" "github.event.workflow_run.conclusion == 'success'"
require "$dev" "github.event.workflow_run.head_branch == 'main'"
require "$dev" 'contents: write'
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

printf 'release-channel contract: PASS\n'
