import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'tools/openbao-fabric-v2-custody-init/runner.py'
spec=importlib.util.spec_from_file_location('runner',MOD); runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
REQUEST={'protocolVersion':'v2','fabricRevision':'fixture','endpointIdentity':'https://openbao-fabric-v2.txo-fabric-system.svc:8200','shamirThreshold':3,'shamirShares':5,'requestId':'fixture-request','expectedVersion':0,'expiresAt':1800}
class RunnerTests(unittest.TestCase):
 def test_fixture_request_creates_metadata_only_ledger(self):
  ledger=runner.CeremonyLedger(); receipt=runner.validate_fixture_request(REQUEST,ledger,now=1)
  self.assertEqual(receipt['state'],'requested');self.assertEqual(set(receipt),{'requestId','version','state','fabricRevision','endpointIdentity','custodyAttribution','auditOutcome','revoked','expiresAt'})
  self.assertNotIn('share',json.dumps(receipt).lower())
 def test_refuses_live_and_transport_deviation(self):
  with self.assertRaises(runner.Refusal): runner.main(['invoke'])
  bad=dict(REQUEST,endpointIdentity='https://other:8200')
  with self.assertRaises(runner.Refusal): runner.validate_fixture_request(bad,runner.CeremonyLedger(),now=1)
 def test_cas_window_and_secret_refusals(self):
  with self.assertRaises(runner.Refusal): runner.validate_fixture_request(dict(REQUEST,expiresAt=1802),runner.CeremonyLedger(),now=1)
  with self.assertRaises(runner.Refusal): runner.validate_fixture_request(dict(REQUEST,token='x'),runner.CeremonyLedger(),now=1)
  ledger=runner.CeremonyLedger(); runner.validate_fixture_request(REQUEST,ledger,now=1)
  with self.assertRaises(runner.Refusal): runner.validate_fixture_request(REQUEST,ledger,now=2)
 def test_tls_fixture_digest_and_no_persistence(self):
  self.assertFalse(runner.verify_tls_fixture(b'fixture-ca-der'))
  self.assertFalse(runner.verify_tls_fixture(b'wrong'))
  self.assertFalse(any(p.suffix in {'.json','.log','.db'} for p in (ROOT/'tools/openbao-fabric-v2-custody-init').iterdir() if p.is_file() and p.name not in {'runner.py','README.md'}))
if __name__=='__main__':unittest.main()
