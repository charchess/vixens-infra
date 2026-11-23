import hashlib
import json
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {name: ROOT / f"contracts/durable-custody-ledger-adapter-v1-{name}.yaml" for name in ("provider-selection", "operational-qualification", "recovery-retention")}
BINDING = {"contractRawYamlSha256": "f8914ce4e29f0652be07bc4b5a080e5e0b518a1ba8b3b24f054184800b467105", "canonicalJcsSha256": "4cd234ccc8080ac7ee4803a91321f51cd5ae8377d2c786375bbc0cdd6ab5823c", "provenanceIdentity": "DurableCustodyLedgerAdapterV1Provenance", "provenancePath": "tests/fixtures/durable-custody-ledger-adapter-v1.provenance.yaml", "interface": ["createLedger", "acquireLease", "compareAndAppend", "readVerifiedChain", "closeLease"]}
RULES = {"contractDigest": {"type":"string","pattern":"^sha256:[0-9a-f]{64}$","minLength":71,"maxLength":71}, "vectorDigest": {"type":"string","pattern":"^sha256:[0-9a-f]{64}$","minLength":71,"maxLength":71}, "scope": {"type":"string","enum":["provider-selection","operational-qualification","recovery-retention"]}, "outcome": {"type":"string","enum":["accepted","refused","not-executed"]}, "reportDigest": {"type":"string","pattern":"^sha256:[0-9a-f]{64}$","minLength":71,"maxLength":71}}
PROHIBITED = ["backend-selection","backend-configuration","backend-provisioning","url","identity","credential","adapter-implementation","runner","openbao","kubernetes","argo","gitops","endpoint","host","socket","dsn","tls","secretref","serviceaccount","exec","webhook","transport"]
def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))
class DurableCustodyLedgerOperationalQualificationTests(unittest.TestCase):
 def test_closed_documents_bind_pr132_immutably(self):
  for name,path in CONTRACTS.items():
   d=load(path); s=d["spec"]
   self.assertEqual(set(d),{"apiVersion","kind","metadata","spec"}); self.assertEqual(d["apiVersion"],"custody.truxonline.io/v1"); self.assertEqual(d["kind"],"DurableCustodyLedgerAdapterV1OperationalQualification"); self.assertEqual(d["metadata"],{"name":"durable-custody-ledger-adapter-v1-"+name})
   self.assertEqual(set(s),{"executable","runtimeCapability","pr132ContractPath","pr132Binding","conformanceAttestation","isolationAttestation","prohibitedSurfaces","qualification"}); self.assertFalse(s["executable"]); self.assertFalse(s["runtimeCapability"]); self.assertEqual(s["pr132ContractPath"],"contracts/durable-custody-ledger-adapter-v1.yaml"); self.assertEqual(s["pr132Binding"],BINDING); self.assertEqual(s["prohibitedSurfaces"],PROHIBITED)
 def test_metadata_only_attestation_rules_and_bindings_are_exact(self):
  for path in CONTRACTS.values():
   s=load(path)["spec"]
   self.assertEqual(s["conformanceAttestation"],{"fieldRules":RULES,"bindings":["contractDigest","vectorDigest","scope","outcome","reportDigest"],"additionalProperties":False})
   self.assertEqual(s["isolationAttestation"],{"fieldRules":{k:RULES[k] for k in ("contractDigest","scope","outcome","reportDigest")},"bindings":["contractDigest","scope","outcome","reportDigest"],"additionalProperties":False})
 def test_exact_qualification_gates(self):
  self.assertEqual(load(CONTRACTS["provider-selection"])["spec"]["qualification"],{"providerSelection":"prohibited","requiredReport":"provider-selection-decision-record","gate":"independent-architecture-and-risk-review"})
  self.assertEqual(load(CONTRACTS["operational-qualification"])["spec"]["qualification"],{"operationalExecution":"prohibited","requiredReports":["conformance-report","isolation-report","operational-gate-report"],"gate":"independent-qa-and-runtime-authorization"})
  self.assertEqual(load(CONTRACTS["recovery-retention"])["spec"]["qualification"],{"recoveryExecution":"prohibited","retentionExecution":"prohibited","requiredReports":["recovery-policy-report","retention-policy-report","operational-gate-report"],"gate":"independent-risk-and-retention-authorization"})
 def test_pr132_artifacts_and_binding_are_consistent_and_reject_mutations(self):
  contract = ROOT / "contracts/durable-custody-ledger-adapter-v1.yaml"
  fixture = ROOT / "tests/fixtures/durable-custody-ledger-adapter-v1.oracle.jcs.json"
  provenance = ROOT / "tests/fixtures/durable-custody-ledger-adapter-v1.provenance.yaml"
  raw, jcs, prov = contract.read_bytes(), fixture.read_bytes(), load(provenance)
  self.assertEqual(hashlib.sha256(raw).hexdigest(), BINDING["contractRawYamlSha256"])
  self.assertEqual(hashlib.sha256(jcs).hexdigest(), BINDING["canonicalJcsSha256"])
  self.assertEqual(prov["kind"], BINDING["provenanceIdentity"])
  self.assertEqual(prov["contractRawSha256"], BINDING["contractRawYamlSha256"])
  self.assertEqual(prov["canonicalJcsRawSha256"], BINDING["canonicalJcsSha256"])
  parsed = yaml.safe_load(raw)
  self.assertEqual(json.dumps(parsed, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(), jcs)
  for field in ("contractRawYamlSha256", "canonicalJcsSha256"):
   changed = dict(BINDING); changed[field] = "0" * 64
   self.assertNotEqual(changed, BINDING)
  for artifact in (raw + b" ", jcs + b" "):
   self.assertNotEqual(hashlib.sha256(artifact).hexdigest(), BINDING["contractRawYamlSha256"])
  for path in CONTRACTS.values():
   binding = load(path)["spec"]["pr132Binding"]
   self.assertEqual(binding, BINDING)
   for field in ("contractRawYamlSha256", "canonicalJcsSha256"):
    changed = dict(binding); changed[field] = "f" * 64
    self.assertNotEqual(changed, BINDING)
if __name__ == "__main__": unittest.main()
