import unittest
from pathlib import Path
ROOT = Path(__file__).parents[1] / "docs/disaster-recovery/cnpg-disposable-target"
RUN_ID = "cnpg-dr-REPLACE_RUN_ID"
FORBIDDEN = ("kind: Application", "kind: ExternalSecret", "kind: ScheduledBackup", "kind: Backup", "immediate:", "postgresql-shared", "namespace: databases", "0.0.0.0/0", "toEntities: [all]", "argocd.argoproj.io/instance")
def validate_isolation(text):
    for token in FORBIDDEN:
        if token in text: raise AssertionError("forbidden boundary: " + token)
    if "kind: Service" in text and "cnpg.io/cluster: " + RUN_ID not in text: raise AssertionError("canonical Service selector")
    for resource in ("namespace.yaml", "default-deny.yaml", "objectstore-readonly.yaml", "scratch-pvc.yaml", "cluster.yaml", "service.yaml"):
        source = (ROOT / resource).read_text()
        if RUN_ID not in source: raise AssertionError("missing run-id: " + resource)
class DisposableCNPGTargetContract(unittest.TestCase):
    def test_template_is_isolated_and_non_executable(self):
        manifest = chr(10).join(x.read_text() for x in ROOT.glob("*.yaml"))
        runbook = (ROOT / "RUNBOOK.md").read_text()
        validate_isolation(manifest)
        self.assertIn("default-deny", manifest); self.assertIn("read-only", manifest); self.assertIn("Gate 0", runbook); self.assertNotIn("kubectl apply", runbook)
    def test_rejects_every_disallowed_boundary(self):
        for token in FORBIDDEN + ("kind: Service",):
            with self.subTest(token=token):
                with self.assertRaises(AssertionError):
                    validate_isolation(token)
if __name__ == "__main__": unittest.main()
