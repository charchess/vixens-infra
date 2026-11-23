# OpenBao Fabric v2 custody-init ceremony contract

This is a source-only protocol contract. It is not a runner, client, Kubernetes workload, Argo source, or live OpenBao invocation.

Preconditions: an existing authenticated operator and an independent custody witness must be present. They must be distinct. The fixed transport identity is the v2 service endpoint, its SNI, and its named v2 CA trust identity.

Ceremony protocol: submit metadata-only request at CAS version; record an independent witness; record initialization metadata only after the witnessed transition; record revocation metadata as the only terminal transition. The state machine is closed: requested → witnessed → initialized → revoked.

Shamir policy is fixed at 3-of-5. Shares, recovery material, tokens, root material, wrapped payloads and policy/provider payloads must never be written to Git, the request, ledger, receipt, logs, or this runbook.

Refuse endpoint, SNI, trust, method, transition, CAS-version, threshold, actor-separation, and secret-material mismatches. Runtime execution requires a separately approved, non-Git custody implementation and Electra-owned evidence.
