import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "contracts/openbao-fabric-v2-phase2-custody-issuer.yaml"

class Phase2CustodyIssuerContractTest(unittest.TestCase):
    def test_offline_issuer_contract_is_immutable_and_non_executable(self):
        source = PATH.read_text()
        for expected in ["kind: OpenBaoFabricV2Phase2CustodyIssuerContract", "executable: false", "runtimeCapability: false", "gitOpsConsumer: false", "repository: charchess/vixens-fabric", "revision: 89d23b3e2b2011b53f21c605714beffb974e3d49", "requiredSentinel: ABSENT_SEPARATE_VIXENS_INFRA_CONTRACT_REQUIRED", "ttlSeconds: 900", "renewable: false", "storage: memory-only", "wrapped: true"]:
            self.assertIn(expected, source)
        for forbidden in ["kind: Secret", "kind: ServiceAccount", "kind: Job", "kind: CronJob", "kind: Application", "kind: ExternalSecret", "kind: SecretStore", "token:", "credential:", "policyBody:", "providerPayload:", "listener:", "auth:", "kv:", "eso:"]:
            self.assertNotIn(forbidden, source)

    def test_refusal_and_receipt_envelopes_are_closed(self):
        source = PATH.read_text()
        for expected in ["refuseRevisionMismatch: true", "refuseTTLAbove900Seconds: true", "refuseRenewableOrPersistentOrUnwrappedDelegation: true", "refuseCredentialOrPayloadMaterial: true", "allowedFields: [phase, phaseHash, fabricRevision, custodyAttribution, auditOutcome, revoked]", "forbiddenFields: [credential, token, wrappedPayload, policyBody, providerPayload, root, share]"]:
            self.assertIn(expected, source)

if __name__ == '__main__': unittest.main()
