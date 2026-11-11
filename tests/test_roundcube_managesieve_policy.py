"""Contract for the private Roundcube-to-ManageSieve path (Infra #68)."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "apps/60-services/mail/base/roundcube-managesieve-policy.yaml"


class RoundcubeManageSievePolicyTest(unittest.TestCase):
    def test_allows_only_roundcube_to_mailserver_on_private_managesieve(self) -> None:
        document = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

        self.assertEqual(document["kind"], "CiliumNetworkPolicy")
        self.assertEqual(document["metadata"]["namespace"], "mail")
        spec = document["spec"]
        self.assertEqual(
            spec["endpointSelector"]["matchLabels"],
            {"app.kubernetes.io/name": "roundcube", "app.kubernetes.io/part-of": "truxonline-mail"},
        )
        self.assertEqual(len(spec["egress"]), 1)
        egress = spec["egress"][0]
        self.assertNotIn("toEntities", egress)
        self.assertNotIn("toCIDR", egress)
        self.assertEqual(
            egress["toEndpoints"],
            [{"matchLabels": {
                "k8s:io.kubernetes.pod.namespace": "mail",
                "k8s:app.kubernetes.io/name": "mailserver",
                "k8s:app.kubernetes.io/part-of": "truxonline-mail",
            }}],
        )
        self.assertEqual(egress["toPorts"], [{"ports": [{"port": "4190", "protocol": "TCP"}]}])

    def test_mailserver_admits_managesieve_only_from_roundcube(self) -> None:
        document = yaml.safe_load((ROOT / "apps/60-services/mail/base/mailserver-ldap-egress-policy.yaml").read_text(encoding="utf-8"))
        roundcube_rules = [
            rule for rule in document["spec"]["ingress"]
            if rule["fromEndpoints"] == [{"matchLabels": {
                "k8s:io.kubernetes.pod.namespace": "mail",
                "k8s:app.kubernetes.io/name": "roundcube",
                "k8s:app.kubernetes.io/part-of": "truxonline-mail",
            }}]
        ]
        self.assertEqual(len(roundcube_rules), 1)
        ports = roundcube_rules[0]["toPorts"][0]["ports"]
        self.assertIn({"port": "4190", "protocol": "TCP"}, ports)


if __name__ == "__main__":
    unittest.main()
