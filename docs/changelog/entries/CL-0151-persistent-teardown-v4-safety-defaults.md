<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0151
title: Persistent Teardown V4 Safety Defaults
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - Makefile
  - bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v4.sh
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - RB-0033-persistent-cluster-teardown
  - 06_REBUILD_SEQUENCE
supersedes: []
superseded_by: []
tags:
  - teardown
  - persistent
  - safety
inheritance: {}
supported_until: 2028-01-20
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: low
  potential_savings_hours: 1.0
date: 2026-01-20
author: platform-team
---

# Persistent Teardown V4 Safety Defaults

## Summary

Persistent teardown now uses the v4 teardown script with safety defaults that
prevent accidental deletion of RDS instances and Secrets Manager data.

## Impact

- `teardown-persistent` calls `goldenpath-idp-teardown-v4.sh`.
- Defaults set in the Makefile:
  - `DELETE_RDS_INSTANCES=false`
  - `RDS_SKIP_FINAL_SNAPSHOT=false`
  - `DELETE_SECRETS=false`

## Files

- `Makefile`
