import copy
from pathlib import Path
import unittest,yaml
P=Path(__file__).resolve().parents[1]/'contracts/durable-custody-ledger-adapter-v1.yaml'
class T(unittest.TestCase):
 def load(self):return yaml.safe_load(P.read_text())['spec']
 def valid(self,s):
  self.assertEqual(set(s),{'executable','runtimeCapability','scalarMetadata','forbiddenTokens','operations','terminalStates','guarantees'});self.assertEqual((s['executable'],s['runtimeCapability']),(False,False));self.assertEqual(s['scalarMetadata']['allowed'],['requestId','ledgerId','version','state','digest','priorDigest','expiresAt','auditOutcome']);self.assertTrue(s['scalarMetadata']['forbidNested']);self.assertIn('jwt',s['forbiddenTokens']);self.assertEqual(set(s['operations']),{'create','lease','transition','close','attest'});self.assertIn('create',s['operations']);self.assertEqual(set(s['operations']['create']),{'input','output','pre','post'});self.assertEqual(s['operations']['create']['pre'],'create-only');self.assertIn('head-equality',s['operations']['transition']['pre']);self.assertEqual(s['terminalStates'],['CLOSED','UNCERTAIN_STORAGE']);self.assertIn('no-further-mutation',s['guarantees'])
 def test_closed(self):self.valid(self.load())
 def test_mutations_refused(self):
  for path,key,val in [('scalarMetadata','forbidNested',False),('operations','route',{}),('operations','create',{})]:
   s=copy.deepcopy(self.load());s[path][key]=val if isinstance(s[path],dict) else val
   with self.assertRaises(AssertionError):self.valid(s)
if __name__=='__main__':unittest.main()
