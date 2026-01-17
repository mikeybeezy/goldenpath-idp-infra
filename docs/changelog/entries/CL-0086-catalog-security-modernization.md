---
id: CL-0086-catalog-security-modernization
title: 'CL-0086: Catalog Security Hardening & Modernization'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0130
  - CL-0086-catalog-security-modernization
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-08
version: '1.0'
breaking_change: false
---

# CL-0086: Catalog Security Hardening & Modernization

## Date
2026-01-08

## Type
Security / Governance

## Description
Implemented "Zoned Defense" for catalog ingestion and modernized the organizational metadata to reflect the GoldenPath IDP identity.

## Impact
- **Security**: Hardened catalog ingestion by restricting global permissions. Adopted ADR-0130.
- **Branding**: Replaced ACME Corp demo data with GoldenPath IDP core entities.
- **Integrity**: Refactored Domains and Groups to align with canonical `enums.yaml`.
- **Documentation**: Created `BACKSTAGE_CATALOG_GOVERNANCE.md` to house intake rules and timings.
