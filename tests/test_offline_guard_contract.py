"""Regression contract for deterministic, fail-closed validation guards."""
from __future__ import annotations
import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-offline-guard-contract.py"
FIXTURES = ROOT / "ci" / "offline-guards" / "fixtures"
SOURCE_SHA = "dae2acc3a27a623b7cd8ee61a5e1b0a4e4decdbd"
class OfflineGuardContractTest(unittest.TestCase):
    def run_fixture(self, name):
        result = subprocess.run([sys.executable, str(CHECK), str(FIXTURES / name)], cwd=ROOT, capture_output=True, text=True, check=False)
        return result, json.loads(result.stdout)
    def test_required_guard_rejects_each_non_success_state(self):
        for state in ("missing", "skipped", "cancelled", "neutral", "timed_out", "action_required"):
            with self.subTest(state=state):
                result, output = self.run_fixture(f"red-required-{state}.json")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(output["failure"], "required guard non-success")
                self.assertEqual(output["failed_guards"], ["kustomize-render"])
                self.assertEqual(output["guard_statuses"]["kustomize-render"], state)
    def test_mapped_path_is_green_at_exact_source_sha(self):
        result, output = self.run_fixture("green-mapped-kustomize.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output["decision"], "applicable")
        self.assertIn("kustomize-render", output["guards"])
        self.assertEqual(output["source_sha"], SOURCE_SHA)
    def test_not_applicable_is_explicit_and_digest_traced(self):
        result, output = self.run_fixture("green-not-applicable.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output["decision"], "not_applicable")
        self.assertEqual(output["rule"], "no_path_rule_matched")
        self.assertEqual(output["source_sha"], SOURCE_SHA)
        self.assertRegex(output["changed_paths_sha256"], r"^[0-9a-f]{64}$")
    def test_control_change_requires_all_guards(self):
        result, output = self.run_fixture("green-control-change.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(output["guards"]), 7)
    def test_validation_summary_is_static_fail_closed(self):
        workflow = (ROOT / ".github/workflows/validate.yaml").read_text(encoding="utf-8")
        self.assertIn("REQUIRED_GUARDS", workflow)
        self.assertIn('get("result") != "success"', workflow)
        self.assertNotIn('!= "success" and . != "skipped"', workflow)
    def test_versioned_evidence_matches_every_fixture_output(self):
        evidence = ROOT / "ci" / "offline-guards" / "evidence"
        fixtures = sorted(FIXTURES.glob("*.json"))
        self.assertEqual({p.name for p in evidence.glob("*.json")}, {p.name for p in fixtures})
        for fixture in fixtures:
            result, output = self.run_fixture(fixture.name)
            expected = json.loads(fixture.read_text(encoding="utf-8"))["expected"]
            self.assertEqual(result.returncode, expected["exit_code"], fixture.name)
            self.assertEqual(json.loads((evidence / fixture.name).read_text(encoding="utf-8")), output, fixture.name)
if __name__ == "__main__": unittest.main()
