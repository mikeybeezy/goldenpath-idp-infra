---
id: ADR-0089-closed-loop-metadata-injection
title: 'ADR-0089: Closed-Loop Metadata Injection'
type: adr
status: active
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle: active
version: '1.0'
supported_until: 2028-01-04
breaking_change: false
---

# ADR-0089: Closed-Loop Metadata Injection

## Status
Accepted

## Context
We have established a robust metadata governance system using sidecars (`metadata.yaml`). However, this metadata remained isolated from the live running resources in Kubernetes. To enable field-level visibility and auditing in a live cluster, we need a way to propagate this metadata into deployment artifacts.

## Decision
We will implement "Closed-Loop Governance" by automatically injecting metadata from governance sidecars into Kubernetes manifests (Helm values and ArgoCD Applications).

1. **Automated Injection**: `scripts/standardize-metadata.py` will serve as the propagation engine.
2. **Standard Keys**: Metadata will be injected into a `governance` block in `values.yaml` files.
3. **K8s Annotations**: Delivery resources (ArgoCD Apps) will be enriched with `goldenpath.idp/*` annotations.
4. **Template Support**: `render-template.py` will be enhanced to support nested metadata resolution.

## Consequences
- **Positive**: Live resources carry their ownership and risk context, enabling real-time auditing.
- **Positive**: Eliminates manual synchronization between documentation and infrastructure config.
- **Neutral**: `values.yaml` files will now be partially managed by automation.
- **Negative**: Increased complexity in the standardization script.
