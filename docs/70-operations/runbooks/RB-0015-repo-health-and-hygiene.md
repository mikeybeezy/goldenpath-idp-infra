---
id: RB-0015-repo-health-and-hygiene
title: Repo Health & Hygiene
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: runbooks
status: active
supported_until: '2028-01-01'
---

# RB-0014: Repo Health & Hygiene

```text
       [ PLATFORM HEALTH ]
      /        |          \
   [  ]    [  ]      [  ]
   Audit     Compliance    Policy
```

## Summary

This runbook is for **Platform Owners** managing the long-term cleanliness and compliance of the repository. It focuses on non-blocking "Hygiene" tasks that affect the overall health score.

## Operational Tasks

### 1. The Audit Loop
Generate a repository-wide compliance snapshot to identify pockets of "Technical Debt" (orphaned sidecars or categories).

```bash
bin/governance audit
```
*   **Target**: 100% compliance.
*   **Failure Mode**: If the audit finds drift, use [**RB-0013**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/70-operations/runbooks/RB-0013-metadata-and-enum-alignment.md) to remediate.

### 2. Registry Verification
The [**`PLATFORM_HEALTH.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md) dashboard tracks how well our sidecars are "bonded" to physical resources.
*   **Fixing `⚠️ Injection Integrity`**: Ensure that the K8s name labels match the sidecar `id` exactly.

### 3. Emoji & Visual Policy
To keep documentation professional and readable, we enforce a strict emoji policy.
*   **Detection**: `scripts/enforce_emoji_policy.py` will flag illegal emojis in ADRs or Policies.
*   **Recovery**:
  ```bash
  python3 scripts/enforce_emoji_policy.py --fix .
  ```

### 4. Vocabulary Maintenance
Every time `enums.yaml` is updated, the human-readable docs must be refreshed.
```bash
bin/governance vocab
```

## Why This Exists
High-velocity platforms rot if not maintained. These hygiene tasks ensure that the "Total Governance" reach remains at 100%, providing users with trustworthy and predictable documentation.

---
*Last Updated: 2026-01-07*
