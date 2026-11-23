import copy
from pathlib import Path
import unittest
import yaml
ROOT=Path(__file__).resolve().parents[1]; PATH=ROOT/'contracts/openbao-fabric-v2-custody-init-runner.yaml'
SHAMIR={'threshold':3,'shares':5,'material':'ABSENT_OUT_OF_GIT_CUSTODY_REQUIRED'}
CAS={'initial':'requested','transitions':{'requested':['witnessed'],'witnessed':['initialized'],'initialized':['revoked'],'revoked':[]},'terminal':'revoked'}
SCHEMAS={
 'requestSchema':['protocolVersion','fabricRevision','endpointIdentity','shamirThreshold','shamirShares','requestId','expectedVersion','expiresAt'],
 'ledgerSchema':['requestId','version','state','fabricRevision','endpointIdentity','operatorAttribution','witnessAttribution','auditOutcome','expiresAt'],
 'receiptSchema':['requestId','version','state','fabricRevision','endpointIdentity','custodyAttribution','auditOutcome','revoked','expiresAt']}
FORBIDDEN=['credential','token','share','recoveryKey','rootToken','wrappedPayload','policyBody','providerPayload']
REFUSALS={'refuseEndpointMismatch','refuseServerNameMismatch','refuseTrustAnchorMismatch','refuseMethodOutsideInitializeOrRevoke','refuseInvalidTransition','refuseCASVersionMismatch','refuseNonThreeOfFive','refuseActorCollision','refuseExpiredWindow','refuseRetryOrSecondInitOrShareReuse','refuseSecretMaterial'}
class Test(unittest.TestCase):
 def load(self): return yaml.safe_load(PATH.read_text())
 def valid(self,d):
  s=d['spec']
  self.assertEqual(s['shamir'],SHAMIR);self.assertEqual(s['casStateMachine'],CAS)
  for k,v in SCHEMAS.items(): self.assertEqual(s[k],{'allowedFields':v})
  self.assertEqual(s['forbiddenPersistence'],FORBIDDEN)
  self.assertEqual(set(s['refusalMatrix']),REFUSALS);self.assertTrue(s['refusalMatrix']);self.assertTrue(all(s['refusalMatrix'].values()))
 def rejected(self,mutator):
  d=self.load();mutator(d)
  with self.assertRaises(AssertionError):self.valid(d)
 def test_exact_closed_protocol(self): self.valid(self.load())
 def test_rejects_shamir_and_cas_deviations(self):
  for k,v in [('threshold',2),('shares',4),('material','present')]: self.rejected(lambda d,k=k,v=v:d['spec']['shamir'].__setitem__(k,v))
  for state in CAS['transitions']:
   self.rejected(lambda d,state=state:d['spec']['casStateMachine']['transitions'].__setitem__(state,['invalid']))
  self.rejected(lambda d:d['spec']['casStateMachine'].__setitem__('terminal','initialized'))
 def test_rejects_schema_and_persistence_deviations(self):
  for schema,fields in SCHEMAS.items():
   for i in range(len(fields)):
    self.rejected(lambda d,schema=schema,i=i:d['spec'][schema]['allowedFields'].__setitem__(i,'mutated'))
  for i in range(len(FORBIDDEN)): self.rejected(lambda d,i=i:d['spec']['forbiddenPersistence'].__setitem__(i,'mutated'))
 def test_rejects_refusal_deviations(self):
  for key in REFUSALS: self.rejected(lambda d,key=key:d['spec']['refusalMatrix'].__setitem__(key,False))
  self.rejected(lambda d:d['spec']['refusalMatrix'].pop(next(iter(REFUSALS))))
  self.rejected(lambda d:d['spec']['refusalMatrix'].__setitem__('refuseExtra',True))
if __name__=='__main__': unittest.main()
