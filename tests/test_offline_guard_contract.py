"""Regression contract for deterministic, fail-closed validation guards."""
from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHECK=ROOT/"scripts"/"check-offline-guard-contract.py"
FIXTURES=ROOT/"ci"/"offline-guards"/"fixtures"
class OfflineGuardContractTest(unittest.TestCase):
 def source_sha(self): return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 def run_fixture(self,name):
  result=subprocess.run([sys.executable,str(CHECK),"--source-sha",self.source_sha(),str(FIXTURES/name)],cwd=ROOT,capture_output=True,text=True,check=False)
  return result,json.loads(result.stdout)
 def test_required_guard_rejects_each_non_success_state(self):
  for state in ("missing","skipped","cancelled","neutral","timed_out","action_required"):
   with self.subTest(state=state):
    result,out=self.run_fixture(f"red-required-{state}.json"); self.assertEqual(result.returncode,1); self.assertEqual(out["failure"],"required guard non-success"); self.assertEqual(out["failed_guards"],["kustomize-render"]); self.assertEqual(out["guard_statuses"]["kustomize-render"],state)
 def test_candidate_head_is_traced_for_mapped_and_not_applicable(self):
  for fixture in ("green-mapped-kustomize.json","green-not-applicable.json"):
   result,out=self.run_fixture(fixture); self.assertEqual(result.returncode,0); self.assertEqual(out["source_sha"],self.source_sha())
  _,out=self.run_fixture("green-not-applicable.json"); self.assertEqual(out["decision"],"not_applicable"); self.assertEqual(out["rule"],"no_path_rule_matched"); self.assertRegex(out["changed_paths_sha256"],r"^[0-9a-f]{64}$")
 def test_control_change_requires_all_guards(self):
  result,out=self.run_fixture("green-control-change.json"); self.assertEqual(result.returncode,0); self.assertEqual(len(out["guards"]),7)
 def test_workflow_change_maps_three_workflow_guards(self):
  result,out=self.run_fixture("green-workflow-change.json"); self.assertEqual(result.returncode,0); self.assertEqual(out["guards"],["actionlint","scope-boundary","yaml-lint"])
  result,out=self.run_fixture("red-workflow-actionlint-skipped.json"); self.assertEqual(result.returncode,1); self.assertEqual(out["guard_statuses"]["actionlint"],"skipped")
 def test_validation_summary_is_static_fail_closed(self):
  text=(ROOT/".github/workflows/validate.yaml").read_text(); self.assertIn("REQUIRED_GUARDS",text); self.assertIn('get("result") != "success"',text); self.assertNotIn('!= "success" and . != "skipped"',text)
if __name__=="__main__": unittest.main()
