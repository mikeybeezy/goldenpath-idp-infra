# Platform TODO (Living)

This is the single rolling backlog. Add items here before starting work.

## Priority legend

- P0: blocking / urgent
- P1: high impact, near-term
- P2: important, can wait
- P3: nice-to-have

## Items

| ID | Priority | Area | Summary | Owner | Status | Effort | Target | Next step | References | Why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 001 | P1 | CI | Defer health-check wiring until multi-env bring-up/teardown is stable | platform | Open | M | Q1 | Stabilize multi-env CI lifecycle | docs/26_POST_APPLY_HEALTH_CHECKS.md, docs/adrs/ADR-0022-platform-post-apply-health-checks.md | Avoid false failures before CI lifecycle is proven |
| 002 | P3 | Security | Introduce SBOM generation for production releases | platform | Open | M |  | Define approach (e.g., Syft/CycloneDX) | docs/28_SECURITY_FLOOR_V1.md | Future supply-chain hardening |
| 003 | P2 | CI | Add CI environment contract validator (hard-fail) | platform | Open | S |  | Define required vars and gating point | docs/21_CI_ENVIRONMENT_CONTRACT.md, docs/adrs/ADR-0011-platform-ci-environment-contract | Enforce required inputs before apply |
| 004 | P2 | GitOps | Configure Argo Rollouts in bootstrap (install + health checks) | platform | Open | M |  | Decide install path and add Argo health checks | docs/29_CD_DEPLOYMENT_CONTRACT.md | Optional rollout safety for V1+ |
| 005 | P2 | Docs | Test doc freshness validator with overdue and missing metadata cases | platform | Open | S |  | Run validator with `--today` and confirm warnings | docs/30_DOCUMENTATION_FRESHNESS.md | Validate mechanism before enforcement |
| 006 | P3 | Docs | Decide if doc freshness check should become a hard gate | platform | Open | S |  | Evaluate after tests and initial adoption | docs/30_DOCUMENTATION_FRESHNESS.md | Avoid over-enforcement in V1 |

## Rules

- Keep items short and specific.
- Update Status + Next step whenever you touch an item.
- Use P0 sparingly.

****
