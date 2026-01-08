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
