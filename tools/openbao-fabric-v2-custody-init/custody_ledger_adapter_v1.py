"""CustodyLedgerAdapter v1: in-memory fixture contract, no backend route exists."""
FORBIDDEN={'credential','token','share','rootToken','recoveryKey','payload','url','identity'}
PROVENANCE={'artifact':'custody-ledger-adapter-v1','mode':'synthetic-only','v2Route':False}
class Refusal(Exception):pass
class Uncertain(Refusal):pass
class CustodyLedgerAdapter:
 def __init__(self):self._records={}
 def create(self,r,now):
  if set(r)!={'requestId','expectedVersion','state','expiresAt','metadata'} or FORBIDDEN&set(r['metadata']):raise Refusal('closed schema')
  if r['expectedVersion']!=0 or r['expiresAt']<=now:raise Refusal('stale/expiry')
  if r['requestId'] in self._records:raise Refusal('create-only collision')
  self._records[r['requestId']]={'version':0,'state':r['state'],'expiresAt':r['expiresAt'],'metadata':dict(r['metadata'])};return {'version':0,'state':r['state']}
 def transition(self,key,expected,state,now,uncertain=False):
  if uncertain:raise Uncertain('STOPPED_UNKNOWN')
  r=self._records.get(key)
  if not r or r['expiresAt']<=now or r['version']!=expected:raise Refusal('stale/expiry')
  r['version']+=1;r['state']=state;return {'version':r['version'],'state':state}
