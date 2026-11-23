"""Offline-only custody-init fixture validator; never contacts OpenBao or Kubernetes."""
import argparse, hashlib

ENDPOINT='https://openbao-fabric-v2.txo-fabric-system.svc:8200'
SNI='openbao-fabric-v2.txo-fabric-system.svc'
CA_SHA256='85e106a9143f39d1f62180b50878a3ae012992ea0998660581f3b874a3bd7421'
REQUEST_FIELDS={'protocolVersion','fabricRevision','endpointIdentity','shamirThreshold','shamirShares','requestId','expectedVersion','expiresAt'}
RECEIPT_FIELDS={'requestId','version','state','fabricRevision','endpointIdentity','custodyAttribution','auditOutcome','revoked','expiresAt'}
FORBIDDEN={'credential','token','share','recoveryKey','rootToken','wrappedPayload','policyBody','providerPayload','auth','kv','eso','Secret','runtime','kubernetes','argo'}
class Refusal(ValueError): pass
class CeremonyLedger:
 def __init__(self): self._entries={}
 def create(self,request,now):
  if request['requestId'] in self._entries: raise Refusal('create-only CAS ledger')
  entry={'requestId':request['requestId'],'version':0,'state':'requested','fabricRevision':request['fabricRevision'],'endpointIdentity':ENDPOINT,'operatorAttribution':'ABSENT_OFFLINE_FIXTURE','witnessAttribution':'ABSENT_OFFLINE_FIXTURE','auditOutcome':'fixture-accepted','expiresAt':request['expiresAt']}
  self._entries[request['requestId']]=entry;return entry
def verify_tls_fixture(ca_der): return hashlib.sha256(ca_der).hexdigest()==CA_SHA256
def validate_fixture_request(request,ledger,now):
 if set(request)!=REQUEST_FIELDS: raise Refusal('closed request schema')
 if FORBIDDEN & set(request): raise Refusal('sensitive input')
 if request['endpointIdentity']!=ENDPOINT: raise Refusal('endpoint/SNI mismatch')
 if request['shamirThreshold']!=3 or request['shamirShares']!=5: raise Refusal('not fixed 3-of-5')
 if not isinstance(request['expiresAt'],int) or request['expiresAt']-now>1800 or request['expiresAt']<=now: raise Refusal('STOPPED_UNKNOWN')
 if request['expectedVersion']!=0: raise Refusal('create-only CAS')
 entry=ledger.create(request,now)
 receipt={'requestId':entry['requestId'],'version':entry['version'],'state':entry['state'],'fabricRevision':entry['fabricRevision'],'endpointIdentity':entry['endpointIdentity'],'custodyAttribution':'opaque-witness-receipt','auditOutcome':entry['auditOutcome'],'revoked':False,'expiresAt':entry['expiresAt']}
 assert set(receipt)==RECEIPT_FIELDS
 return receipt
def main(argv=None):
 p=argparse.ArgumentParser(add_help=False);p.add_argument('command',nargs='?');args=p.parse_args(argv)
 if args.command!='validate-fixture': raise Refusal('offline fixture validation only; live invocation refused')
 return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Refusal as e: raise SystemExit(str(e))
