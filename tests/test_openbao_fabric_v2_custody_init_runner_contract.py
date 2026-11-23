import copy
from pathlib import Path
import unittest
import yaml
ROOT=Path(__file__).resolve().parents[1]; PATH=ROOT/'contracts/openbao-fabric-v2-custody-init-runner.yaml'
IDENTITIES={'runner':'urn:truxonline:openbao-fabric-v2-custody:role:infra-custody-init-runner:v1','operator':'urn:truxonline:openbao-fabric-v2-custody:role:electra-runtime-operator:v1','issuer':'urn:truxonline:openbao-fabric-v2-custody:role:infra-custody-issuer:v1','witness':'urn:truxonline:openbao-fabric-v2-custody:role:lisa-independent-witness:v1'}
SHAMIR={'threshold':3,'shares':5,'material':'ABSENT_OUT_OF_GIT_CUSTODY_REQUIRED'}
CAS={'initial':'requested','transitions':{'requested':['witnessed'],'witnessed':['initialized'],'initialized':['revoked'],'revoked':[]},'terminal':'revoked'}
SCHEMAS={'requestSchema':['protocolVersion','fabricRevision','endpointIdentity','shamirThreshold','shamirShares','requestId','expectedVersion','expiresAt'],'ledgerSchema':['requestId','version','state','fabricRevision','endpointIdentity','operatorAttribution','witnessAttribution','auditOutcome','expiresAt'],'receiptSchema':['requestId','version','state','fabricRevision','endpointIdentity','custodyAttribution','auditOutcome','revoked','expiresAt']}
FORBIDDEN=['credential','token','share','recoveryKey','rootToken','wrappedPayload','policyBody','providerPayload']
REFUSALS={'refuseEndpointMismatch','refuseServerNameMismatch','refuseTrustAnchorMismatch','refuseMethodOutsideInitializeOrRevoke','refuseInvalidTransition','refuseCASVersionMismatch','refuseNonThreeOfFive','refuseActorCollision','refuseExpiredWindow','refuseRetryOrSecondInitOrShareReuse','refuseSecretMaterial'}
SPEC_KEYS={'executable','runtimeCapability','gitOpsConsumer','fixedTransportIdentity','ceremonyWindow','actors','shamir','casStateMachine','requestSchema','ledgerSchema','receiptSchema','forbiddenPersistence','refusalMatrix'}
class Test(unittest.TestCase):
 def load(self): return yaml.safe_load(PATH.read_text())
 def valid(self,d):
  s=d['spec'];self.assertEqual(set(s),SPEC_KEYS);self.assertEqual({k:s[k] for k in ('executable','runtimeCapability','gitOpsConsumer')},{'executable':False,'runtimeCapability':False,'gitOpsConsumer':False})
  self.assertEqual(s['fixedTransportIdentity'],{'endpoint':'https://openbao-fabric-v2.txo-fabric-system.svc:8200','serverName':'openbao-fabric-v2.txo-fabric-system.svc','trustAnchorType':'ca-root-der','trustAnchorSHA256':'85e106a9143f39d1f62180b50878a3ae012992ea0998660581f3b874a3bd7421'})
  self.assertEqual(s['ceremonyWindow'],{'maxSeconds':1800,'expiryState':'STOPPED_UNKNOWN','failedBeforeInitState':'STOPPED_UNKNOWN','failedAfterInitState':'STOPPED_UNKNOWN','retryAllowed':False,'secondInitAllowed':False,'shareReuseAllowed':False})
  self.assertEqual(set(s['actors']),{'runner','operator','issuer','witness','pairwiseDistinct'});self.assertEqual({k:s['actors'][k] for k in IDENTITIES},IDENTITIES);self.assertTrue(s['actors']['pairwiseDistinct']);self.assertEqual(len(set(IDENTITIES.values())),4)
  self.assertEqual(s['shamir'],SHAMIR);self.assertEqual(s['casStateMachine'],CAS)
  for k,v in SCHEMAS.items():self.assertEqual(s[k],{'allowedFields':v})
  self.assertEqual(s['forbiddenPersistence'],FORBIDDEN);self.assertEqual(set(s['refusalMatrix']),REFUSALS);self.assertTrue(s['refusalMatrix']);self.assertTrue(all(s['refusalMatrix'].values()))
 def rejected(self,mutator):
  d=self.load();mutator(d)
  with self.assertRaises(AssertionError):self.valid(d)
 def test_exact_closed_protocol(self):self.valid(self.load())
 def test_rejects_prior_boundary_deviations(self):
  cases=[lambda d:d['spec'].__setitem__('runtime',True),lambda d:d['spec'].__setitem__('Secret','x'),lambda d:d['spec'].__setitem__('token','x'),lambda d:d['spec'].__setitem__('auth','x'),lambda d:d['spec'].__setitem__('kv','x'),lambda d:d['spec'].__setitem__('eso','x'),lambda d:d['spec'].__setitem__('executable',True),lambda d:d['spec']['fixedTransportIdentity'].__setitem__('trustAnchorSHA256','0'*64),lambda d:d['spec']['ceremonyWindow'].__setitem__('maxSeconds',1801),lambda d:d['spec']['ceremonyWindow'].__setitem__('retryAllowed',True),lambda d:d['spec']['actors'].__setitem__('witness',IDENTITIES['operator']),lambda d:d['spec']['actors'].__setitem__('extra','x'),lambda d:d['spec']['actors'].pop('runner'),lambda d:d['spec']['actors'].__setitem__('runner','mutated'),lambda d:d['spec']['actors'].pop('operator'),lambda d:d['spec']['actors'].__setitem__('operator','mutated'),lambda d:d['spec']['actors'].pop('issuer'),lambda d:d['spec']['actors'].__setitem__('issuer','mutated'),lambda d:d['spec']['actors'].pop('witness'),lambda d:d['spec']['actors'].__setitem__('witness','mutated'),lambda d:d['spec']['actors'].pop('pairwiseDistinct'),lambda d:d['spec']['actors'].__setitem__('pairwiseDistinct',False)]
  for case in cases:self.rejected(case)
 def test_rejects_shamir_and_cas_deviations(self):
  for k,v in [('threshold',2),('shares',4),('material','present')]:self.rejected(lambda d,k=k,v=v:d['spec']['shamir'].__setitem__(k,v))
  for state in CAS['transitions']:self.rejected(lambda d,state=state:d['spec']['casStateMachine']['transitions'].__setitem__(state,['invalid']))
  self.rejected(lambda d:d['spec']['casStateMachine'].__setitem__('terminal','initialized'))
 def test_rejects_schema_persistence_and_refusal_deviations(self):
  for schema,fields in SCHEMAS.items():
   for i in range(len(fields)):self.rejected(lambda d,schema=schema,i=i:d['spec'][schema]['allowedFields'].__setitem__(i,'mutated'))
  for i in range(len(FORBIDDEN)):self.rejected(lambda d,i=i:d['spec']['forbiddenPersistence'].__setitem__(i,'mutated'))
  for key in REFUSALS:self.rejected(lambda d,key=key:d['spec']['refusalMatrix'].__setitem__(key,False))
  self.rejected(lambda d:d['spec']['refusalMatrix'].pop(next(iter(REFUSALS))));self.rejected(lambda d:d['spec']['refusalMatrix'].__setitem__('refuseExtra',True))
if __name__=='__main__':unittest.main()
