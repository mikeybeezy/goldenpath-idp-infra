---
id: RB-0015-repo-health-and-hygiene
title: Repo Health & Hygiene
type: runbook
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 1
category: runbooks
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - CAPABILITY_LEDGER
  - CI_TEARDOWN_WORKFLOW
  - DOCS_RUNBOOKS_README
  - PLATFORM_HEALTH
  - RB-0013-leak-protection-management
  - RB-0014-metadata-and-enum-alignment
  - RB-0016-extending-governance-vocabulary
---
## RB-0014: Repo Health & Hygiene

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

* **Target**: 100% compliance.
* **Failure Mode**: If the audit finds drift, use [**RB-0013**](docs/70-operations/runbooks/RB-0013-metadata-and-enum-alignment.md) to remediate.

### 2. Registry Verification

The [**`PLATFORM_HEALTH.md`**](../../../PLATFORM_HEALTH.md) dashboard tracks how well our sidecars are "bonded" to physical resources.

* **Fixing `⚠️ Injection Integrity`**: Ensure that the K8s name labels match the sidecar `id` exactly.

### 3. Emoji & Visual Policy

To keep documentation professional and readable, we enforce a strict emoji policy.

* **Detection**: `scripts/enforce_emoji_policy.py` will flag illegal emojis in ADRs or Policies.
* **Recovery**:

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
Last Updated: 2026-01-07
