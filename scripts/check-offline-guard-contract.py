#!/usr/bin/env python3
"""Evaluate versioned offline-guard fixtures without network or runtime access."""
from __future__ import annotations
import argparse, fnmatch, hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "ci" / "offline-guards"
MAP = CONTRACT / "path-to-guard.json"
INVENTORY = CONTRACT / "inventory.json"
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def path_digest(paths): return hashlib.sha256("\n".join(sorted(paths)).encode()).hexdigest()
def matches(path, glob): return fnmatch.fnmatchcase(path, glob)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("fixture")
    args=parser.parse_args()
    if not SHA_RE.fullmatch(args.source_sha): raise SystemExit("source SHA must be a 40-character lowercase hex commit")
    fixture=load(Path(args.fixture)); mapping=load(MAP); inventory=load(INVENTORY)
    changed=fixture.get("changed_paths")
    if not isinstance(changed,list) or not all(isinstance(p,str) for p in changed):
        print(json.dumps({"result":"failed","failure":"invalid changed_paths"},sort_keys=True)); return 1
    required=sorted(g["id"] for g in inventory["guards"] if g["blocking"])
    control=any(matches(path,glob) for path in changed for glob in mapping["control_paths"])
    matched=[] if control else [rule for rule in mapping["rules"] if any(matches(path,rule["glob"]) for path in changed)]
    guards=required if control else sorted({guard for rule in matched for guard in rule["guards"]})
    decision="applicable" if guards else "not_applicable"
    rule="control-plane" if control else (matched[0]["glob"] if matched else mapping["not_applicable_rule"])
    output={"source_sha":args.source_sha,"changed_paths_sha256":path_digest(changed),"decision":decision,"guards":guards,"rule":rule,"result":"passed"}
    statuses=fixture.get("guard_statuses",{})
    if not isinstance(statuses,dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in statuses.items()): output.update(result="failed",failure="invalid guard statuses")
    elif decision=="applicable":
        failed={g:statuses.get(g,"missing") for g in guards if statuses.get(g)!="success"}
        if failed: output.update(result="failed",failure="required guard non-success",failed_guards=sorted(failed),guard_statuses=failed)
    elif statuses: output.update(result="failed",failure="not_applicable has guard statuses")
    print(json.dumps(output,sort_keys=True)); return 0 if output["result"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
