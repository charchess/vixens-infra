#!/usr/bin/env python3
"""Validate Music Assistant's effective secret-controller target."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SECRET_NAME = "music-assistant-secrets"
SECRET_NAMESPACE = "media"


def field(block: str, name: str, indent: int) -> str | None:
    match = re.search(rf"^ {{{indent}}}{re.escape(name)}:\s*([^\s#]+)\s*$", block, re.MULTILINE)
    return match.group(1) if match else None


def block(document: str, name: str, header_indent: int, child_indent: int) -> str:
    match = re.search(
        rf"^ {{{header_indent}}}{re.escape(name)}:\s*$\n(?P<body>(?:^ {{{child_indent}}}.*\n?)*)",
        document,
        re.MULTILINE,
    )
    return match.group("body") if match else ""


def document_kind(document: str) -> str | None:
    return field(document, "kind", 0)


def metadata(document: str) -> tuple[str | None, str | None]:
    values = block(document, "metadata", 0, 2)
    return field(values, "name", 2), field(values, "namespace", 2)


def infisical_target(document: str) -> tuple[str | None, str | None]:
    specification = block(document, "spec", 0, 2)
    reference = block(specification, "managedSecretReference", 2, 4)
    return field(reference, "secretName", 4), field(reference, "secretNamespace", 4)


def is_openbao_external_secret(document: str) -> bool:
    name, namespace = metadata(document)
    if document_kind(document) != "ExternalSecret" or (name, namespace) != (SECRET_NAME, SECRET_NAMESPACE):
        return False

    specification = block(document, "spec", 0, 2)
    target = block(specification, "target", 2, 4)
    store = block(specification, "secretStoreRef", 2, 4)
    return field(target, "name", 4) == SECRET_NAME and field(store, "name", 4) == "openbao"


def validate(rendered: str) -> None:
    documents = [document for document in re.split(r"^---\s*$", rendered, flags=re.MULTILINE) if document.strip()]
    external = []

    for document in documents:
        if document_kind(document) == "InfisicalSecret":
            resource_name, resource_namespace = metadata(document)
            target_name, target_namespace = infisical_target(document)
            if (target_name, target_namespace) == (SECRET_NAME, SECRET_NAMESPACE):
                raise SystemExit(
                    "legacy InfisicalSecret metadata "
                    f"{resource_namespace}/{resource_name} effectively targets "
                    f"{target_namespace}/{target_name}"
                )
        if is_openbao_external_secret(document):
            external.append(document)

    if len(external) != 1:
        raise SystemExit(f"expected exactly one ESO/OpenBao ExternalSecret target, found {len(external)}")


if __name__ == "__main__":
    validate(Path(sys.argv[1]).read_text())
