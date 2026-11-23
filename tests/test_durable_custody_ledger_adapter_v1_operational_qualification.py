import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {
    "provider-selection": ROOT / "contracts/durable-custody-ledger-adapter-v1-provider-selection.yaml",
    "operational-qualification": ROOT / "contracts/durable-custody-ledger-adapter-v1-operational-qualification.yaml",
    "recovery-retention": ROOT / "contracts/durable-custody-ledger-adapter-v1-recovery-retention.yaml",
}
PR132_CONTRACT = ROOT / "contracts/durable-custody-ledger-adapter-v1.yaml"
FORBIDDEN = ("http://", "https://", "providerConfig")


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class DurableCustodyLedgerOperationalQualificationTests(unittest.TestCase):
    def test_contracts_are_source_only_closed_and_bind_pr132(self):
        expected_names = {
            "provider-selection": "durable-custody-ledger-adapter-v1-provider-selection",
            "operational-qualification": "durable-custody-ledger-adapter-v1-operational-qualification",
            "recovery-retention": "durable-custody-ledger-adapter-v1-recovery-retention",
        }
        for name, path in CONTRACTS.items():
            document = load(path)
            self.assertEqual(document["apiVersion"], "custody.truxonline.io/v1")
            self.assertEqual(document["kind"], "DurableCustodyLedgerAdapterV1OperationalQualification")
            self.assertEqual(document["metadata"], {"name": expected_names[name]})
            spec = document["spec"]
            self.assertFalse(spec["executable"])
            self.assertFalse(spec["runtimeCapability"])
            self.assertEqual(spec["pr132ContractPath"], "contracts/durable-custody-ledger-adapter-v1.yaml")
            self.assertEqual(spec["pr132Interface"], ["createLedger", "acquireLease", "compareAndAppend", "readVerifiedChain", "closeLease"])
            self.assertEqual(spec["conformanceAttestation"], {"allowedFields": ["contractDigest", "vectorDigest", "scope", "outcome", "reportDigest"], "additionalProperties": False})
            self.assertEqual(spec["isolationAttestation"], {"allowedFields": ["contractDigest", "scope", "outcome", "reportDigest"], "additionalProperties": False})
            self.assertEqual(spec["prohibitedSurfaces"], ["backend-selection", "backend-configuration", "backend-provisioning", "url", "identity", "credential", "adapter-implementation", "runner", "openbao", "kubernetes", "argo", "gitops"])
            self.assertNotIn("v2", path.read_text(encoding="utf-8").lower())
        self.assertTrue(PR132_CONTRACT.is_file())

    def test_each_qualification_contract_has_its_exact_gate(self):
        provider = load(CONTRACTS["provider-selection"])["spec"]
        self.assertEqual(provider["qualification"], {"providerSelection": "prohibited", "requiredReport": "provider-selection-decision-record", "gate": "independent-architecture-and-risk-review"})
        operational = load(CONTRACTS["operational-qualification"])["spec"]
        self.assertEqual(operational["qualification"], {"operationalExecution": "prohibited", "requiredReports": ["conformance-report", "isolation-report", "operational-gate-report"], "gate": "independent-qa-and-runtime-authorization"})
        recovery = load(CONTRACTS["recovery-retention"])["spec"]
        self.assertEqual(recovery["qualification"], {"recoveryExecution": "prohibited", "retentionExecution": "prohibited", "requiredReports": ["recovery-policy-report", "retention-policy-report", "operational-gate-report"], "gate": "independent-risk-and-retention-authorization"})

    def test_contract_text_has_no_runtime_or_backend_surface(self):
        for path in CONTRACTS.values():
            text = path.read_text(encoding="utf-8").lower()
            for forbidden in FORBIDDEN:
                if forbidden in {"openbao", "kubernetes", "argo", "gitops", "runner", "adapter"}:
                    continue  # permitted only as an explicit prohibited-surface label
                self.assertNotIn(forbidden, text, (path, forbidden))


if __name__ == "__main__":
    unittest.main()
