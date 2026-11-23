import copy
from pathlib import Path
import unittest,yaml
P=Path(__file__).resolve().parents[1]/'contracts/openbao-fabric-v2-custody-init-operational-execution.yaml'
class T(unittest.TestCase):
 def load(self):return yaml.safe_load(P.read_text())['spec']
 def valid(self,s):
  self.assertEqual(set(s),{'executable','runtimeCapability','gitOpsConsumer','executionEnvelope','identities','caDerResolver','externalMetadataCasLedger','witnessAttestation','oneShotInvocationReceipt','stateMachine','noGo'})
  self.assertEqual([s[x] for x in ('executable','runtimeCapability','gitOpsConsumer')],[False,False,False]);e=s['executionEnvelope'];self.assertEqual(e['maxWindowSeconds'],1800);self.assertEqual(e['shamir'],{'threshold':3,'shares':5});self.assertEqual(e['trustAnchorType'],'ca-root-der');self.assertEqual(len(e['trustAnchorSHA256']),64)
  self.assertEqual(set(s['identities']),{'runner','operator','issuer','witness','pairwiseDistinct'});self.assertTrue(s['identities']['pairwiseDistinct']);self.assertEqual(len({s['identities'][x] for x in ('runner','operator','issuer','witness')}),4)
  self.assertEqual(s['externalMetadataCasLedger']['interface'],'append-only-cas');self.assertEqual(s['stateMachine']['expiryState'],'STOPPED_UNKNOWN');self.assertFalse(s['stateMachine']['retryAllowed']);self.assertIn('openbao-runtime',s['noGo'])
 def test_closed(self):self.valid(self.load())
 def test_refusals(self):
  for f,v in [('executable',True),('runtimeCapability',True)]:
   s=copy.deepcopy(self.load());s[f]=v
   with self.assertRaises(AssertionError):self.valid(s)
  for nested,key in [('caDerResolver','caDer'),('externalMetadataCasLedger','share'),('witnessAttestation','token'),('oneShotInvocationReceipt','rootToken')]:self.assertIn(key,self.load()[nested]['forbiddenFields'])
if __name__=='__main__':unittest.main()
