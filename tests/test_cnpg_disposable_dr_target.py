import unittest
from pathlib import Path
ROOT = Path(__file__).parents[1] / "docs/disaster-recovery/cnpg-disposable-target"
class DisposableCNPGTargetContract(unittest.TestCase):
    def test_manifest_and_runbook_are_isolated_and_non_executable(self):
        manifest = chr(10).join(x.read_text() for x in ROOT.glob("*.yaml"))
        runbook = (ROOT / "RUNBOOK.md").read_text()
        for value in ("cnpg-dr-REPLACE_RUN_ID", "default-deny", "read-only"):
            self.assertIn(value, manifest)
        self.assertIn("Gate 0", runbook)
        self.assertNotIn("kubectl apply", runbook)
if __name__ == "__main__": unittest.main()
