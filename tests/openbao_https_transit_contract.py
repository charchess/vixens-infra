#!/usr/bin/env python3
"""Static checks for the private OpenBao HTTPS and Transit policy contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "apps/00-infra/openbao/base/cluster-secret-store.yaml"
IDENTITY = ROOT / "apps/00-infra/openbao/base/transit-client-identity.yaml"
KUSTOMIZATION = ROOT / "apps/00-infra/openbao/base/kustomization.yaml"
POLICY = ROOT / "apps/00-infra/openbao/transit-seal-contract/txo-fabric-seal.hcl.example"
SOURCE_ROOT = ROOT / "apps/00-infra/openbao"


def require(pattern: str, text: str, message: str) -> None:
    if not re.search(pattern, text, flags=re.MULTILINE):
        raise SystemExit(message)


def forbid(pattern: str, text: str, message: str) -> None:
    if re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE):
        raise SystemExit(message)


def validate_store(text: str) -> None:
    require(r"^\s*server:\s*https://nas\.truxonline\.com:8200\s*$", text, "OpenBao endpoint must be strict HTTPS DNS/SNI")
    require(r"^\s*caProvider:\s*$", text, "ClusterSecretStore must declare caProvider")
    require(r"^\s*type:\s*ConfigMap\s*$", text, "caProvider must reference a ConfigMap")
    require(r"^\s*name:\s*openbao-ca\s*$", text, "caProvider must reference openbao-ca")
    require(r"^\s*namespace:\s*external-secrets\s*$", text, "caProvider must use external-secrets namespace")
    require(r"^\s*key:\s*ca\.crt\s*$", text, "caProvider must reference the CA chain key")
    require(r"^\s*role:\s*openbao-transit\s*$", text, "Kubernetes auth must use the Transit role")
    require(r"^\s*name:\s*openbao-transit\s*$", text, "Kubernetes auth must use the Transit identity")
    insecure_scheme = r"^\s*server:\s*http" + r"://"
    bypass_fields = "tls_skip" + "_verify|tlsSkipVerify"
    forbid(insecure_scheme, text, "HTTP OpenBao endpoint is forbidden")
    forbid(r"tokenSecretRef", text, "static OpenBao token authentication is forbidden")
    forbid(bypass_fields, text, "TLS verification bypass is forbidden")
    forbid(r"^\s*server:\s*https?://(?:\d{1,3}\.){3}\d{1,3}", text, "IP OpenBao endpoint is forbidden")


def validate_identity(text: str) -> None:
    require(r"^kind:\s*ServiceAccount\s*$", text, "Transit identity must be a ServiceAccount")
    require(r"^\s*name:\s*openbao-transit\s*$", text, "unexpected Transit ServiceAccount name")
    require(r"^\s*namespace:\s*external-secrets\s*$", text, "unexpected Transit ServiceAccount namespace")
    require(r"^automountServiceAccountToken:\s*false\s*$", text, "Transit ServiceAccount must not mount a default token")


def validate_kustomization(text: str) -> None:
    require(r"^\s*-\s+cluster-secret-store\.yaml\s*$", text, "Kustomization must include ClusterSecretStore")
    require(r"^\s*-\s+transit-client-identity\.yaml\s*$", text, "Kustomization must include Transit identity")


def validate_policy(text: str) -> None:
    paths = re.findall(r'^path "([^"]+)" \{\s*\n\s*capabilities = \["([^"]+)"\]', text, flags=re.MULTILINE)
    expected = {
        ("transit/encrypt/txo-fabric-seal", "update"),
        ("transit/decrypt/txo-fabric-seal", "update"),
    }
    if set(paths) != expected or len(paths) != len(expected):
        raise SystemExit("Transit policy must allow only update encrypt/decrypt on txo-fabric-seal")
    forbid(r"\*|\b(read|list|create|delete|sudo)\b", text, "Transit policy contains a forbidden path or capability")


def validate_no_sensitive_material() -> None:
    for path in SOURCE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text()
        forbid(r"-----BEGIN (?:CERTIFICATE|.*PRIVATE KEY)-----", text, f"PEM material is forbidden: {path.relative_to(ROOT)}")


def validate_negative_cases() -> None:
    for bad in (
        "server: http" + "://nas.truxonline.com:8200\n",
        "server: https://" + "192.0.2.8:8200\n",
        "tls_skip" + "_verify: true\n",
    ):
        try:
            validate_store(bad)
        except SystemExit:
            continue
        raise SystemExit("forbidden endpoint/TLS fixture was accepted")
    try:
        validate_policy('path "transit/*" {\n  capabilities = ["sudo"]\n}\n')
    except SystemExit:
        return
    raise SystemExit("forbidden Transit policy fixture was accepted")


def main() -> None:
    validate_store(STORE.read_text())
    validate_identity(IDENTITY.read_text())
    validate_kustomization(KUSTOMIZATION.read_text())
    validate_policy(POLICY.read_text())
    validate_no_sensitive_material()
    validate_negative_cases()
    print("OpenBao HTTPS/Transit contract: strict endpoint, CA reference, identity, allow/deny PASS")


if __name__ == "__main__":
    main()
