---
id: PLATFORM_SCRIPTS_INDEX
title: Platform Automation Scripts Index
type: documentation
category: tooling
version: '1.0'
owner: platform-team
status: active
dependencies:
  - python3
  - pyyaml
risk_profile:
  production_impact: low
  security_risk: medium
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - PLATFORM_HEALTH
  - METADATA_VALIDATION_GUIDE
  - METADATA_MAINTENANCE_GUIDE
---

# Platform Automation Scripts Index

This directory contains the automation engine powering the GoldenPath IDP. These scripts handle everything from metadata governance and health reporting to documentation formatting and relationship extraction.

## Core Governance Scripts

| Script | Purpose | Achievement |
| :--- | :--- | :--- |
| [`standardize_metadata.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/standardize_metadata.py) | **The Healer** | Automated schema remediation, sidecar generation, and **Metadata Injection**. |
| [`validate_metadata.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/validate_metadata.py) | **The Quality Gate** | PR-level enforcement of metadata compliance, sidecar presence, and **Injection Verification**. |
| [`extract_relationships.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/extract_relationships.py) | **The Graph Builder** | Programmatic extraction of document relationships and dependencies. |
| [`platform_health.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/platform_health.py) | **The Reporter** | Generation of global health metrics and **Injection Coverage** auditing. |
| [`render_template.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/render_template.py) | **The Renderer** | Backstage-compatible templating with **Nested Key Support**. |

## Documentation & Formatting

- [`format_docs.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/format_docs.py): Global whitespace and frontmatter normalizer.
- [`check_doc_freshness.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/check_doc_freshness.py): Audits document lifecycle and staleness.
- [`check_doc_index_contract.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/check_doc_index_contract.py): Verifies that indexes adhere to the platform contract.

## Deployment & Teardown Logging

- [`generate-build-log.sh`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/generate-build-log.sh): Captures detailed EKS/Terraform build logs.
- [`generate-teardown-log.sh`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/generate-teardown-log.sh): Captures managed-resource cleanup logs during teardown.
- [`resolve-cluster-name.sh`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/resolve-cluster-name.sh): Dynamic discovery of EKS cluster context.

## Maintenance & Utilities

- [`backfill_metadata.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/backfill_metadata.py): Legacy batch backfill utility.
- [`check_compliance.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/check_compliance.py): Secondary audit tool for metadata syntax.
- [`migrate_partial_metadata.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/migrate_partial_metadata.py): Handles schema transitions for complex fields.
- [`test_platform_health.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/test_platform_health.py): Unit tests for the health reporter.
- [`reliability_metrics.sh`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/reliability_metrics.sh): Calculates MTTR/MTBF for platform components.
