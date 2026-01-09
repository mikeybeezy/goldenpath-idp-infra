---
id: CL-0086-catalog-security-modernization
title: 'CL-0086: Catalog Security Hardening & Modernization'
type: changelog
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle: active
version: '1.0'
relates_to:
  - CL-0086
supported_until: 2028-01-08
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
