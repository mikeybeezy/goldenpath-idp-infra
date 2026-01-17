---
id: RB-0013-leak-protection-management
title: Leak Protection Management
type: runbook
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: none
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - DOCS_RUNBOOKS_README
  - RB-0012-argocd-app-readiness
  - RB-0014-metadata-and-enum-alignment
  - RB-0015-repo-health-and-hygiene
category: runbooks
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

You will encounter this runbook if your CI pipeline fails with the following: Search for `LEAK PROTECTION` in the infra repo logs.

## Action Steps

### 1. Identify the Offending File
Check the CI logs to find the exact path of the file that triggered the block. It will be located in either:
*   `envs/prod/`
*   `apps/prod/`
*   `gitops/argocd/apps/prod/`
*   `scripts/scaffold_test.py`
*   `scripts/enforce_emoji_policy.py`

### 2. Determine Intent
*   **Case A: This asset MUST be in Production.**
    * If the asset is ready for prime time, you must switch it from "Experimental" to "Governed."
    * Open the `metadata.yaml` (or the frontmatter of the `.md` file).
    * Verify `metadata.yaml` exists in the directory.
    * Run `python3 scripts/validate_metadata.py`.
    * Check `PLAN_OUTPUT.txt` for compliance tags.
    * Ensure the `domain` matches the directory structure.
    * Change `exempt: true` to `exempt: false` (or remove the field entirely).
    * Ensure all mandated fields (owner, domain, risk_profile) are correctly populated.

*   **Case B: This asset was copied by mistake.**
    * Delete the file from the Production path.
    * If it was intended for testing, move it to `envs/dev/` or `apps/test/`.

### 3. Verification
Run the validation locally before pushing:
```bash
bin/governance check [path/to/file]
```

## Why This Exists
In a "Born Governed" ecosystem, we allow developers to bypass strict rules for rapid prototyping (using `exempt: true`). However, Production is an immutable high-compliance zone. This gate ensures that nothing enters Production without being explicitly declared, owned, and risk-assessed.

---
*Last Updated: 2026-01-07*
