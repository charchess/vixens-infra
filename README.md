# vixens-infra

Shared infrastructure services consuming Vixens Core contracts.

## Bootstrap status

This repository is a **no-cutover bootstrap**. It is not an active Argo CD source and contains no copied production manifests, credentials or runtime state.

## Non-goals

Cluster bootstrap/provider implementation, personal applications, TXO Fabric product lifecycle and cross-repository release promotion.

## CI scope

YAML and Kustomize rendering/schema checks for shared service manifests and their declared Core dependencies.

## Delivery model

Changes follow Issue → branch → PR → required CI → merge. The retained `charchess/vixens` repository remains the future multi-repository GitOps orchestrator and release/BOM authority.
