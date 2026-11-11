"""Offline guard contract fixtures stay deterministic and local."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-offline-guard-contract.py"
FIXTURES = ROOT / "ci" / "offline-guards" / "fixtures"


class OfflineGuardContractTest(unittest.TestCase):
    def run_fixture(self, name: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(CHECK), str(FIXTURES / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def test_mapped_path_fixture_is_green_and_traces_kustomize_guard(self) -> None:
        result, output = self.run_fixture("green-mapped-kustomize.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output["decision"], "applicable")
        self.assertIn("kustomize-render", output["guards"])
        self.assertEqual(output["rule"], "apps/**/kustomization.yaml")

    def test_unmapped_path_is_green_only_with_explicit_trace(self) -> None:
        result, output = self.run_fixture("green-not-applicable.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output["decision"], "not_applicable")
        self.assertEqual(output["rule"], "no_path_rule_matched")
        self.assertRegex(str(output["changed_paths_sha256"]), r"^[0-9a-f]{64}$")

    def test_control_change_forces_all_required_guards(self) -> None:
        result, output = self.run_fixture("green-control-change.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output["decision"], "applicable")
        self.assertEqual(output["rule"], "control-plane")
        self.assertEqual(output["guards"], [
            "actionlint", "kustomize-render", "release-channel-contract",
            "repository-hygiene", "scope-boundary", "secret-scan", "yaml-lint",
        ])

    def test_broken_fixture_is_red(self) -> None:
        result, output = self.run_fixture("red-broken-fixture.json")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(output["result"], "failed")
        self.assertEqual(output["failure"], "fixture validation failed")

    def test_missing_required_guard_is_red(self) -> None:
        result, output = self.run_fixture("red-missing-required-guard.json")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(output["result"], "failed")
        self.assertEqual(output["failure"], "required guard missing")

    def test_versioned_evidence_matches_every_fixture_output(self) -> None:
        evidence = ROOT / "ci" / "offline-guards" / "evidence"
        fixtures = sorted(FIXTURES.glob("*.json"))
        self.assertEqual(
            {path.name for path in evidence.glob("*.json")},
            {path.name for path in fixtures},
        )
        for fixture in fixtures:
            result, output = self.run_fixture(fixture.name)
            expected = json.loads(fixture.read_text(encoding="utf-8"))["expected"]
            self.assertEqual(result.returncode, expected["exit_code"], fixture.name)
            recorded = json.loads((evidence / fixture.name).read_text(encoding="utf-8"))
            self.assertEqual(recorded, output, fixture.name)


if __name__ == "__main__":
    unittest.main()
