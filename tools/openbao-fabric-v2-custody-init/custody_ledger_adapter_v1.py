"""Synthetic memory-only CustodyLedgerAdapter v1; no route/client exists."""
import hashlib,re,threading
FORBIDDEN={'credential','token','share','rootToken','recoveryKey','payload','url','identity'};ALLOW={'fabricRevision','endpointIdentity','auditOutcome'};STATES={'REQUESTED':['WITNESSED'],'WITNESSED':['CLOSED'],'CLOSED':[],'STOPPED_UNKNOWN':[]}
class Refusal(Exception):pass
class Uncertain(Refusal):pass
class CustodyLedgerAdapter:
 def __init__(self):self._r={};self._lock=threading.Lock()
 def create(self,r,now):
  if set(r)!={'requestId','expectedVersion','state','expiresAt','metadata'} or not isinstance(r['requestId'],str) or not re.fullmatch('[a-z0-9-]{1,64}',r['requestId']) or r['expectedVersion']!=0 or r['state']!='REQUESTED' or r['expiresAt']<=now or set(r['metadata'])-ALLOW or FORBIDDEN&set(r['metadata']):raise Refusal('closed create')
  with self._lock:
   if r['requestId'] in self._r:raise Refusal('collision')
   self._r[r['requestId']]={'version':0,'state':'REQUESTED','expiresAt':r['expiresAt'],'events':[self._event(0,'REQUESTED',r['metadata'])]}
   return {'version':0,'state':'REQUESTED'}
 def _event(self,v,state,m):return {'version':v,'state':state,'stateDigest':hashlib.sha256((str(v)+state+repr(sorted(m.items()))).encode()).hexdigest()}
 def transition(self,k,expected,state,now,uncertain=False):
  with self._lock:
   r=self._r.get(k)
   if uncertain:
    if r:r['state']='STOPPED_UNKNOWN'
    raise Uncertain('STOPPED_UNKNOWN')
   if not r or r['state']=='STOPPED_UNKNOWN' or r['expiresAt']<=now or r['version']!=expected or state not in STATES.get(r['state'],[]):raise Refusal('closed transition')
   r['version']+=1;r['state']=state;r['events'].append(self._event(r['version'],state,{}));return {'version':r['version'],'state':state}
