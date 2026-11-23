import copy
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "contracts/openbao-fabric-v2-phase2-custody-issuer.yaml"
FABRIC_SHA = "89d23b3e2b2011b53f21c605714beffb974e3d49"
FABRIC_PATH = "apps/60-services/txo-fabric/openbao-fabric-v2-phase2-custody-bootstrap/contract.yaml"
SENTINEL = "ABSENT_SEPARATE_VIXENS_INFRA_CONTRACT_REQUIRED"

class Phase2CustodyIssuerContractTest(unittest.TestCase):
    def load(self):
        return yaml.safe_load(PATH.read_text())

    def validate(self, document):
        self.assertEqual(set(document), {"apiVersion", "kind", "metadata", "spec"})
        self.assertEqual(document["kind"], "OpenBaoFabricV2Phase2CustodyIssuerContract")
        self.assertEqual(set(document["metadata"]), {"name"})
        spec = document["spec"]
        self.assertEqual(set(spec), {"executable", "runtimeCapability", "gitOpsConsumer", "requiresExistingAuthenticatedAuthority", "cannotBootstrapInitialCustodyAlone", "fabricImmutableVersionBinding", "offlineIssuerEnvelope", "electraDelegationEnvelope", "revokeReceiptSchema", "refusalModel"})
        self.assertEqual({key: spec[key] for key in ("executable", "runtimeCapability", "gitOpsConsumer")}, {"executable": False, "runtimeCapability": False, "gitOpsConsumer": False})
        self.assertTrue(spec["requiresExistingAuthenticatedAuthority"])
        self.assertTrue(spec["cannotBootstrapInitialCustodyAlone"])
        self.assertEqual(spec["fabricImmutableVersionBinding"], {"repository": "charchess/vixens-fabric", "revision": FABRIC_SHA, "contractPath": FABRIC_PATH, "requiredSentinel": SENTINEL})
        self.assertEqual(set(spec["offlineIssuerEnvelope"]), {"material", "policyPayload"})
        self.assertEqual(spec["electraDelegationEnvelope"], {"identityRef": "EXISTING_AUTHENTICATED_ELECTRA_RECOVERY_IDENTITY_REQUIRED", "ttlSeconds": 900, "renewable": False, "storage": "memory-only", "wrapped": True})
        self.assertEqual(spec["revokeReceiptSchema"], {"version": "v1", "allowedFields": ["phase", "phaseHash", "fabricRevision", "custodyAttribution", "auditOutcome", "revoked"], "forbiddenFields": ["credential", "token", "wrappedPayload", "policyBody", "providerPayload", "root", "share"]})
        self.assertEqual(set(spec["refusalModel"]), {"refuseMissingAuthority", "refuseRevisionMismatch", "refuseMissingSentinel", "refuseTTLAbove900Seconds", "refuseRenewableOrPersistentOrUnwrappedDelegation", "refuseCredentialOrPayloadMaterial"})
        self.assertTrue(all(spec["refusalModel"].values()))

    def test_contract_is_structurally_closed(self):
        self.validate(self.load())

    def test_delegation_property_removal_or_substitution_is_refused(self):
        document = self.load()
        for key in ("ttlSeconds", "renewable", "storage", "wrapped"):
            mutated = copy.deepcopy(document)
            del mutated["spec"]["electraDelegationEnvelope"][key]
            with self.assertRaises(AssertionError, msg=key): self.validate(mutated)
        for key, value in (("ttlSeconds", 901), ("renewable", True), ("storage", "disk"), ("wrapped", False)):
            mutated = copy.deepcopy(document)
            mutated["spec"]["electraDelegationEnvelope"][key] = value
            with self.assertRaises(AssertionError, msg=key): self.validate(mutated)

    def test_extra_action_runtime_or_custody_keys_are_refused(self):
        document = self.load()
        for key in ("action", "runtime", "issuer", "policy", "auth", "kv", "eso", "token", "Secret"):
            mutated = copy.deepcopy(document)
            mutated["spec"][key] = "forbidden"
            with self.assertRaises(AssertionError, msg=key): self.validate(mutated)

if __name__ == '__main__': unittest.main()
