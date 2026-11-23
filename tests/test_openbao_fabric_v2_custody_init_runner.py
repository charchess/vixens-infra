import importlib.util,json,hashlib,socket
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'tools/openbao-fabric-v2-custody-init/runner.py';spec=importlib.util.spec_from_file_location('runner',MOD);runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
REQUEST={'protocolVersion':'v2','fabricRevision':'fixture','endpointIdentity':'https://openbao-fabric-v2.txo-fabric-system.svc:8200','shamirThreshold':3,'shamirShares':5,'requestId':'fixture-request','expectedVersion':0,'expiresAt':1800}
class RunnerTests(unittest.TestCase):
 def no_io(self,fn):
  old=socket.create_connection;socket.create_connection=lambda *a,**k:(_ for _ in ()).throw(AssertionError('network'))
  try:return fn()
  finally:socket.create_connection=old
 def test_success_is_metadata_only_and_no_io(self):
  receipt=self.no_io(lambda:runner.validate_fixture_request(REQUEST,runner.CeremonyLedger(),1,runner.SNI));self.assertEqual(receipt['state'],'requested');self.assertNotIn('share',json.dumps(receipt).lower())
 def test_sni_and_tls_synthetic_fixture(self):
  der=b'synthetic-nonsecret-ca-der';digest=hashlib.sha256(der).hexdigest()
  helper_spec=importlib.util.spec_from_file_location('fixture_helper',ROOT/'tests/test_tls_fixture_helper.py');helper=importlib.util.module_from_spec(helper_spec);helper_spec.loader.exec_module(helper)
  self.assertTrue(helper.matches_digest(der,digest));self.assertFalse(helper.matches_digest(der,'0'*64));self.assertFalse(runner.verify_tls_fixture(der))
  with self.assertRaises(TypeError):runner.verify_tls_fixture(der,digest)
  with self.assertRaises(runner.Refusal):runner.validate_fixture_request(REQUEST,runner.CeremonyLedger(),1,'openbao-fabric-v2.txo-fabric-system.svc:8200')
 def test_grammar_expiry_and_live_refuse_without_io(self):
  for r in [dict(REQUEST,requestId='BAD'),dict(REQUEST,fabricRevision='../bad'),dict(REQUEST,protocolVersion='v3'),dict(REQUEST,expiresAt=1802)]:
   with self.assertRaises(runner.Refusal):self.no_io(lambda r=r:runner.validate_fixture_request(r,runner.CeremonyLedger(),1))
  with self.assertRaises(runner.Refusal):self.no_io(lambda:runner.main(['invoke']))
if __name__=='__main__':unittest.main()
