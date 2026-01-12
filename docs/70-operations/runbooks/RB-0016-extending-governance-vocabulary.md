---
id: RB-0016-extending-governance-vocabulary
title: Extending Governance Vocabulary
type: runbook
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 1
category: runbooks
---

# RB-0015: Extending Governance Vocabulary

```text
       [ NEW VALUE? ]
             |
    _________V_________
   |                   |
   |   CHECK enums.yaml |
   |___________________|
             |
    _________V_________
   |                   |
   |   OPEN VOCAB PR   |
   |___________________|
             |
    _________V_________
   |                   |
   |  PLATFORM APPROVAL|
   |___________________|
```

## Summary

This runbook guides you through adding new values (owners, domains, artifact types, etc.) to the system's "Governance Vocabulary." This is required when your project uses a valid descriptive term that hasn't been formalised yet.

## Steps to Take

### 1. Confirm the Need
Is your value truly new, or is it a synonym of an existing one?
*   Check [**`GOVERNANCE_VOCABULARY.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/10-governance/GOVERNANCE_VOCABULARY.md).
*   If you find a suitable synonym, use it instead to reduce fragmentation.

### 2. Propose the Addition
If a new value is necessary:
1.  Navigate to [**`schemas/metadata/enums.yaml`**](file:///Users/mikesablaze/goldenpath-idp-infra/schemas/metadata/enums.yaml).
2.  Add your value to the appropriate list (e.g., `owners`, `domains`).
3.  Ensure the syntax is correct (valid YAML list).

### 3. Open a "Vocabulary PR"
*   **Title**: `feat: add <value> to governance enums`
*   **Description**: Briefly explain why this new category or owner is needed.
*   **Labels**: Apply the `governance` label.

### 4. Wait for Approval
The Platform Team will review your request. Once merged, the system will automatically rebuild the indexes, and your main PR will pass the validation gate.

## Why This Exists
By centralising the vocabulary, we ensure that the platform's Knowledge Graph remains clean, searchable, and trustworthy. Without this gate, the catalog would quickly fill with typos and inconsistent terminology.

---
*Last Updated: 2026-01-07*
