#!/usr/bin/env python3
"""Evaluate versioned offline-guard fixtures without network or runtime access."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "ci" / "offline-guards"
MAP = CONTRACT / "path-to-guard.json"
INVENTORY = CONTRACT / "inventory.json"
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def path_digest(paths: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(paths)).encode("utf-8")).hexdigest()


def matches(path: str, glob: str) -> bool:
    return fnmatch.fnmatchcase(path, glob)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} FIXTURE.json", file=sys.stderr)
        return 2
    fixture = load(Path(argv[1]))
    mapping = load(MAP)
    inventory = load(INVENTORY)
    changed_paths = fixture.get("changed_paths")
    source_sha = fixture.get("source_sha")
    if not isinstance(changed_paths, list) or not all(isinstance(path, str) for path in changed_paths):
        print(json.dumps({"result": "failed", "failure": "invalid changed_paths"}, sort_keys=True))
        return 1
    if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
        print(json.dumps({"result": "failed", "failure": "invalid source_sha"}, sort_keys=True))
        return 1
    required = sorted(guard["id"] for guard in inventory["guards"] if guard["blocking"])
    controls = mapping["control_paths"]
    control_change = any(matches(path, glob) for path in changed_paths for glob in controls)
    matched = [] if control_change else [rule for rule in mapping["rules"] if any(matches(path, rule["glob"]) for path in changed_paths)]
    guards = required if control_change else sorted({guard for rule in matched for guard in rule["guards"]})
    decision = "applicable" if guards else "not_applicable"
    rule = "control-plane" if control_change else (matched[0]["glob"] if matched else mapping["not_applicable_rule"])
    output: dict[str, object] = {
        "source_sha": source_sha,
        "changed_paths_sha256": path_digest(changed_paths),
        "decision": decision,
        "guards": guards,
        "rule": rule,
        "result": "passed",
    }
    statuses = fixture.get("guard_statuses", {})
    if not isinstance(statuses, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in statuses.items()):
        output.update(result="failed", failure="invalid guard statuses")
    elif decision == "applicable":
        failed = {guard: statuses.get(guard, "missing") for guard in guards if statuses.get(guard) != "success"}
        if failed:
            output.update(result="failed", failure="required guard non-success", failed_guards=sorted(failed), guard_statuses=failed)
    elif statuses:
        output.update(result="failed", failure="not_applicable has guard statuses")
    print(json.dumps(output, sort_keys=True))
    return 0 if output["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
