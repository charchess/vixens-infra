#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
kustomize=${KUSTOMIZE:-kustomize}
target="$root/apps/20-media/music-assistant/overlays/prod"
fixture="$root/tests/fixtures/music-assistant-infisical-default-managed-secret-reference.yaml"
checker="$root/tests/music_assistant_secret_controller.py"
rendered=$(mktemp)
error=$(mktemp)
trap 'rm -f "$rendered" "$error"' EXIT

"$kustomize" build "$target" >"$rendered"
python3 "$checker" "$rendered"

if python3 "$checker" "$fixture" > /dev/null 2>"$error"; then
  printf '%s\n' 'expected the legacy Infisical fixture to be rejected' >&2
  exit 1
fi
grep -Fqx 'legacy InfisicalSecret metadata default/music-assistant-secrets effectively targets media/music-assistant-secrets' "$error"

if git -c safe.directory="$root" -C "$root" grep -n -E '(^kind:[[:space:]]*InfisicalSecret[[:space:]]*$|^[[:space:]]*managedSecretReference:)' -- . ':(exclude)tests/**'; then
  printf '%s\n' 'Infisical source remains outside the isolated RED fixture' >&2
  exit 1
fi

printf '%s\n' 'music-assistant secret controller: ESO/OpenBao unique; Infisical absent'
