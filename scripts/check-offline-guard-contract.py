#!/usr/bin/env python3
"""Evaluate versioned offline-guard fixtures without network or runtime access."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "ci" / "offline-guards"
MAP = CONTRACT / "path-to-guard.json"
INVENTORY = CONTRACT / "inventory.json"
BASELINE = CONTRACT / "baseline.json"


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
    baseline = load(BASELINE)
    changed_paths = fixture["changed_paths"]
    if not isinstance(changed_paths, list) or not all(isinstance(path, str) for path in changed_paths):
        print(json.dumps({"result": "failed", "failure": "invalid changed_paths"}))
        return 1

    required = sorted(guard["id"] for guard in inventory["guards"] if guard["blocking"])
    controls = mapping["control_paths"]
    control_change = any(matches(path, glob) for path in changed_paths for glob in controls)
    matched = [] if control_change else [
        rule for rule in mapping["rules"]
        if any(matches(path, rule["glob"]) for path in changed_paths)
    ]
    guards = required if control_change else sorted({guard for rule in matched for guard in rule["guards"]})
    decision = "applicable" if guards else "not_applicable"
    rule = "control-plane" if control_change else (matched[0]["glob"] if matched else mapping["not_applicable_rule"])
    output: dict[str, object] = {
        "source_sha": baseline["source_sha"],
        "changed_paths_sha256": path_digest(changed_paths),
        "decision": decision,
        "guards": guards,
        "rule": rule,
        "result": "passed",
    }

    if fixture.get("fixture_valid", True) is False:
        output.update(result="failed", failure="fixture validation failed")
    else:
        statuses = fixture.get("guard_statuses", {})
        if not isinstance(statuses, dict):
            output.update(result="failed", failure="invalid guard statuses")
        else:
            bad = [guard for guard in guards if statuses.get(guard, "success") in {"missing", "skipped", "cancelled"}]
            if bad:
                output.update(result="failed", failure="required guard missing", failed_guards=sorted(bad))

    print(json.dumps(output, sort_keys=True))
    return 0 if output["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
