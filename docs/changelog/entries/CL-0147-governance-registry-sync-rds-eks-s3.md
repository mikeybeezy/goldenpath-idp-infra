<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0147
title: Governance Registry Sync for RDS/EKS/S3
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0165
  - ADR-0168
  - ADR-0170
  - EC-0005-kubernetes-operator-framework
  - SCRIPT-0037
  - SCRIPT-0043
  - agent_session_summary
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-18
author: platform-team
---

# CL-0147: Governance Registry Sync for RDS/EKS/S3

## Summary

Aligned S3, EKS, and RDS request flows to persist governance outputs in-repo,
closing the loop between apply workflows and catalog/audit artifacts.

## Changes

### Added

- **S3**: Apply workflow writes catalog + audit outputs
  - `docs/20-contracts/resource-catalogs/s3-catalog.yaml`
  - `governance/{environment}/s3_request_audit.csv`
- **EKS**: Apply workflow writes catalog + audit outputs
  - `docs/20-contracts/resource-catalogs/eks-catalog.yaml`
  - `governance/{environment}/eks_request_audit.csv`
- **RDS**: Provisioning workflow persists audit trail
  - `governance/{environment}/rds_request_audit.csv`

### Updated

- Schemas document the catalog/audit outputs:
  - `schemas/requests/s3.schema.yaml`
  - `schemas/requests/eks.schema.yaml`
  - `schemas/requests/rds.schema.yaml`

## Notes

- Audit records are git-tracked for traceability alongside request contracts.
