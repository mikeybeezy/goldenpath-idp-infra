---
id: RB-0012-leak-protection-management
title: Leak Protection Management
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: none
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
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: runbooks
status: active
supported_until: '2028-01-01'
---

# RB-0012: Leak Protection Management

```text
    _______________________________
   |                               |
   |       GOVERNANCE SHIELD       |
   |_______________________________|
               |       |
      _________|_______|_________
     |                           |
     |    [ PRODUCTION ZONE ]    |
     |___________________________|
               ^       ^
               |       |
        _______|_______|_______
       |        [ LEAK ]       |
       |     (exempt: true)    |
       |_______________________|
               |   X   |
               |_______|
           [ BLOCKED BY CI ]
```

## Summary

**Leak Protection** is a mandatory safety gate in our CI/CD pipeline. It prevents resources marked with `exempt: true` (scratchpads, experimental templates, or test data) from accidentally "leaking" into Production environments.

## The Trigger

You will encounter this runbook if your CI pipeline fails with the following error:
` LEAK PROTECTION: Resources marked as 'exempt: true' cannot be deployed to Production environments.`

## Action Steps

### 1. Identify the Offending File
Check the CI logs to find the exact path of the file that triggered the block. It will be located in either:
*   `envs/prod/`
*   `apps/prod/`
*   `gitops/argocd/apps/prod/`

### 2. Determine Intent
*   **Case A: This asset MUST be in Production.**
    - If the asset is ready for prime time, you must switch it from "Experimental" to "Governed."
    - Open the `metadata.yaml` (or the frontmatter of the `.md` file).
    - Change `exempt: true` to `exempt: false` (or remove the field entirely).
    - Ensure all mandated fields (owner, domain, risk_profile) are correctly populated.

*   **Case B: This asset was copied by mistake.**
    - Delete the file from the Production path.
    - If it was intended for testing, move it to `envs/dev/` or `apps/test/`.

### 3. Verification
Run the validation locally before pushing:
```bash
bin/governance check [path/to/file]
```

## Why This Exists
In a "Born Governed" ecosystem, we allow developers to bypass strict rules for rapid prototyping (using `exempt: true`). However, Production is an immutable high-compliance zone. This gate ensures that nothing enters Production without being explicitly declared, owned, and risk-assessed.

---
*Last Updated: 2026-01-07*
