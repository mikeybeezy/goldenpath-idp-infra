---
id: ADR-0087-k8s-metadata-sidecars
title: 'ADR-0087: Integration of Governance Metadata with Kubernetes Resources'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0087-k8s-metadata-sidecars
  - ADR-0137
  - METADATA_ARTIFACT_ADOPTION_POLICY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
dependencies:
  - module:vpc
  - service:eks
---

# ADR-0087: Integration of Governance Metadata with Kubernetes Resources

## Status
Proposed

## Context
The repository has achieved 100% metadata compliance across all documentation and markdown files. This metadata enables automated health reporting, risk assessment, and lifecycle management. However, there is a "visibility gap" between the documentation and the live Kubernetes resources deployed via Helm and GitOps.

Currently, K8s manifests lack a standardized way to carry the same governance information (ownership, risk profile, etc.) that our documentation system provides.

## Decision
We will implement "Metadata Sidecars" for all Kubernetes resources. A metadata sidecar is a `metadata.yaml` file located in the same directory as the resource's configuration (e.g., within a Helm chart or a baseline directory).

### 1. Sidecar Schema
The `metadata.yaml` file will follow the same "Concluded Schema" used for markdown documents, ensuring a unified Knowledge Graph.

```yaml
---
id: HELM_KONG
title: "Kong Ingress Gateway"
type: chart
owner: platform-team
status: active
dependencies:
  - module:vpc
  - service:eks
risk_profile:
  production_impact: high
  security_risk: ingress-exposure
  coupling_risk: high
reliability:
  rollback_strategy: helm-rollback
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: true
---
```

### 2. Location
- **Helm Charts**: `gitops/helm/<chart-name>/metadata.yaml`
- **Tooling Configs**: `idp-tooling/<tool-name>/metadata.yaml`

### 3. Live Injection (Future)
The metadata defined in these sidecars SHOULD be injected into the live Kubernetes resources as annotations (prefixed with `governance.idp.io/`) during the CI/CD sweep. This allows for live audits of cluster compliance.

## Consequences
- **Positive**: Uniform governance across documentation and live infra.
- **Positive**: Simplifies Backstage catalog integration (Sidecar → Catalog Info).
- **Negative**: Extra files to manage in the `gitops/` directory.
- **Dependency**: Requires `validate_metadata.py` to be updated to support YAML files.
