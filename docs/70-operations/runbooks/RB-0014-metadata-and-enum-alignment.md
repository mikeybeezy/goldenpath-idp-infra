---
id: RB-0014-metadata-and-enum-alignment
title: Metadata & Enum Alignment
type: runbook
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
category: runbooks
---

# RB-0013: Metadata & Enum Alignment

```text
    [ YOUR CODE ] <----( HEALING )---- [ GOVERNANCE ]
          |                                  |
    { id: "???" } <--- [ DRIFT ] ---> { domain: "???" }
          \               |                /
           \_____[ bin/governance ]_______/
                     [ HEAL ]
```

## Summary

This runbook addresses failures related to **Metadata Quality Gates**. These issues occur when local metadata sidecars or file frontmatter deviate from the canonical enums and schemas defined in `/schemas/metadata/`.

## Common Symptoms

*   `Enum validation failed`: You used a value (e.g., `owner: rogue-team`) not found in `enums.yaml`.
*   `[MISSING/MALFORMED]`: Required fields are empty or improperly formatted.
*   `[INJECTION FAILURE]`: The `id` in your sidecar doesn't match the K8s resource labels.

## Recovery Procedures

### 1. The "Hammer" (Auto-Healing)
Before manual editing, always try the platform's self-healing engine. This is the **Primary Recovery Path**.

```bash
# Heal a specific file or directory
bin/governance heal [path/to/target]
```
This command performs contextual inference (e.g., mapping `categories: unknown` based on directory path) and prunes redundant fields matching parent defaults.

### 2. Resolving Enum Drift
If `heal` doesn't work, you are likely using a value that doesn't exist in the system vocabulary.
1.  Check [**`GOVERNANCE_VOCABULARY.md`**](../../10-governance/GOVERNANCE_VOCABULARY.md) for valid values.
2.  Update your `metadata.yaml` to use a supported value for `domain`, `owner`, `risk_profile`, etc.

### 3. Schema Failure
If you see `⚠️ Warning: Could not load schema`, notify the Platform Team. The central governance contracts may be corrupted.

## Why This Exists
Consistent metadata is the "Glue" of our Knowledge Graph. It ensures that ownership, risk, and reliability data can be queried across the entire platform, powering dashboards and the Backstage Developer Portal.

---
*Last Updated: 2026-01-07*
