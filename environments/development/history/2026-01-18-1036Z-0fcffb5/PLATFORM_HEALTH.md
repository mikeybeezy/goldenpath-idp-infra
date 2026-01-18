---
type: governance-report
env: development
generated_at: 2026-01-18T10:35:50Z
source:
  branch: development
  sha: 0fcffb5f1cac2be325aa830f10af93c2d4d4dce7
pipeline:
  workflow: Governance Registry Writer
  run_id: 21110322466
integrity:
  derived_only: true
---
---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-18'
relates_to:
  - platform_health.py
---

## 🏥 Platform Health Command Center

**Generated**: `2026-01-18 10:35:58` | **V1 Readiness**: `92.0%` | **Mean Confidence**: `⭐ (1.3/5.0)`

**Realized Value**: `155.4 Hours` | **Infra Run Rate**: `$1,250.00 USD/mo`

## V1 Platform Readiness Gate

> [!IMPORTANT]
> The platform is currently **92.0%** ready for V1 production rollout.

| Milestone | Status | Readiness |
| :--- | :--- | :--- |
| **Metadata Integrity** | ✅ | 100.0% |
| **Injection Integrity** | ✅ | 100.0% |
| **Architecture Maturity** | 🚧 | 96/160 Active |
| **Changelog Activity** | ✅ | 145 Entries |

## Knowledge Graph Vitality

| Metric | Count | Source |
| :--- | :--- | :--- |
| **Architecture Decisions** | 160 | [ADR Index](docs/adrs/01_adr_index.md) |
| **Automation Scripts** | 50 | [Script Index](scripts/index.md) |
| **Certified Scripts (M3)** | 1/51 (2%) | [Certification Matrix](docs/10-governance/SCRIPT_CERTIFICATION_MATRIX.md) |
| **CI Workflows** | 60 | [Workflow Index](ci-workflows/CI_WORKFLOWS.md) |
| **Change Logs** | 145 | [Changelog Index](docs/changelog/README.md) |
| **Tracked Resources** | 644 | Repository Scan |

## Catalog Inventory

| Catalog | Entity Count |
| :--- | :--- |
| Ecr Registry | 1 |
| Ecr Repositories | 11 |
| Eks | 1 |
| IDP Apis | 9 |
| IDP Components | 18 |
| IDP Domains | 4 |
| IDP Resources | 14 |
| IDP Systems | 5 |
| Rds | 1 |

## AWS Inventory Snapshot

- **Last run**: `2026-01-09T23:55:30Z`
- **Accounts**: `REDACTED`
- **Regions**: `eu-west-2`
- **Total resources**: `33`
- **Tagged**: `31` | **Untagged**: `2` | **Tag violations**: `30`
- **Report**: [`reports/aws-inventory/aws-inventory-2026-01-09.md`](reports/aws-inventory/aws-inventory-2026-01-09.md)

## 🛡️ Risk & Maturity Visualization

```mermaid
pie title Production Impact distribution
    "HIGH" : 36
    "MEDIUM" : 38
    "LOW" : 463
    "NONE" : 105
```

## Governance Maturity

- **Metadata Compliance**: `100.0%`
- **Risk-Weighted Score**: `100.0%`

## Injection Coverage

- **Sidecar Coverage**: `100.0%` (35/35)

## Project Realized Value (Heartbeat)

> [!TIP]
> Total realized value reclaimed through automation heartbeats: **155.4 hours**.

- **ROI Ledger**: [.goldenpath/value_ledger.json](.goldenpath/value_ledger.json)

## Financial Governance (Cloud Cost)

> [!NOTE]
> Current monthly infrastructure run rate: **$1,250.00 USD**.

- **Estimated Annual**: `$15,000.00 USD`
- **Cost Ledger**: [.goldenpath/cost_ledger.json](.goldenpath/cost_ledger.json)
- **Tooling**: Infracost (CI-integrated)

## Operational Risks

- **Orphaned (No Owner)**: 0
- **Stale (Past Lifecycle)**: 0

---

### Strategic Guidance

- **V1 Readiness Indicator**: A composite metric tracking Architecture (ADRs), Governance (Metadata/Injection), and Delivery (Changelogs). Target: 100%.
- **Visualizing Trends**: The `xychart-beta` is best viewed in GitHub/GitLab or VS Code with updated Mermaid support (v10.x+). It tracks our 'Readiness Velocity' across audit cycles.

<!-- AUTOMATED REPORT - DO NOT EDIT MANUALLY -->
