import importlib.util,threading,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/openbao-fabric-v2-custody-init/synthetic_custody_ledger_fixture_v1.py';s=importlib.util.spec_from_file_location('x',P);x=importlib.util.module_from_spec(s);s.loader.exec_module(x)
def p():return {'ledgerId':'ledger-1','requestId':'request-1','expiresAt':10}
class T(unittest.TestCase):
 def test_chain_and_closed_transitions(self):
  l=x.SyntheticCustodyLedgerFixture();g=l.create(p(),0);e=l.transition('ledger-1',0,'LEASED',1);self.assertEqual(e['priorDigest'],g['digest']);self.assertEqual(len(e['digest']),64)
  with self.assertRaises(x.Refusal):l.transition('ledger-1',1,'REQUESTED',1)
 def test_uncertain_no_mutation_and_concurrency(self):
  l=x.SyntheticCustodyLedgerFixture();l.create(p(),0);before=list(l._l['ledger-1'])
  with self.assertRaises(x.UncertainStorage):l.transition('ledger-1',0,'LEASED',1,True)
  self.assertEqual(l._l['ledger-1'],before);wins=[]
  def go():
   try:l.transition('ledger-1',0,'LEASED',1);wins.append(1)
   except x.Refusal:pass
  ts=[threading.Thread(target=go) for _ in range(2)];[t.start() for t in ts];[t.join() for t in ts];self.assertEqual(len(wins),1)
 def test_closed_genesis(self):
  l=x.SyntheticCustodyLedgerFixture()
  for q in [{},dict(p(),expiresAt=0),dict(p(),ledgerId='BAD')]:
   with self.assertRaises(x.Refusal):l.create(q,0)
if __name__=='__main__':unittest.main()
