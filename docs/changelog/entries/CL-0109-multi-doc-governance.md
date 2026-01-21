---
id: CL-0109
title: Multi-Document YAML Logic and De-conflicted Ownership
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0014-platform-ci-local-preflight-checks
  - CL-0108
  - CL-0109
  - CL-0110
supersedes: []
superseded_by: []
tags:
  - governance
  - k8s
  - yaml
  - automation
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 2.0
---

# CL-0109: Multi-Document YAML Logic and De-conflicted Ownership

## Summary
Upgraded the platform's automated remediation engine (`standardize_metadata.py`) to handle multi-document Kubernetes manifests and resolved a metadata ownership conflict that caused oscillation in CI.

## Details
- **Multi-Document Awareness**: Refactored `inject_governance` to use `yaml.safe_load_all()` and `platform_yaml_dump_all()`. The engine now correctly annotates all Kubernetes resources within a single file (e.g., RBAC files with multiple documents), which were previously skipped.
- **Ownership De-confliction**: Implemented a "Specific Owner Wins" policy. App-level metadata (defined in `apps/`) now takes precedence over Environment-level metadata (defined in `gitops/argocd/apps/`). This prevents the engine from fighting over which ID should be applied to ArgoCD manifests.
- **Marker-Based Indexing**: Converted Script and Workflow index generation to a marker-based injection strategy (similar to ADRs). This ensures that hand-managed frontmatter and auto-generated tables do not cause "drift" failures in CI.
- **Centralized Multi-Doc Dumping**: Extended `scripts/lib/metadata_config.py` with `platform_yaml_dump_all()` to maintain dialect alignment across complex manifests.

## Technical Improvements
- Added `explicit_start=True` to multi-document YAML outputs to follow Kubernetes best practices.
- Implemented string-level idempotency checks in `inject_governance` to minimize unnecessary disk I/O and CI triggers.
- Resolved `NameError` and missing `import re` in stabilized generation scripts.
