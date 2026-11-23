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
 def test_type_matrix_and_concurrent_transition(self):
  class S(str):pass
  l=x.SyntheticCustodyLedgerFixture();l.create(p(),0);wins=[];fails=[]
  def go():
   try:l.transition('ledger-1',0,'LEASED',1);wins.append(1)
   except x.Refusal:fails.append(1)
  ts=[threading.Thread(target=go) for _ in range(2)];[t.start() for t in ts];[t.join() for t in ts];self.assertEqual((len(wins),len(fails),len(l._l['ledger-1'])),(1,1,2))
  for args in [(S('ledger-1'),0,'LEASED',1,False),('ledger-1',True,'LEASED',1,False),('ledger-1',1,S('CLOSED'),1,False),('ledger-1',1,'CLOSED',True,False),('ledger-1',1,'CLOSED',1,1)]:
   before=len(l._l['ledger-1'])
   with self.assertRaises(x.Refusal):l.transition(*args)
   self.assertEqual(len(l._l['ledger-1']),before)
  for q,n,u in [(p(),True,False),(p(),0,1),(S('bad'),0,False)]:
   with self.assertRaises(x.Refusal):x.SyntheticCustodyLedgerFixture().create(q,n,u)
 def test_uncertain_refusal_no_event_after_closed_stale_expiry(self):
  l=x.SyntheticCustodyLedgerFixture();l.create(p(),0);l.transition('ledger-1',0,'CLOSED',1)
  for expected,now in [(1,1),(0,1),(1,10)]:
   before=len(l._l['ledger-1'])
   with self.assertRaises(x.Refusal):l.transition('ledger-1',expected,'LEASED',now,True)
   self.assertEqual(len(l._l['ledger-1']),before)
 def test_copy_isolation_and_uncertain_illegal_state(self):
  l=x.SyntheticCustodyLedgerFixture();q=p();g=l.create(q,0);q['expiresAt']=999;g['payload']['expiresAt']=999
  self.assertEqual(l._l['ledger-1'][0]['payload']['expiresAt'],10)
  before=len(l._l['ledger-1'])
  with self.assertRaises(x.Refusal):l.transition('ledger-1',0,'BAD',1,True)
  self.assertEqual(len(l._l['ledger-1']),before)
 def test_transition_return_isolation(self):
  l=x.SyntheticCustodyLedgerFixture();l.create(p(),0);a=l.transition('ledger-1',0,'LEASED',1);b=l.transition('ledger-1',1,'WITNESSED',1);before=[(e['payload']['expiresAt'],e['digest']) for e in l._l['ledger-1']]
  a['payload']['expiresAt']=999;b['payload']['expiresAt']=998
  self.assertEqual([(e['payload']['expiresAt'],e['digest']) for e in l._l['ledger-1']],before)