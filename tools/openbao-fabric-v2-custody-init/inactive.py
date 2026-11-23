"""Inactive, fixture-only custody-init protocol model. No live transport exists here."""
import hashlib
class Refusal(Exception): pass
ENVELOPE={'endpoint':'https://openbao-fabric-v2.txo-fabric-system.svc:8200','sni':'openbao-fabric-v2.txo-fabric-system.svc','window':1800,'threshold':3,'shares':5}
FORBIDDEN={'token','credential','share','caDer','rootToken','recoveryKey','wrappedPayload','policyBody','providerPayload','command','arguments','logs','rawError'}
def parse_envelope(value):
 if set(value)!=set(ENVELOPE) or value!=ENVELOPE:raise Refusal('closed envelope')
 return dict(value)
class FakeCA:
 def __init__(self):self.calls=0
 def resolve(self,synthetic_fixture):
  self.calls+=1
  if type(synthetic_fixture) is not str or synthetic_fixture!='SYNTHETIC_NON_GOVERNED_TLS_FIXTURE':raise Refusal('TLS mismatch')
class FakeLedger:
 def __init__(self,mode='ok'):self.mode=mode;self.created=False;self.calls=0
 def create_v0(self):
  self.calls+=1
  if self.mode in ('collision','crash','timeout') or self.created:raise Refusal(self.mode)
  self.created=True
class FakeWitness:
 def __init__(self):self.calls=0
 def attest(self,present,expired=False):
  self.calls+=1
  if not present or expired:raise Refusal('witness/authorization refused')
def inactive_fixture(request,ca,ledger,witness,der,now=0,expires=1800):
 if set(request)!={'envelope','witness'} or type(request['witness']) is not bool:raise Refusal('closed request schema')
 if FORBIDDEN & set(request) or expires-now>1800 or expires<=now:raise Refusal('refused before operation')
 parse_envelope(request['envelope']);ca.resolve(der);ledger.create_v0();witness.attest(request.get('witness',False),request.get('expired',False));return {'state':'CLOSED','secretPersisted':False}
