<!--  AUTOMATED REPORT - DO NOT EDIT MANUALLY  -->
---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-07'
relates_to:
  - platform_health.py
---

# Platform Health Command Center
**Generated**: `2026-01-07 09:35:26` | **V1 Readiness**: `94.9%` | **Mean Confidence**: `⭐(1.2/5.0)`
**Realized Value**: `4.4 Hours` | **Infra Run Rate**: `$1,250.00 USD/mo`

## V1 Platform Readiness Gate
> [!IMPORTANT]
> The platform is currently **94.9%** ready for V1 production rollout.

| Milestone | Status | Readiness |
| :--- | :--- | :--- |
| **Metadata Integrity** | ✅ | 97.3% |
| **Injection Integrity** | ✅ | 100.0% |
| **Architecture Maturity** |  | 93/119 Active |
| **Changelog Activity** | ✅ | 86 Entries |

## Governance Velocity (Historical Trend)
```mermaid
xychart-beta
    title "V1 Readiness Trend (Last 10 Runs)"
    x-axis ["Run -3", "Run -1"]
    y-axis "Readiness %" 0 --> 100
    line [100.0, 100.0, 100.0]
```

## Knowledge Graph Vitality
| Metric | Count | Source |
| :--- | :--- | :--- |
| **Architecture Decisions** | 119 | [ADR Index](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/01_adr_index.md) |
| **Automation Scripts** | 31 | [Script Index](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/index.md) |
| **CI Workflows** | 0 | [Workflow Index](file:///Users/mikesablaze/goldenpath-idp-infra/ci-workflows/CI_WORKFLOWS.md) |
| **Change Logs** | 86 | [Changelog Index](file:///Users/mikesablaze/goldenpath-idp-infra/docs/changelog/README.md) |
| **Tracked Resources** | 441 | Repository Scan |

## Catalog Inventory
| Catalog | Entity Count |
| :--- | :--- |

## Risk & Maturity Visualization
```mermaid
pie title Production Impact distribution
    "HIGH" : 36
    "MEDIUM" : 32
    "LOW" : 356
    "NONE" : 16
```

## Governance Maturity
- **Metadata Compliance**: `97.3%`
- **Risk-Weighted Score**: `100.0%`

## Injection Coverage
- **Sidecar Coverage**: `100.0%` (32/32)

## Project Realized Value (Heartbeat)
> [!TIP]
> Total realized value reclaimed through automation heartbeats: **4.4 hours**.
- **ROI Ledger**: [.goldenpath/value_ledger.json](file:///Users/mikesablaze/goldenpath-idp-infra/.goldenpath/value_ledger.json)

## Financial Governance (Cloud Cost)
> [!NOTE]
> Current monthly infrastructure run rate: **$1,250.00 USD**.
- **Estimated Annual**: `$15,000.00 USD`
- **Cost Ledger**: [.goldenpath/cost_ledger.json](file:///Users/mikesablaze/goldenpath-idp-infra/.goldenpath/cost_ledger.json)
- **Tooling**: Infracost (CI-integrated)

## Operational Risks
- **Orphaned (No Owner)**: 0
- **Stale (Past Lifecycle)**: 0

---
### Strategic Guidance
- **V1 Readiness Indicator**: A composite metric tracking Architecture (ADRs), Governance (Metadata/Injection), and Delivery (Changelogs). Target: 100%.
- **Visualizing Trends**: The `xychart-beta` is best viewed in GitHub/GitLab or VS Code with updated Mermaid support (v10.x+). It tracks our 'Readiness Velocity' across audit cycles.
