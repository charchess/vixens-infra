"""Offline-only custody-init fixture validator; it never opens sockets or files."""
import argparse, hashlib, re
ENDPOINT='https://openbao-fabric-v2.txo-fabric-system.svc:8200'; SNI='openbao-fabric-v2.txo-fabric-system.svc'; CA_SHA256='85e106a9143f39d1f62180b50878a3ae012992ea0998660581f3b874a3bd7421'
REQUEST_FIELDS={'protocolVersion','fabricRevision','endpointIdentity','shamirThreshold','shamirShares','requestId','expectedVersion','expiresAt'}; RECEIPT_FIELDS={'requestId','version','state','fabricRevision','endpointIdentity','custodyAttribution','auditOutcome','revoked','expiresAt'}
FORBIDDEN={'credential','token','share','recoveryKey','rootToken','wrappedPayload','policyBody','providerPayload','auth','kv','eso','Secret','runtime','kubernetes','argo'}
class Refusal(ValueError): pass
class CeremonyLedger:
 def __init__(self): self._entries={}
 def create(self,r):
  if r['requestId'] in self._entries: raise Refusal('create-only CAS ledger')
  e={'requestId':r['requestId'],'version':0,'state':'requested','fabricRevision':r['fabricRevision'],'endpointIdentity':ENDPOINT,'operatorAttribution':'ABSENT_OFFLINE_FIXTURE','witnessAttribution':'ABSENT_OFFLINE_FIXTURE','auditOutcome':'fixture-accepted','expiresAt':r['expiresAt']};self._entries[r['requestId']]=e;return e
def verify_tls_fixture(ca_der): return hashlib.sha256(ca_der).hexdigest()==CA_SHA256
def _grammar(r):
 if r['protocolVersion']!='v2' or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,63}',r['fabricRevision']) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',r['requestId']):raise Refusal('bounded request grammar')
def validate_fixture_request(r,ledger,now,server_name=SNI):
 if set(r)!=REQUEST_FIELDS or FORBIDDEN&set(r):raise Refusal('closed request schema')
 if r['endpointIdentity']!=ENDPOINT or server_name!=SNI or ':' in server_name:raise Refusal('endpoint/SNI mismatch')
 _grammar(r)
 if r['shamirThreshold']!=3 or r['shamirShares']!=5:raise Refusal('not fixed 3-of-5')
 if not isinstance(r['expiresAt'],int) or r['expiresAt']-now>1800 or r['expiresAt']<=now:raise Refusal('STOPPED_UNKNOWN')
 if r['expectedVersion']!=0:raise Refusal('create-only CAS')
 e=ledger.create(r);receipt={'requestId':e['requestId'],'version':e['version'],'state':e['state'],'fabricRevision':e['fabricRevision'],'endpointIdentity':e['endpointIdentity'],'custodyAttribution':'opaque-witness-receipt','auditOutcome':e['auditOutcome'],'revoked':False,'expiresAt':e['expiresAt']};assert set(receipt)==RECEIPT_FIELDS;return receipt
def main(argv=None):
 p=argparse.ArgumentParser(add_help=False);p.add_argument('command',nargs='?');a=p.parse_args(argv)
 if a.command!='validate-fixture':raise Refusal('offline fixture validation only; live invocation refused')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Refusal as e:raise SystemExit(str(e))
