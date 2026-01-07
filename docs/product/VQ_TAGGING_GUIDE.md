---
id: VQ_TAGGING_GUIDE
title: 'VQ Tagging Guide: Scripts & Workflows'
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
---

# VQ Tagging Guide: Scripts & Workflows

To track the value of your automation, we use the `value_quantification` object in your metadata sidecars.

## 🐍 1. Tagging Python Scripts
Scripts are tagged using an adjacent `metadata.yaml` or a directory-level default.

### Example: [standardize_metadata.py](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/metadata.yaml)
```yaml
id: APPS_SCRIPTS_METADATA
type: automation-script
value_quantification:
  impact_tier: tier-1
  potential_savings_hours: 1.0  # Saves 1h per global refactor
```

---

## 🤖 2. Tagging GitHub Workflows
Since GitHub Actions YAML files don't support custom governance keys, we use a **Metadata Sidecar** in the `.github/workflows/` directory.

### Example: [.github/workflows/create-ecr-registry.metadata.yaml](file:///Users/mikesablaze/goldenpath-idp-infra/.github/workflows/create-ecr-registry.metadata.yaml)
```yaml
id: WORKFLOW_CREATE_ECR
type: documentation
domain: delivery
value_quantification:
  impact_tier: tier-2
  potential_savings_hours: 0.5  # Saves 30m vs manual TF/Console work
```

---

## 🔍 3. Why Tag Both?
- **Scripts** represent "Architectural Force Multipliers" (O(1) fixes).
- **Workflows** represent "Developer Lifecycle Reclaim" (Time saved per PR).

By tagging both, the VQ Engine can differentiate between **Efficiency Value** (Scripts) and **Velocity Value** (Workflows).
