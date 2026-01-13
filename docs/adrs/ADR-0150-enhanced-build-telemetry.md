---
id: ADR-0150-enhanced-build-telemetry
title: 'ADR-0150: Enhanced Build Telemetry with Resource Context'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---

# ADR-0150: Enhanced Build Telemetry with Resource Context

## Proposer
Platform Team

## Status
Proposed

## Context
We currently track build duration via `docs/build-timings.csv`. However, raw duration is an insufficient metric for platform performance. A 17-minute build that provisions an entire EKS cluster is highly efficient, while a 17-minute build that changes a single ConfigMap is a performance regression.

Without context on *what* was built (resource churn), it is impossible to calculate "Velocity" or detect "Zombie Builds" (builds that hang but eventually succeed or fail).

## Decision
We will enhance the platform build system to capture and record **Resource Context** during Terraform operations.

Specifically, we will:
1.  Parse the `terraform apply` final output to extract:
    *   `Resources Added`
    *   `Resources Changed`
    *   `Resources Destroyed`
2.  Update the `docs/build-timings.csv` schema to include these new fields.
3.  Update the `Makefile` and `generate-build-log.sh` logic to scrape and persist this data.

## Consequences
### Positive
*   **Contextual Performance**: Allows calculation of "Time per Resource" metrics.
*   **Anomaly Detection**: Makes it easier to spot hangs (High duration / Low resource count).
*   **Auditability**: Provides a high-level summary of change magnitude over time in a simple CSV.

### Negative
*   **Schema Change**: Existing CSV parsers (if any) will need to adapt to the new columns. (We will handle backward compatibility by appending columns).
*   **Complexity**: parsing text output (CLI scraping) is inherently brittle compared to structured JSON, but Terraform's structured JSON output (`-json`) is verbose and difficult to stream in real-time CI logs. We will stick to regex on the final summary line for simplicity.

## Governance
This aligns with the **"Born Governed"** observability pillar by increasing the fidelity of our operational metrics.
