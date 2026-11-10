#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
kustomize=${KUSTOMIZE:-kustomize}
target="$root/apps/20-media/music-assistant/overlays/prod"
rendered=$(mktemp)
trap 'rm -f "$rendered"' EXIT

"$kustomize" build "$target" >"$rendered"

python3 - "$rendered" <<'PY'
import re
import sys
from pathlib import Path

rendered = Path(sys.argv[1]).read_text()
documents = [doc for doc in re.split(r'^---\s*$', rendered, flags=re.MULTILINE) if doc.strip()]
external = []
infisical = []

for document in documents:
    kind = re.search(r'^kind:\s*(\S+)\s*$', document, re.MULTILINE)
    name = re.search(r'^  name:\s*(music-assistant-secrets)\s*$', document, re.MULTILINE)
    namespace = re.search(r'^  namespace:\s*(media)\s*$', document, re.MULTILINE)
    if not kind or not name or not namespace:
        continue
    if kind.group(1) == 'ExternalSecret':
        target = re.search(r'^  target:\n(?:.*\n)*?^    name:\s*(music-assistant-secrets)\s*$', document, re.MULTILINE)
        store = re.search(r'^  secretStoreRef:\n(?:.*\n)*?^    name:\s*(openbao)\s*$', document, re.MULTILINE)
        if target and store:
            external.append(document)
    if kind.group(1) == 'InfisicalSecret':
        infisical.append(document)

if len(external) != 1:
    raise SystemExit(f'expected exactly one ESO/OpenBao ExternalSecret target, found {len(external)}')
if infisical:
    raise SystemExit('legacy InfisicalSecret still targets music-assistant-secrets')

print('music-assistant secret controller: ESO/OpenBao unique; Infisical absent')
PY
