---
id: CL-0084-backstage-ecr-instrumentation
title: 'CL-0084: Backstage VQ Alignment and ECR Instrumentation'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
lifecycle: active
version: '1.0'
relates_to:
  - CL-0084
supported_until: 2028-01-08
breaking_change: false
---

# CL-0084: Backstage VQ Alignment and ECR Instrumentation

## Date
2026-01-08

## Type
Feature / Governance

## Description
Fully operationalized the Backstage Helm suite and instrumented AWS ECR resources into the IDP catalog.

## Impact
- **Governance**: Classified `backstage-helm` as a High Value (HV) asset with its own `metadata.yaml`.
- **Automation**: Created `scripts/deploy-backstage.sh` which automates both the portal and its managed database (CNPG) with built-in ROI heartbeats.
- **Instrumentation**: Created `scripts/generate_backstage_ecr.py` to map container registries into the IDP.
- **Reporting**: Expanded the Platform Health dashboard to track 11 new ECR resources, increasing total IDP resource coverage by 1100%.
- **Stability**: Resolved mislocated metadata configuration to stabilize repository CI gates.
