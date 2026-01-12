---
id: CL-0047-closed-loop-governance
title: 'CL-0047: Closed-Loop Governance & Metadata Injection'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
version: '1.0'
lifecycle: active
relates_to:
  - ADR-0089
  - METADATA_INJECTION_GUIDE
supported_until: 2027-01-04
breaking_change: false
---

# CL-0047: Closed-Loop Governance & Metadata Injection

## Summary
Implemented "Phase 2: Closed-Loop Governance," enabling the automatic propagation of governance metadata from static sidecars into live Kubernetes deployment resources.

## Changes
- **Tooling Enhancement**: Updated `scripts/standardize-metadata.py` with a **Governance Injection Pass**.
- **Metadata Propagation**: Automatically enriched 80+ `values.yaml` files and ArgoCD manifests with ownership and risk data.
- **Template Support**: Upgraded `scripts/render-template.py` to support nested key resolution (e.g. `values.governance.id`).
- **Application Hardening**: Updated application templates to render governance annotations (`goldenpath.idp/id`, etc.).
- **Registry Update**: Created [Platform Automation Scripts Index](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/index.md).

## Business Value
- **100% Auditability**: Live cluster resources now advertise their own ownership and risk profiles.
- **Unified Knowledge Graph**: The gap between "Documentation" and "Live State" is programmatically bridged.
- **Operational Efficiency**: Zero manual effort required to synchronize governance data across the estate.
