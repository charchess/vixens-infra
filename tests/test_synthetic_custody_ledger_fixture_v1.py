import importlib.util,threading,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/openbao-fabric-v2-custody-init/synthetic_custody_ledger_fixture_v1.py';s=importlib.util.spec_from_file_location('x',P);x=importlib.util.module_from_spec(s);s.loader.exec_module(x)
def p():return {'ledgerId':'ledger-1','requestId':'request-1','expiresAt':10}
class T(unittest.TestCase):
 def test_full_path_and_closed(self):
  l=x.SyntheticCustodyLedgerFixture();g=l.create(p(),0);a=l.transition('ledger-1',0,'LEASED',1);b=l.transition('ledger-1',1,'WITNESSED',1);c=l.transition('ledger-1',2,'CLOSED',1);self.assertIsNone(g['priorDigest']);self.assertEqual((a['priorDigest'],b['priorDigest'],c['priorDigest']),(g['digest'],a['digest'],b['digest']))
  with self.assertRaises(x.Refusal):l.transition('ledger-1',3,'REQUESTED',1)
 def test_uncertain_terminal_event(self):
  l=x.SyntheticCustodyLedgerFixture();l.create(p(),0)
  with self.assertRaises(x.UncertainStorage):l.transition('ledger-1',0,'LEASED',1,True)
  e=l._l['ledger-1'][-1];self.assertEqual((e['version'],e['state'],e['priorDigest']),(1,'UNCERTAIN_STORAGE',l._l['ledger-1'][0]['digest']))
  with self.assertRaises(x.Refusal):l.transition('ledger-1',1,'LEASED',1)
 def test_closed_create_and_concurrency(self):
  l=x.SyntheticCustodyLedgerFixture();wins=[]
  def go():
   try:l.create(p(),0);wins.append(1)
   except x.Refusal:pass
  ts=[threading.Thread(target=go) for _ in range(2)];[t.start() for t in ts];[t.join() for t in ts];self.assertEqual(len(wins),1)
  for q in [{},dict(p(),expiresAt=0),dict(p(),ledgerId='BAD'),dict(p(),extra=1)]:
   with self.assertRaises(x.Refusal):x.SyntheticCustodyLedgerFixture().create(q,0)
if __name__=='__main__':unittest.main()
