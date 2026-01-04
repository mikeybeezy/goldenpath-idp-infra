---
id: CL-0046-k8s-metadata-sidecars
title: 'CL-0046: K8s Metadata Sidecar Integration'
type: changelog
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# CL-0046: K8s Metadata Sidecar Integration

## Description
This change extends the IDP's governance schema from documentation (Markdown) to live infrastructure configuration (Helm/YAML) using a "Metadata Sidecar" pattern.

## Changes
- **New Pattern**: Established the `metadata.yaml` sidecar standard for infrastructure components.
- **Structural Enforcement**: Updated `scripts/validate-metadata.py` to mandate the presence of `metadata.yaml` in core zones (`gitops/helm/`, `idp-tooling/`, `envs/`).
- **Automated Remediation**: Upgraded `scripts/standardize-metadata.py` to automatically generate missing sidecars from templates.
- **Mass Implementation**: Backfilled **22 new sidecars** across the GitOps tree (Loki, Grafana, Keycloak, etc.) and standardized 341 files.
- **Verification**: Achieved 100% repository-wide structural and schema compliance.

## Business Value
- **Elimination of "Dark Infrastructure"**: Guaranteed visibility for 100% of the platform's GitOps estate.
- **Scale-Ready Governance**: New components are automatically invited into the governance framework.
- **Unified Knowledge Graph**: Ownership and risk data are now standard across all 341 platform resources.
