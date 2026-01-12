---
id: PLATFORM_HEALTH_PROPOSED_UPDATES
title: Platform Health Proposed Updates
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
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
category: platform
---

# Platform Health Proposed Updates

Purpose: capture recommended health metrics, data sources, and lightweight
implementation steps to strengthen V1 signal quality without heavy rework.

## A) Metadata Field Usage Guidance

### Recommended doc types for value_intent / value_unit / inefficiency_type

| Doc Type | Should Carry Fields? | Rationale | Suggested Fields |
| --- | --- | --- | --- |
| ADRs | Yes | Decisions should declare value intent and expected trade-offs. | value_intent, value_unit |
| Changelogs | Yes (lightweight) | Helps tie releases to outcomes. | value_intent |
| Runbooks | No | Operational guides should stay procedural. | None |
| Governance Docs | Yes (selective) | Policies can clarify expected value outcomes. | value_intent |
| Reports (health/audit) | Yes | Reporting should quantify value and inefficiency. | value_intent, value_unit, inefficiency_type |
| Roadmap / Scope | Yes | Prioritization should map to value intent. | value_intent |
| Templates | Optional | Scaffolds can set defaults, but not required. | value_intent |
| Technical Design Docs | Optional | Only if value outcome is explicit. | value_intent |

### Doc types that should NOT carry these fields

| Doc Type | Why |
| --- | --- |
| README / Onboarding | Avoid noise and drift. |
| Build/Run Logs | Logs should be factual execution records. |
| Policies that are purely procedural | No value claim needed. |

### Terraform / AWS resources?

Not recommended for direct inclusion in resource tags or TF configs.
- Tags have strict limits and should stay operational (owner, env, cost, risk).
- Value intent belongs in governance/docs, not infrastructure resources.
- If needed, capture value intent in a catalog contract doc adjacent to TF.

## B) Proposed Outcome Metrics (V1)

| Metric | Definition | Source | Notes |
| --- | --- | --- | --- |
| Plan success rate | Successful plan runs / total | CI logs | Per 7/30 days |
| Apply success rate | Successful apply runs / total | CI logs | Per 7/30 days |
| Teardown success % | Successful teardown / total | Build run logs | Needs consistent status field |
| Bootstrap p95 | 95th percentile duration | Build run logs | Requires duration field |
| Drift rate | Plans with non-zero changes in "no-change" contexts | CI logs | Must tag runs as drift checks |
| Catalog sync latency | PR merge time to entity visible | Catalog timestamps | Use event time + generated entity time |
| ECR time-to-ready | PR merge to repo visible in Backstage | GitHub + catalog | Track in ECR flow |

## C) Implementation Steps (Lightweight)

| Step | Change | Effort | Impact | Notes |
| --- | --- | --- | --- | --- |
| 1 | Add outcome metrics schema (JSON) | S | High | Store in docs/10-governance/reports |
| 2 | Add aggregation script | M | High | Parse CI logs + build logs |
| 3 | Extend platform_health.py | S | High | Surface metrics in dashboard |
| 4 | Add ECR time-to-ready capture | M | High | Use PR merge timestamp + catalog update time |
| 5 | Add metadata fields to schema | M | Medium | Update validator + templates |
| 6 | Add dashboard section for inefficiencies | S | Medium | Highlight top 3 bottlenecks |

## D) Proposed OUTCOME_METRICS.json (Draft)

Suggested fields:
- window_days
- plan_success_rate
- apply_success_rate
- teardown_success_rate
- bootstrap_p95_seconds
- drift_rate
- catalog_sync_latency_seconds
- ecr_time_to_ready_seconds
- last_updated

## E) Size of Metadata Schema Update

Estimate: **medium** (1-2 days)
- Update schema definition and validator.
- Update templates (ADR/changelog) to include fields.
- No bulk backfill required; start forward-only.

## F) Open Decisions

| Decision | Options | Recommendation |
| --- | --- | --- |
| Value fields in templates | Default vs optional | Optional, then enforce in ADRs only |
| Where to store outcome metrics | JSON vs markdown | JSON for compute, markdown for human read |
| ECR time-to-ready | Event-based vs cron | Event-based + cron backstop |
