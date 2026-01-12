---
id: CONFIDENCE_MATRIX
title: Automation Confidence Matrix
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
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
status: active
category: governance
---

# IDP Automation Confidence Matrix (Five-Star Approval)

> "As velocity increases, the cost of brittleness becomes exponential. We don't just ship; we certify."

To maintain a 100% Green governance state at high speed, every script and workflow must pass through this multi-dimensional testing matrix to receive its **Confidence Rating**.

---

## 🟢 Surface Areas & Certifications

| Surface Area | Focus | Certification Requirements |
| :--- | :--- | :--- |
| **1. Logic** | Code Reliability | - **Unit Tests**: Mandatory coverage for logic forks.<br>- **Error Handling**: No silent failures; graceful exits.<br>- **Linting**: 100% compliance with `ruff`/`yamllint`. |
| **2. Safety** | Operational Risk | - **Idempotency**: Execution is a no-op if state already matches.<br>- **Dry-Run Mode**: Mandatory `-d` or `--dry-run` support.<br>- **Resource Cleanup**: Automated teardown of temporary state. |
| **3. Context** | Governance | - **Traceability**: Hard-gate link to ADR and Changelog.<br>- **VQ Class**: Explicit classification (e.g., 🔴 HV/HQ).<br>- **Heartbeat**: Integrated with `vq_logger.py`. |
| **4. Human** | Developer Experience | - **Self-Doc**: `--help` provides usable examples.<br>- **Log Quality**: Structured info/error messaging.<br>- **Ownership**: Explicit `owner` tag in metadata. |
| **5. System** | Integration | - **CI/CD Gated**: Restricted to protected branch execution.<br>- **Multi-Env**: Verified in `dev`, `test`, and `prod`.<br>- **Rollback**: Documented and tested `revert` path. |

---

## Maturity Rating Scale

| Rating | Tier | Description |
| :--- | :--- | :--- |
| **** | **Experimental** | Script exists, passes linter, and solves a local problem. |
| **** | **Documented** | Linked to ADR/CL; has VQ classification and assigned owner. |
| **** | **Validated** | Supports Idempotency and Dry-run; passes unit tests. |
| **** | **Certified** | Verified via "Field Test" in onboarding; uses Zero-Trust perms. |
| **** | **Golden Core** | Immutable, fully observable, and verified across all environments. |

---

## Implementation Plan (Phase 4)

1.  **Metadata Update**: Add `maturity: [1-5]` to `reliability` block in metadata.
2.  **Audit Integration**: Update `scripts/platform_health.py` to calculate the "Mean Confidence Score" of the repo.
3.  **Hard Gate**: Update `pr_guardrails.py` to require  for any script moving to `🔴 HV/HQ` (Core).
