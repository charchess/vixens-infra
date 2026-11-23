import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'tools/openbao-fabric-v2-custody-init/inactive.py';s=importlib.util.spec_from_file_location('i',P);i=importlib.util.module_from_spec(s);s.loader.exec_module(i)
R={'envelope':i.ENVELOPE,'witness':True}; TRUST='SYNTHETIC_NON_GOVERNED_TLS_FIXTURE'
class T(unittest.TestCase):
 def adapters(self):return i.FakeCA(),i.FakeLedger(),i.FakeWitness()
 def zero(self,a):self.assertEqual((a[0].calls,a[1].calls,a[2].calls),(0,0,0))
 def test_nominal_fixture_only_success(self):
  a=self.adapters();x=i.inactive_fixture(R,*a,TRUST);self.assertEqual(x,{'state':'CLOSED','secretPersisted':False});self.assertEqual((a[0].calls,a[1].calls,a[2].calls),(1,1,1))
 def test_pre_adapter_refusals_zero_calls(self):
  cases=[dict(R,token='x'),dict(R,credential='x'),dict(R,share='x'),dict(R,caDer='x'),dict(R,rootToken='x'),dict(R,recoveryKey='x'),dict(R,wrappedPayload='x'),dict(R,policyBody='x'),dict(R,providerPayload='x'),dict(R,command='x'),dict(R,arguments='x'),dict(R,logs='x'),dict(R,rawError='x')]
  for r in cases+[{}, {'envelope':i.ENVELOPE}, {'witness':True}, dict(R,witness=1),dict(R,extra=True)]:
   a=self.adapters()
   with self.assertRaises(i.Refusal):i.inactive_fixture(r,*a,TRUST)
   self.zero(a)
  a=self.adapters()
  with self.assertRaises(i.Refusal):i.inactive_fixture(R,*a,TRUST,expires=1801)
  self.zero(a)
  a=self.adapters()
  with self.assertRaises(i.Refusal):i.inactive_fixture({'envelope':dict(i.ENVELOPE,endpoint='x'),'witness':True},*a,TRUST)
  self.zero(a)
  for mode in ('collision','crash','timeout'):
   a=[*self.adapters()];a[1]=i.FakeLedger(mode)
   with self.assertRaises(i.Refusal):i.inactive_fixture(R,*a,TRUST)
   self.assertEqual((a[0].calls,a[1].calls,a[2].calls),(1,1,0))
 def test_exact_synthetic_trust_only(self):
  class S(str):pass
  class Spoof:
   def __eq__(self,other):return True
  for value in ('', 'fake', 'ca-root-der', b'SYNTHETIC_NON_GOVERNED_TLS_FIXTURE',S(TRUST),Spoof()):
   with self.assertRaises(i.Refusal):i.FakeCA().resolve(value)
if __name__=='__main__':unittest.main()
