"""SyntheticCustodyLedgerFixture v1: source-only deterministic in-memory fixture."""
import hashlib,json,re,threading,copy
class Refusal(Exception):pass
class UncertainStorage(Refusal):pass
TRANS={'REQUESTED':{'LEASED','CLOSED'},'LEASED':{'WITNESSED','UNCERTAIN_STORAGE','CLOSED'},'WITNESSED':{'CLOSED'},'UNCERTAIN_STORAGE':set(),'CLOSED':set()}; TERMINAL={'UNCERTAIN_STORAGE','CLOSED'}
def digest(kind,payload,prior=''):
 return hashlib.sha256(('SyntheticCustodyLedgerFixture/v1\\0'+kind+'\\0'+prior+'\\0'+json.dumps(payload,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
def valid(p):return set(p)=={'ledgerId','requestId','expiresAt'} and all(type(p[x]) is str and re.fullmatch('[a-z0-9-]{1,64}',p[x]) for x in ('ledgerId','requestId')) and type(p['expiresAt']) is int
class SyntheticCustodyLedgerFixture:
 def __init__(self):self._l={};self._lock=threading.Lock()
 def create(self,p,now,uncertain=False):
  if type(p) is not dict or type(now) is not int or type(uncertain) is not bool or uncertain:raise Refusal('closed boundary')
  if not valid(p) or p['expiresAt']<=now:raise Refusal('closed genesis')
  with self._lock:
   if p['ledgerId'] in self._l:raise Refusal('CAS')
   payload=copy.deepcopy(p);e={'kind':'genesis','version':0,'state':'REQUESTED','payload':payload,'priorDigest':None};e['digest']=digest('genesis',e);self._l[p['ledgerId']]=[e];return copy.deepcopy(e)
 def transition(self,lid,expected,next_state,now,uncertain=False):
  if type(lid) is not str or type(expected) is not int or type(next_state) is not str or type(now) is not int or type(uncertain) is not bool:raise Refusal('closed boundary')
  with self._lock:
   es=self._l.get(lid)
   if uncertain:
    if not es:raise Refusal('missing')
    last=es[-1]
    if type(expected)is not int or type(now)is not int or type(next_state)is not str or last['version']!=expected or last['payload']['expiresAt']<=now or last['state'] in TERMINAL or next_state not in TRANS[last['state']]:raise Refusal('CAS/expiry/terminal')
    e={'kind':'event','version':last['version']+1,'state':'UNCERTAIN_STORAGE','payload':last['payload'],'priorDigest':last['digest']};e['digest']=digest('event',e,last['digest']);es.append(e)
    raise UncertainStorage('UNCERTAIN_STORAGE')
   if not es:raise Refusal('missing')
   last=es[-1]
   if type(expected)is not int or last['version']!=expected or last['payload']['expiresAt']<=now or next_state not in TRANS[last['state']]:raise Refusal('CAS/transition')
   e={'kind':'event','version':expected+1,'state':next_state,'payload':last['payload'],'priorDigest':last['digest']};e['digest']=digest('event',e,last['digest']);es.append(e);return e.copy()
