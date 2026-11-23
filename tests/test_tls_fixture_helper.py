"""Test-only synthetic digest comparator; production runner does not import this module."""
import hashlib
def matches_digest(ca_der, expected_digest):
 return hashlib.sha256(ca_der).hexdigest()==expected_digest
