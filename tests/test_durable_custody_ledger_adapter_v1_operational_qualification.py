import hashlib
import json
import re
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {name: ROOT / f"contracts/durable-custody-ledger-adapter-v1-{name}.yaml" for name in ("provider-selection", "operational-qualification", "recovery-retention")}
BINDING = {"contractRawYamlSha256": "f8914ce4e29f0652be07bc4b5a080e5e0b518a1ba8b3b24f054184800b467105", "canonicalJcsSha256": "4cd234ccc8080ac7ee4803a91321f51cd5ae8377d2c786375bbc0cdd6ab5823c", "provenanceIdentity": "DurableCustodyLedgerAdapterV1Provenance", "provenancePath": "tests/fixtures/durable-custody-ledger-adapter-v1.provenance.yaml", "interface": ["createLedger", "acquireLease", "compareAndAppend", "readVerifiedChain", "closeLease"]}
RULES = {"contractDigest": {"type":"string","pattern":"^sha256:[0-9a-f]{64}$","minLength":71,"maxLength":71}, "vectorDigest": {"type":"string","pattern":"^sha256:[0-9a-f]{64}$","minLength":71,"maxLength":71}, "scope": {"type":"string","enum":["provider-selection","operational-qualification","recovery-retention"]}, "outcome": {"type":"string","enum":["accepted","refused","not-executed"]}, "reportDigest": {"type":"string","pattern":"^sha256:[0-9a-f]{64}$","minLength":71,"maxLength":71}}
PROHIBITED = ["backend-selection","backend-configuration","backend-provisioning","url","identity","credential","adapter-implementation","runner","openbao","kubernetes","argo","gitops","endpoint","host","socket","dsn","tls","secretref","serviceaccount","exec","webhook","transport"]
def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))
def valid_attestation(attestation, binding, contract, fixture, provenance):
 try:
  rules = RULES
  if set(attestation) != set(rules): return False
  if attestation["contractDigest"] != "sha256:" + binding["contractRawYamlSha256"]: return False
  if attestation["vectorDigest"] != "sha256:" + binding["canonicalJcsSha256"]: return False
  if type(attestation["reportDigest"]) is not str or re.fullmatch(r"sha256:[0-9a-f]{64}", attestation["reportDigest"]) is None: return False
  if attestation["scope"] not in rules["scope"]["enum"] or attestation["outcome"] not in rules["outcome"]["enum"]: return False
  if any(type(attestation[k]) is not str or len(attestation[k]) < rules[k].get("minLength", 1) or len(attestation[k]) > rules[k].get("maxLength", 10**9) for k in rules): return False
  if hashlib.sha256(contract).hexdigest() != binding["contractRawYamlSha256"] or hashlib.sha256(fixture).hexdigest() != binding["canonicalJcsSha256"]: return False
  return provenance["kind"] == binding["provenanceIdentity"] and provenance["contractRawSha256"] == binding["contractRawYamlSha256"] and provenance["canonicalJcsRawSha256"] == binding["canonicalJcsSha256"]
 except (KeyError, TypeError): return False
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
 def test_closed_attestation_validator_rejects_real_mutations(self):
  c=(ROOT/"contracts/durable-custody-ledger-adapter-v1.yaml").read_bytes(); j=(ROOT/"tests/fixtures/durable-custody-ledger-adapter-v1.oracle.jcs.json").read_bytes(); p=load(ROOT/BINDING["provenancePath"])
  a={"contractDigest":"sha256:"+BINDING["contractRawYamlSha256"],"vectorDigest":"sha256:"+BINDING["canonicalJcsSha256"],"scope":"operational-qualification","outcome":"not-executed","reportDigest":"sha256:"+"0"*64}
  self.assertTrue(valid_attestation(a,BINDING,c,j,p))
  for key,value in (("scope","bad"),("outcome","bad"),("contractDigest","sha256:"+"0"*64),("vectorDigest","sha256:"+"0"*64)):
   m=dict(a); m[key]=value; self.assertFalse(valid_attestation(m,BINDING,c,j,p))
  m=dict(a); m["extra"]="x"; self.assertFalse(valid_attestation(m,BINDING,c,j,p)); m=dict(a); del m["reportDigest"]; self.assertFalse(valid_attestation(m,BINDING,c,j,p))
  for bad in ("sha512:"+"0"*64, "sha256:"+"g"*64, "sha256:"+"0"*63, "x"*71, None, 1, type("DigestSubclass", (str,), {})("sha256:"+"0"*64)):
   m=dict(a); m["reportDigest"]=bad; self.assertFalse(valid_attestation(m,BINDING,c,j,p))
  self.assertFalse(valid_attestation(a,BINDING,c+b" ",j,p)); self.assertFalse(valid_attestation(a,BINDING,c,j+b" ",p)); q=dict(p); q["canonicalJcsRawSha256"]="0"*64; self.assertFalse(valid_attestation(a,BINDING,c,j,q))
if __name__ == "__main__": unittest.main()
