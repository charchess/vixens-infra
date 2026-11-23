from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "argocd/overlays/prod/apps/txo-fabric-openbao-v2-phase1.yaml"
ROOT_KUSTOMIZATION = ROOT / "argocd/overlays/prod/kustomization.yaml"
SHA = "6f84c67d00b9446637f868c3ac11e325293f8b4d"
NAME = "txo-fabric-openbao-v2-phase1"


class OpenBaoFabricV2Phase1ArgoBoundaryTest(unittest.TestCase):
    def test_manual_project_application_is_exactly_allowlisted(self):
        source = APP.read_text()
        self.assertIn(f"name: {NAME}", source)
        self.assertIn("repoURL: https://github.com/charchess/vixens-fabric.git", source)
        self.assertIn(f"targetRevision: {SHA}", source)
        self.assertIn("path: apps/60-services/txo-fabric/openbao-fabric-v2-phase1", source)
        self.assertIn("namespace: txo-fabric-system", source)
        self.assertIn("server: https://kubernetes.default.svc", source)
        self.assertIn("FailOnSharedResource=true", source)
        for kind in ("ConfigMap", "PersistentVolumeClaim", "StatefulSet", "Service", "NetworkPolicy", "Issuer", "Certificate"):
            self.assertIn(f"kind: {kind}", source)
        for forbidden in ("automated:", "prune:", "selfHeal:", "retry:", "hook:", "finalizers:", "ClusterRole", "CustomResourceDefinition", "ExternalSecret", "SecretStore", "ClusterSecretStore", "ServiceAccount", "Job", "auth", "bootstrap", "client", "policy"):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("clusterResourceWhitelist:\n    -", source)

    def test_production_root_selects_exactly_one_boundary(self):
        root = ROOT_KUSTOMIZATION.read_text()
        self.assertEqual(root.count("apps/txo-fabric-openbao-v2-phase1.yaml"), 1)

    def test_render_is_limited_to_project_and_manual_application(self):
        rendered = subprocess.run(["kustomize", "build", "argocd/overlays/prod"], cwd=ROOT, text=True, capture_output=True, check=True).stdout
        boundary = [doc for doc in rendered.split("---\n") if NAME in doc]
        self.assertEqual(len(boundary), 2)
        joined = "\n---\n".join(boundary)
        self.assertIn("kind: AppProject", joined)
        self.assertIn("kind: Application", joined)
        self.assertIn(f"targetRevision: {SHA}", joined)
        self.assertNotIn("automated:", joined)
        self.assertNotIn("prune:", joined)
        self.assertNotIn("selfHeal:", joined)
        self.assertNotIn("retry:", joined)
        self.assertNotIn("finalizers:", joined)


if __name__ == "__main__":
    unittest.main()
