import copy
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "contracts/openbao-fabric-v2-custody-init-runner.yaml"

class CustodyInitRunnerContractTest(unittest.TestCase):
    def load(self): return yaml.safe_load(PATH.read_text())
    def validate(self, d):
        self.assertEqual(d["kind"], "OpenBaoFabricV2CustodyInitRunnerContract")
        s=d["spec"]
        self.assertEqual(set(s), {"executable", "runtimeCapability", "gitOpsConsumer", "fixedTransportIdentity", "shamir", "actors", "casStateMachine", "requestSchema", "ledgerSchema", "receiptSchema", "forbiddenPersistence", "refusalMatrix"})
        self.assertEqual({k:s[k] for k in ("executable","runtimeCapability","gitOpsConsumer")},{"executable":False,"runtimeCapability":False,"gitOpsConsumer":False})
        self.assertEqual(s["fixedTransportIdentity"],{"endpoint":"https://openbao-fabric-v2.txo-fabric-system.svc:8200","serverName":"openbao-fabric-v2.txo-fabric-system.svc","trustIdentity":"openbao-fabric-v2-ca"})
        self.assertEqual(s["shamir"],{"threshold":3,"shares":5,"material":"ABSENT_OUT_OF_GIT_CUSTODY_REQUIRED"})
        self.assertTrue(s["actors"]["distinctOperatorAndWitness"])
        self.assertEqual(s["casStateMachine"],{"initial":"requested","transitions":{"requested":["witnessed"],"witnessed":["initialized"],"initialized":["revoked"],"revoked":[]},"terminal":"revoked"})
        self.assertEqual(s["requestSchema"]["allowedFields"],["protocolVersion","fabricRevision","endpointIdentity","shamirThreshold","shamirShares","requestId","expectedVersion"])
        self.assertTrue(all(s["refusalMatrix"].values()))
        forbidden={"Secret","ServiceAccount","Job","CronJob","Application","ExternalSecret","SecretStore","token","share","policy","auth","kv","eso"}
        self.assertFalse(forbidden & set(s))
    def test_contract_is_closed_metadata_only(self): self.validate(self.load())
    def test_refuses_cas_and_transport_mutations(self):
        d=self.load()
        for path,value in [(("shamir","threshold"),2),(("fixedTransportIdentity","serverName"),"other"),(("actors","distinctOperatorAndWitness"),False),(("casStateMachine","terminal"),"initialized")]:
            m=copy.deepcopy(d);m["spec"][path[0]][path[1]]=value
            with self.assertRaises(AssertionError): self.validate(m)
    def test_refuses_secret_and_runtime_keys(self):
        d=self.load()
        for key in ("token","share","Secret","auth","kv","eso","runtime"):
            m=copy.deepcopy(d);m["spec"][key]="forbidden"
            with self.assertRaises(AssertionError): self.validate(m)
if __name__=='__main__': unittest.main()
