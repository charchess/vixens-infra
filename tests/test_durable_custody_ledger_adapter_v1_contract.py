import copy
from pathlib import Path
import unittest,yaml
P=Path(__file__).resolve().parents[1]/'contracts/durable-custody-ledger-adapter-v1.yaml'
class T(unittest.TestCase):
 def load(self):return yaml.safe_load(P.read_text())['spec']
 def valid(self,s):
  self.assertEqual(set(s),{'executable','runtimeCapability','metadataRules','forbiddenTokens','operations','casInvariants','terminalStates','guarantees'});self.assertEqual((s['executable'],s['runtimeCapability']),(False,False));self.assertEqual(set(s['metadataRules']),{'requestId','ledgerId','version','state','digest','priorDigest','expiresAt','auditOutcome'});self.assertEqual(s['operations'],{'create':{'input':['ledgerId','requestId','expectedVersion','expiresAt'],'output':['version','state','digest'],'pre':['create-only'],'post':['version-0','priorDigest-null']},'lease':{'input':['ledgerId','expectedVersion','expectedHeadDigest','leaseId','expiresAt'],'output':['version','resultHeadDigest','leaseId'],'pre':['atomic-tuple-equality'],'post':['atomic-consume','nonreplay','expiry']},'transition':{'input':['ledgerId','expectedVersion','expectedHeadDigest','nextState'],'output':['resultVersion','state','priorDigest','resultHeadDigest'],'pre':['atomic-tuple-equality','legal-transition'],'post':['exact-next-version','exact-next-head','priorDigest-linkage','stale-concurrent-refusal']},'close':{'input':['ledgerId','expectedVersion','expectedHeadDigest'],'output':['resultVersion','state','resultHeadDigest'],'pre':['atomic-tuple-equality'],'post':['terminal-closure']},'attest':{'input':['owner','contractRevision','vectorDigest','ledgerId','expectedVersion','expectedHeadDigest','leaseId','expiresAt'],'output':['owner','contractRevision','vectorDigest','ledgerId','expectedVersion','resultVersion','resultHeadDigest','eventDigest','consumedLeaseId','auditOutcome','expiresAt','terminalClosed'],'pre':['atomic-tuple-equality','lease-expiry'],'post':['self-verifiable','lease-consumed','terminal-closure']}});self.assertEqual(s['casInvariants']['atomicTuple'],['expectedVersion','expectedHeadDigest']);self.assertEqual(s['casInvariants']['lease'],['atomic-consume','nonreplay','expiry']);self.assertEqual(s['terminalStates'],['CLOSED','UNCERTAIN_STORAGE'])
 def test_closed(self):self.valid(self.load())
 def test_mutation_matrix(self):
  s=self.load()
  for key in ['casInvariants','terminalStates']:
   m=copy.deepcopy(s);m.pop(key)
   with self.assertRaises(AssertionError):self.valid(m)
  for key in s['operations']:
   m=copy.deepcopy(s);m['operations'].pop(key)
   with self.assertRaises(AssertionError):self.valid(m)
  for key in s['metadataRules']:
   m=copy.deepcopy(s);m['metadataRules'].pop(key)
   with self.assertRaises(AssertionError):self.valid(m)
  for token in s['forbiddenTokens']:
   self.assertIsInstance(token,str)
if __name__=='__main__':unittest.main()
