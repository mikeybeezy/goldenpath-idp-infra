<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: EC-0011-break-glass-rds-destroy
title: Break-Glass RDS Destroy - Elegant Friction for Database Teardown
type: extension-capability
status: implemented
relates_to:
  - CL-0153-standalone-rds-state
  - RB-0033-persistent-cluster-teardown
  - session_capture/2026-01-20-persistent-cluster-deployment
priority: medium
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: high
  potential_savings_hours: 8.0
  confidence: high
  rationale: 'Replaces manual AWS Console click-ops with auditable, break-glass destruction.

    Prevents fat-finger mistakes while maintaining IaC principles.

    8 hours = time saved per incident from clear audit trail and reduced confusion.

    '
effort_estimate: 4-6 hours (Makefile + documentation + testing)
---

## Executive Summary

Replace manual AWS Console operations for RDS deletion with a codified **Break-Glass Mechanism** that provides:
- Explicit safety friction (deliberate confirmation flags)
- Full audit trail (who, when, what)
- IaC-compliant destruction (no console click-ops)

**Origin**: Feedback from session 2026-01-20 (Antigravity Agent) noting that the standalone RDS approach is "correct for safety but inelegant in implementation."

## Problem Statement

### Current State

The standalone RDS architecture (CL-0153) intentionally has **no standard `make rds-destroy` target** to prevent accidental deletion. When RDS teardown is required, the only supported path is the confirmation-gated `rds-destroy-break-glass` target.

### Why This Matters

| Aspect | Console Click-Ops | Break-Glass Target |
|--------|-------------------|-------------------|
| Auditability | None | Full (logged) |
| IaC Compliance | Broken | Maintained |
| Error Rate | High | Low (gated) |
| Reproducibility | None | 100% |
| Safety Friction | None | Deliberate |

## Implemented Solution

### Makefile Target (Break-Glass, Confirmation-Gated)

The Makefile now includes a confirmation-gated destroy target that:
- Disables AWS deletion protection.
- Temporarily flips Terraform `prevent_destroy` in `envs/<env>-rds/main.tf`.
- Streams output to a timestamped log.

```bash
# Will fail without confirmation
make rds-destroy-break-glass ENV=dev

# Explicit confirmation required
make rds-destroy-break-glass ENV=dev CONFIRM_DESTROY_DATABASE_PERMANENTLY=YES
```

### Optional: Manual Toggle (main.tf)

If you prefer manual control, temporarily set `prevent_destroy = false` in
`envs/<env>-rds/main.tf`, then run:

```bash
terraform -chdir=envs/<env>-rds destroy -auto-approve
```

## Value Quantification

| Metric | Value | Rationale |
|--------|-------|-----------|
| VQ Class | 🟢 HV/HQ | High value (safety + audit), high quantifiability |
| Impact Tier | High | Prevents data loss, enables compliance |
| Potential Savings | 8 hours/incident | Clear audit trail reduces investigation time |
| Confidence | High | Well-understood problem, straightforward solution |

### ROI Calculation

- **Without target**: 2 hours manual console work + 4 hours investigation when something goes wrong + 2 hours explaining to stakeholders = 8 hours
- **With break-glass target**: 5 minutes execution + audit-friendly logs = ~0 hours investigation
- **Implementation cost**: 4-8 hours one-time

**Payback**: First incident avoided

## Implementation Steps

1. Add confirmation-gated `rds-destroy-break-glass` Makefile target.
2. Update runbooks and quick reference to document the break-glass path.
3. Validate in dev environment before production use.

## Security Considerations

- Target requires explicit `CONFIRM_DESTROY_DATABASE_PERMANENTLY=YES`.
- Destruction output is logged to `logs/build-timings/` for audit review.
- Consider adding MFA/token validation for production environments.

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| No destroy capability | Current state - breaks IaC principles |
| Standard `make rds-destroy` | Too easy to accidentally run |
| Console-only deletion | No audit trail, click-ops |
| Require ticket approval | Adds process friction without technical safety |

## Success Criteria

- [ ] Makefile target `rds-destroy-break-glass` works with confirmation.
- [ ] RB-0030 and RB-0033 reflect the break-glass flow.
- [ ] At least one successful test destruction in dev.

---

Signed: Claude Opus 4.5 (2026-01-20T17:45:00Z)
