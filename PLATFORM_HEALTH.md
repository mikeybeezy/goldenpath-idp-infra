---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-16'
relates_to:
  - 01_adr_index
  - DOCS_CHANGELOG_README
  - SCRIPT_CERTIFICATION_MATRIX
  - platform_health.py
---
## 🏥 Platform Health Command Center

**Generated**: `2026-01-16 08:25:16` | **V1 Readiness**: `93.0%` | **Mean Confidence**: `⭐ (1.3/5.0)`

**Realized Value**: `133.4 Hours` | **Infra Run Rate**: `$1,250.00 USD/mo`

## V1 Platform Readiness Gate

> [!IMPORTANT]
> The platform is currently **93.0%** ready for V1 production rollout.

|Milestone|Status|Readiness|
|:---|:---|:---|
|**Metadata Integrity**|✅|100.0%|
|**Injection Integrity**|✅|100.0%|
|**Architecture Maturity**|🚧|95/146 Active|
|**Changelog Activity**|✅|136 Entries|

## Knowledge Graph Vitality

|Metric|Count|Source|
|:---|:---|:---|
|**Architecture Decisions**|146|[ADR Index](docs/adrs/01_adr_index.md)|
|**Automation Scripts**|47|[Script Index](scripts/index.md)|
|**Certified Scripts (M3)**|1/47 (2%)|[Certification Matrix](docs/10-governance/SCRIPT_CERTIFICATION_MATRIX.md)|
|**CI Workflows**|44|[Workflow Index](ci-workflows/CI_WORKFLOWS.md)|
|**Change Logs**|136|[Changelog Index](docs/changelog/README.md)|
|**Tracked Resources**|620|Repository Scan|

## Catalog Inventory

|Catalog|Entity Count|
|:---|:---|
|Ecr Registry|1|
|Ecr Repositories|11|
|IDP Apis|9|
|IDP Components|18|
|IDP Domains|4|
|IDP Resources|14|
|IDP Systems|5|

## AWS Inventory Snapshot

- **Last run**: `2026-01-10T00:44:01Z`
- **Accounts**: `REDACTED`
- **Regions**: `eu-west-2`
- **Total resources**: `31`
- **Tagged**: `29` | **Untagged**: `2` | **Tag violations**: `29`
- **Report**: [`reports/aws-inventory/aws-inventory-2026-01-10.md`](reports/aws-inventory/aws-inventory-2026-01-10.md)

## 🛡️ Risk & Maturity Visualization

```mermaid
pie title Production Impact distribution
    "HIGH" : 50
    "MEDIUM" : 33
    "LOW" : 449
    "NONE" : 86
```

## Governance Maturity

- **Metadata Compliance**: `100.0%`
- **Risk-Weighted Score**: `100.0%`

## Injection Coverage

- **Sidecar Coverage**: `100.0%` (35/35)

## Project Realized Value (Heartbeat)

> [!TIP]
> Total realized value reclaimed through automation heartbeats: **133.4 hours**.

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
