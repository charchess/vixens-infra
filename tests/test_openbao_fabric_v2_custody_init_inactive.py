import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'tools/openbao-fabric-v2-custody-init/inactive.py';s=importlib.util.spec_from_file_location('i',P);i=importlib.util.module_from_spec(s);s.loader.exec_module(i)
R={'envelope':i.ENVELOPE,'witness':True}
class T(unittest.TestCase):
 def test_closed_and_tls_refusal(self):
  with self.assertRaises(i.Refusal):i.inactive_fixture(R,i.FakeCA(),i.FakeLedger(),i.FakeWitness(),b'fake')
  with self.assertRaises(i.Refusal):i.parse_envelope(dict(i.ENVELOPE,endpoint='x'))
 def test_ledger_and_witness_refusals(self):
  for mode in ('collision','crash','timeout'):
   with self.assertRaises(i.Refusal):i.inactive_fixture(R,i.FakeCA(),i.FakeLedger(mode),i.FakeWitness(),b'fake')
  with self.assertRaises(i.Refusal):i.FakeWitness().attest(False)
  with self.assertRaises(i.Refusal):i.FakeWitness().attest(True,True)
 def test_secret_and_window_refusal_before_adapter(self):
  with self.assertRaises(i.Refusal):i.inactive_fixture(dict(R,token='x'),i.FakeCA(),i.FakeLedger(),i.FakeWitness(),b'fake')
  with self.assertRaises(i.Refusal):i.inactive_fixture(R,i.FakeCA(),i.FakeLedger(),i.FakeWitness(),b'fake',expires=1801)
if __name__=='__main__':unittest.main()
