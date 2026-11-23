from pathlib import Path
import unittest,yaml
P=Path(__file__).resolve().parents[1]/'contracts/durable-custody-ledger-adapter-v1.yaml'
class T(unittest.TestCase):
 def test_closed(self):
  s=yaml.safe_load(P.read_text())['spec'];self.assertEqual(set(s),{'executable','runtimeCapability','allowedInterface','requiredMutationFields','guarantees','eventSchema','attestationSchema','forbiddenMethods','conformanceVectors'});self.assertEqual((s['executable'],s['runtimeCapability']),(False,False));self.assertEqual(s['allowedInterface'],['create','lease','transition','close','attest']);self.assertEqual(s['requiredMutationFields'],['ledgerId','expectedVersion','headDigest','leaseId','expiresAt']);self.assertIn('append-only',s['guarantees']);self.assertEqual(s['conformanceVectors']['fixture'],'SyntheticCustodyLedgerFixture/v1');self.assertIn('credential',s['eventSchema']['forbiddenFields']);self.assertIn('network',s['forbiddenMethods'])
if __name__=='__main__':unittest.main()
