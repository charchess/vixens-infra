import importlib.util,threading,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/openbao-fabric-v2-custody-init/custody_ledger_adapter_v1.py';s=importlib.util.spec_from_file_location('l',P);l=importlib.util.module_from_spec(s);s.loader.exec_module(l)
def r(i='a',x=10):return {'requestId':i,'expectedVersion':0,'state':'REQUESTED','expiresAt':x,'metadata':{'fabricRevision':'f'}}
class T(unittest.TestCase):
 def test_closed_create_and_concurrency(self):
  a=l.CustodyLedgerAdapter();wins=[]
  def go():
   try:a.create(r(),0);wins.append(1)
   except l.Refusal:pass
  ts=[threading.Thread(target=go) for _ in range(2)];[x.start() for x in ts];[x.join() for x in ts];self.assertEqual(len(wins),1);self.assertEqual(len(a._r['a']['events']),1)
 def test_refusals_stop_and_stale(self):
  a=l.CustodyLedgerAdapter()
  for x in [dict(r(),requestId='BAD'),dict(r(),metadata={'token':'x'}),dict(r(),expiresAt=0),dict(r(),state='CLOSED')]:
   with self.assertRaises(l.Refusal):a.create(x,0)
  a.create(r(),0)
  with self.assertRaises(l.Refusal):a.transition('a',1,'WITNESSED',1)
  with self.assertRaises(l.Uncertain):a.transition('a',0,'WITNESSED',1,True)
  with self.assertRaises(l.Refusal):a.transition('a',0,'WITNESSED',1)
if __name__=='__main__':unittest.main()
