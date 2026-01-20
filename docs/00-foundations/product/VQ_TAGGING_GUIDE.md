---
id: VQ_TAGGING_GUIDE
title: 'VQ Tagging Guide: Scripts & Workflows'
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0121-value-quantification-framework
  - CL-0077-value-quantification-framework
  - PLATFORM_DASHBOARDS
  - SESSION_CAPTURE_2026_01_20_VQ
---
## VQ Tagging Guide: Scripts & Workflows

## Metadata Enums Index

## vq_class

|Value|Meaning|Notes|
|------|--------|------|
|🔴 HV/HQ|High value, high quality|Trust-critical, must be hardened|
|🟡 HV/LQ|High value, low quality|Ship fast, reversible|
|🔵 MV/HQ|Medium value, high quality|Bound tightly|
|⚫ LV/LQ|Low value, low quality|Avoid|

## lifecycle

To track the value of your automation, we use the `value_quantification` object in your metadata sidecars.

### How this maps to your platform (concrete)

### 🔴 High Value + High Quality (TOP PRIORITY) 🔴 HV/HQ

These must be done slow enough to be right.

Examples from your work:

- metadata schemas & enums
- inheritance rules
- approval routing
- teardown sequencing
- policy enforcement
- audit trails

These are non-negotiable. They form trust.

### 🟡 High Value + Low Quality (MOVE FAST) 🟡 HV/LQ

These can be rough, reversible, or experimental.

Examples:

- Backstage templates
- UX surfaces
- dashboards v1
- reporting views
- automation helpers

Rule: If it breaks, no one loses trust or data.

### 🔵 Low Value + High Quality (BOUND IT) 🔵 MV/HQ

Do it once, do it safely, then stop touching it.

Examples:

- legacy compatibility
- rare workflows
- edge-case compliance

Rule: Don’t polish; contain.

### ⚫ Low Value + Low Quality (DROP IT) ⚫ LV/LQ

This is how you protect your energy.

Examples:

- perfect docs nobody uses
- edge tooling no one depends on
- premature integrations

Rule: If it doesn’t compound, don’t carry it.

## 1. Tagging Python Scripts

Scripts are tagged using an adjacent `metadata.yaml` or a directory-level default.

### Example: [standardize_metadata.py](../../../scripts/metadata.yaml)

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

### Example: [.github/workflows/create-ecr-registry.metadata.yaml](.github/workflows/create-ecr-registry.metadata.yaml)

```yaml
id: WORKFLOW_CREATE_ECR
type: documentation
domain: delivery
value_quantification:
  impact_tier: tier-2
  potential_savings_hours: 0.5  # Saves 30m vs manual TF/Console work
```

---

## 3. Why Tag Both?

- **Scripts** represent "Architectural Force Multipliers" (O(1) fixes).
- **Workflows** represent "Developer Lifecycle Reclaim" (Time saved per PR).

By tagging both, the VQ Engine can differentiate between **Efficiency Value** (Scripts) and **Velocity Value** (Workflows).
