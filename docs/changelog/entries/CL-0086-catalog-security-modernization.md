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
