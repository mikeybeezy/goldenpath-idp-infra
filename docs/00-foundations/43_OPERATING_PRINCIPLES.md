---
id: 43_OPERATING_PRINCIPLES
title: Platform Operating Principles (Grove + Rumelt)
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 05_OBSERVABILITY_DECISIONS
- 16_INFRA_Build_ID_Strategy_Decision
- 34_PLATFORM_SUCCESS_CHECKLIST
- 44_PRINCIPLES_AND_FRAMEWORKS
------

# Platform Operating Principles (Grove + Rumelt)

Doc contract:
- Purpose: Define operating principles and the versioned signal register.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md, docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/40-delivery/16_INFRA_Build_ID_Strategy_Decision.md, docs/00-foundations/44_PRINCIPLES_AND_FRAMEWORKS.md

These principles guide how we make tradeoffs, prioritize work, and measure
platform progress. They are meant to be practical and enforceable.

## Frameworks reference

For Hohpe, Grove, Rumelt, DDD, and due-diligence mappings, see
docs/00-foundations/44_PRINCIPLES_AND_FRAMEWORKS.md.

## Strategy kernel (Rumelt)

Every major platform initiative must state:
- Diagnosis: the real constraint or failure mode.
- Guiding policy: the stance we will take.
- Coherent actions: the few aligned moves that enforce the stance.

If we cannot state all three, we are not ready to commit effort.

## Principles

1) Output over activity
- Measure outcomes: deploy frequency, lead time, teardown success rate, MTTR.
- If it does not move an outcome, it is not a priority.

2) Bottleneck first
- The constraint sets throughput. Today that is build, promotion, and teardown.
- Fix the slowest, riskiest stage before adding new surface area.

3) Leverage before scale
- Defaults, templates, and automation multiply every team.
- Manual work does not scale and should be encoded into runbooks and scripts.

4) Leading indicators beat lagging indicators
- Track early signals: plan/apply success, teardown time, LB cleanup time.
- Do not wait for incidents to learn.

5) OKRs with explicit owners
- Every reliability target has an owner and a timebox.
- Example: teardown success >= 95% within 30 days.

6) Task-relevant maturity
- Novice teams need guardrails; expert teams need flexibility.
- Defaults are strict; overrides are explicit and logged.

7) Fast, reversible decisions
- Small decisions are made quickly with clear rollback paths.
- Big decisions go to ADRs with stated tradeoffs and the strategy kernel.

8) Platform is a team game
- Docs, runbooks, and onboarding are part of the product.
- If users cannot operate it, it is not shipped.

## Signal register (versioned)

Version: 2026-01-01
Review cadence: 90d
Owner: platform

The signal register is part of this living doc and is versioned in git. It
must reflect developer experience: reduce cognitive load, reduce friction,
and increase discoverability.

| Signal | Why it matters (developer focus) | Owner |
| --- | --- | --- |
| Deploy success rate | Teams can ship without heroics | platform |
| Teardown success rate | Confidence to iterate without cleanup fear | platform |
| p95 build duration | Fast feedback reduces cognitive load | platform |
| p95 teardown duration | Cost/risk predictability for teams | platform |
| Time to first deploy | Onboarding friction and time-to-value | platform |
| Self-serve success rate | Fewer manual escalations | platform |
| Docs access time | Lower friction in discovery and onboarding | platform |
| Catalog coverage | Teams can find what exists | platform |
| Ownership completeness | Clear support paths and accountability | platform |
| Drift rate | Governance proof without manual effort | platform |

## How to use this

When choosing work, prefer items that improve deploy reliability or visibility.
If two options are equal, choose the one that reduces operator judgment.
