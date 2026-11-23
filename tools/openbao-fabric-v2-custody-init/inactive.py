"""Inactive, fixture-only custody-init protocol model. No live transport exists here."""
import hashlib
class Refusal(Exception): pass
ENVELOPE={'endpoint':'https://openbao-fabric-v2.txo-fabric-system.svc:8200','sni':'openbao-fabric-v2.txo-fabric-system.svc','window':1800,'threshold':3,'shares':5}
FORBIDDEN={'token','credential','share','caDer','rootToken','command'}
def parse_envelope(value):
 if set(value)!=set(ENVELOPE) or value!=ENVELOPE:raise Refusal('closed envelope')
 return dict(value)
class FakeCA:
 def resolve(self,der):
  if hashlib.sha256(der).hexdigest()!='85e106a9143f39d1f62180b50878a3ae012992ea0998660581f3b874a3bd7421':raise Refusal('TLS mismatch')
class FakeLedger:
 def __init__(self,mode='ok'):self.mode=mode;self.created=False
 def create_v0(self):
  if self.mode in ('collision','crash','timeout') or self.created:raise Refusal(self.mode)
  self.created=True
class FakeWitness:
 def attest(self,present,expired=False):
  if not present or expired:raise Refusal('witness/authorization refused')
def inactive_fixture(request,ca,ledger,witness,der,now=0,expires=1800):
 if FORBIDDEN & set(request) or expires-now>1800 or expires<=now:raise Refusal('refused before operation')
 parse_envelope(request['envelope']);ca.resolve(der);ledger.create_v0();witness.attest(request.get('witness',False),request.get('expired',False));return {'state':'CLOSED','secretPersisted':False}
