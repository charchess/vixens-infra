# OpenBao HTTPS and Transit identity contract

This source contract has one strict OpenBao server identity:

- endpoint: `https://nas.truxonline.com:8200`
- TLS server name/SNI: `nas.truxonline.com`
- trust reference: ConfigMap `external-secrets/openbao-ca`, key `ca.crt`
- server certificate requirement: its SAN includes `nas.truxonline.com`

The CA chain and server certificate are distributed and rotated through the
separately approved trust/certificate path. No PEM, private key, bearer token,
or Secret value belongs in this repository. The `ClusterSecretStore` references
the CA with `caProvider`; it must never use HTTP, an IP literal, or
a TLS-verification bypass.

## Kubernetes-auth Transit identity

The only in-cluster client identity declared here is ServiceAccount
`external-secrets/openbao-transit`. It has no Kubernetes Role or RoleBinding.
External Secrets obtains a bounded Kubernetes token for it and authenticates to
the OpenBao Kubernetes auth mount `kubernetes` using role `openbao-transit`.

The OpenBao-side role is an out-of-band authorization record, to be installed
only under a separately approved runtime gate. Its required binding is:

```text
role name: openbao-transit
bound_service_account_names: openbao-transit
bound_service_account_namespaces: external-secrets
policies: txo-fabric-seal
token_no_default_policy: true
```

## Transit policy allow/deny contract

`txo-fabric-seal.hcl.example` is non-executable source evidence for the
OpenBao policy named `txo-fabric-seal`. Its entire permitted surface is exactly:

- `update transit/encrypt/txo-fabric-seal`
- `update transit/decrypt/txo-fabric-seal`

Every other path and capability is denied, including wildcard Transit paths,
key management, policy/auth/token management, KV access, list/read/create/
delete/sudo, and administration. It is not an ExternalSecret authority or a
fallback secret store.

`tests/openbao_https_transit_contract.py` validates these properties from the
versioned source and includes negative inputs for the forbidden endpoint,
trust, and policy cases. It is a static contract test; it neither calls
OpenBao nor performs an unseal, sync, reconcile, rotation, restart, cutover,
or Transit operation.

## Rollback

Revert the single Git commit containing this contract, then allow the normal
review and reconciliation authority to decide any subsequent runtime action.
Do not attempt an in-place trust or identity rollback from this repository.
