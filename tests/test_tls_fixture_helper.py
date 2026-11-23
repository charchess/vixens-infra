"""Test-only synthetic digest comparator; production runner does not import this module."""
import hashlib
import unittest
def matches_digest(ca_der, expected_digest):
 return hashlib.sha256(ca_der).hexdigest()==expected_digest
class SyntheticFixtureTests(unittest.TestCase):
 def test_nonsecret_fixture_positive_and_negative(self):
  der=b'synthetic-nonsecret-ca-der';digest=hashlib.sha256(der).hexdigest()
  self.assertTrue(matches_digest(der,digest));self.assertFalse(matches_digest(der,'0'*64))
if __name__=='__main__':unittest.main()
