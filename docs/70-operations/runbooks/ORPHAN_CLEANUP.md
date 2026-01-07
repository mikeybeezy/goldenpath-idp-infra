---
id: ORPHAN_CLEANUP
title: Orphan Cleanup
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
schema_version: 1
relates_to:
  - TEARDOWN_README
  - 10_REPO_DECOMMISSIONING
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0036
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
version: 1.0
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# Orphan Cleanup

## Purpose

This is a living reference for identifying and cleaning orphan resources after
failed or partial runs. Orphan cleanup is a **manual, explicit action** executed
via workflow or CLI, not an automatic teardown step.

## What is an orphan resource?

An orphan resource is any cloud resource that was created by the platform but
is no longer tracked by Terraform state (or is outside the intended lifecycle)
and therefore would not be destroyed by normal teardown.

## Blind spots to watch

- **Permissions drift:** orphan cleanup needs `tag:GetResources` plus delete
  rights across EC2/ELB/EKS/IAM. If one permission is missing, cleanup silently
  leaves stragglers.
- **Tag gaps:** any resource missing `BuildId` or `Environment` won’t be cleaned.
  Enforce tags in Terraform and bootstrap tooling.
- **Timing/order:** deleting EKS before LB/NAT cleanup can leave AWS resources
  stuck. Orphan cleanup should explicitly handle dependency order and retries.
- **State vs reality:** if state is missing/corrupt, Terraform won’t delete.
  Orphan cleanup must be able to handle “no state” runs.
- **Race with AWS eventual consistency:** delete calls may take minutes; retries
  and backoff are needed or cleanup will report “failed” even though AWS is
  still working.
- **Cost spikes:** orphan cleanup does broad scans. In large accounts it’s slow
  and expensive unless you filter by tag and region aggressively.
- **False positives:** if `BuildId` reuse happens, cleanup can remove “current”
  resources by mistake. This makes `BuildId` uniqueness critical.
- **Error visibility:** cleanup failures must be summarized clearly or they’ll
  be ignored; otherwise you get silent resource leaks.
