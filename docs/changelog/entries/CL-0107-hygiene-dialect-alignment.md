---
id: CL-0107
title: Hygiene Dialect Alignment and Script Idempotency
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
  - CL-0107
  - CL-0108
supersedes: []
superseded_by: []
tags:
  - hygiene
  - automation
  - ci
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.5
supported_until: '2028-01-01'
---
# CL-0107: Hygiene Dialect Alignment and Script Idempotency

## Summary
Resolved a systemic feedback loop between automated governance scripts and CI hygiene gates. By aligning the "dialects" of the automation engines with the enforcement tools, we have eliminated redundant CI failures and ensured that automated healing is idempotent and non-disruptive.

## Details
- **terminal Newline Enforcement**: Updated `standardize_metadata.py` and `vq_logger.py` to strictly enforce terminal newlines (`\n`) for all generated Markdown, JSON, and YAML files, matching `pre-commit` standards.
- **Idempotent Standardization**: Implemented change-detection in the `standardize_metadata.py` engine. The script now performs a memory-based comparison and only writes to disk if an actual standardization correction is required.
- **Precision K8s Injection**: Refactored the `inject_governance` logic to be strictly idempotent. Kubernetes manifests and ArgoCD applications are no longer re-written if the governance annotations already match the current metadata state.
- **Pre-commit Modernization**: Migrated `.pre-commit-config.yaml` to utilize the modern `stages: [pre-commit]` syntax, resolving long-standing deprecation warnings in the CI pipeline.
- **CI Stability**: Eliminated the "Dirty PR" loop where automated indexing scripts would trigger hygiene failures in the same PR they were meant to assist.

## Related
- ADR-0014: Platform CI Local Preflight Checks
- METADATA_STRATEGY.md
- bin/governance
