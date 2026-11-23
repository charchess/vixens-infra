import copy
from pathlib import Path
import unittest
import yaml
ROOT=Path(__file__).resolve().parents[1]; PATH=ROOT/'contracts/openbao-fabric-v2-custody-init-runner.yaml'
IDENTITIES={
 'runner':'urn:truxonline:openbao-fabric-v2-custody:role:infra-custody-init-runner:v1',
 'operator':'urn:truxonline:openbao-fabric-v2-custody:role:electra-runtime-operator:v1',
 'issuer':'urn:truxonline:openbao-fabric-v2-custody:role:infra-custody-issuer:v1',
 'witness':'urn:truxonline:openbao-fabric-v2-custody:role:lisa-independent-witness:v1'}
class Test(unittest.TestCase):
 def load(self):return yaml.safe_load(PATH.read_text())
 def valid(self,d):
  s=d['spec'];self.assertEqual(set(s),{'executable','runtimeCapability','gitOpsConsumer','fixedTransportIdentity','ceremonyWindow','actors','shamir','casStateMachine','requestSchema','ledgerSchema','receiptSchema','forbiddenPersistence','refusalMatrix'});self.assertEqual({k:s[k] for k in ('executable','runtimeCapability','gitOpsConsumer')},{'executable':False,'runtimeCapability':False,'gitOpsConsumer':False})
  self.assertEqual(s['fixedTransportIdentity'],{'endpoint':'https://openbao-fabric-v2.txo-fabric-system.svc:8200','serverName':'openbao-fabric-v2.txo-fabric-system.svc','trustAnchorType':'ca-root-der','trustAnchorSHA256':'85e106a9143f39d1f62180b50878a3ae012992ea0998660581f3b874a3bd7421'})
  self.assertEqual(s['ceremonyWindow'],{'maxSeconds':1800,'expiryState':'STOPPED_UNKNOWN','failedBeforeInitState':'STOPPED_UNKNOWN','failedAfterInitState':'STOPPED_UNKNOWN','retryAllowed':False,'secondInitAllowed':False,'shareReuseAllowed':False})
  self.assertEqual({k:s['actors'][k] for k in IDENTITIES},IDENTITIES);self.assertTrue(s['actors']['pairwiseDistinct']);self.assertEqual(len(set(IDENTITIES.values())),4)
  self.assertTrue(all(s['refusalMatrix'].values()))
 def test_closed(self):self.valid(self.load())
 def test_refuses_trust_window_and_actor_mutations(self):
  d=self.load()
  for path,value in [(('fixedTransportIdentity','trustAnchorSHA256'),'0'*64),(('ceremonyWindow','maxSeconds'),1801),(('ceremonyWindow','retryAllowed'),True),(('actors','witness'),IDENTITIES['operator'])]:
   m=copy.deepcopy(d);m['spec'][path[0]][path[1]]=value
   with self.assertRaises(AssertionError):self.valid(m)
 def test_refuses_extra_runtime_keys(self):
  d=self.load()
  for key in ('runtime','token','Secret','auth','kv','eso'):
   m=copy.deepcopy(d);m['spec'][key]='forbidden'
   with self.assertRaises(AssertionError):self.valid(m)
if __name__=='__main__':unittest.main()
