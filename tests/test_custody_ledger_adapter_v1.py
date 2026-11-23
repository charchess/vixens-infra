import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/openbao-fabric-v2-custody-init/custody_ledger_adapter_v1.py';s=importlib.util.spec_from_file_location('l',P);l=importlib.util.module_from_spec(s);s.loader.exec_module(l)
def req(i='a',x=10):return {'requestId':i,'expectedVersion':0,'state':'REQUESTED','expiresAt':x,'metadata':{'fabricRevision':'fixture'}}
class T(unittest.TestCase):
 def test_provenance_and_create_only_cas(self):
  a=l.CustodyLedgerAdapter();self.assertEqual(l.PROVENANCE,{'artifact':'custody-ledger-adapter-v1','mode':'synthetic-only','v2Route':False});self.assertEqual(a.create(req(),0),{'version':0,'state':'REQUESTED'})
  with self.assertRaises(l.Refusal):a.create(req(),0)
 def test_stale_expiry_uncertain_and_refusals(self):
  a=l.CustodyLedgerAdapter();a.create(req(),0)
  with self.assertRaises(l.Refusal):a.transition('a',1,'WITNESSED',1)
  with self.assertRaises(l.Uncertain):a.transition('a',0,'WITNESSED',1,True)
  with self.assertRaises(l.Refusal):a.create(dict(req('b'),metadata={'token':'x'}),0)
  with self.assertRaises(l.Refusal):a.create(req('c',0),0)
if __name__=='__main__':unittest.main()
