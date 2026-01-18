---
id: CL-0147
title: Governance Registry Sync for RDS/EKS/S3
type: changelog
status: active
date: 2026-01-18
author: platform-team
category: ci-workflow
relates_to:
  - ADR-0170-s3-self-service-request-system
  - ADR-0168-eks-request-parser-and-mode-aware-workflows
  - ADR-0165-rds-user-db-provisioning-automation
  - SCRIPT-0037
  - SCRIPT-0043
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
