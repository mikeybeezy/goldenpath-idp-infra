---
id: DECISION_ROUTING_STRATEGY
title: Decision Routing & Governance Strategy
type: policy
domain: platform-core
applies_to: []
owner: platform-team
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
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: governance
status: active
supported_until: '2028-01-01'
---

# Decision Routing & Governance Strategy

## Purpose
This document establishes the **Automated Decision Routing** framework. It ensures that every platform change is governed by the correct domain experts and backed by the required architectural evidence (ADRs, Changelog snippets).

## The Routing Engine
The source of truth for all routing logic is maintained in:
 [**`schemas/routing/agent-routing.yaml`**](schemas/routing/agent-routing.yaml)

### 1. Functional Domain Routing (`by_domain`)
We categorize risk based on the primary area of impact:
- **Critical Control (`identity`, `security`)**: Requires **Security Review** + **ADR** + **Changelog**. No exceptions.
- **Operational Excellence (`delivery`, `observability`, `catalog`)**: Requires **Platform Review** + **Changelog** to ensure downstream awareness.

### 2. Technical Component Routing (`by_component`)
We enforce architectural integrity based on the stack:
- **Core Systems (`infra`, `ci`, `backstage`)**: Requires an **ADR** to justify structural changes.
- **AI Agents (`agents`)**: The highest governance tier. Requires **Dual Approval (Platform + Security)** and full documentation (**ADR + Changelog**).

## Extensibility
This is a **living policy**. To adapt it:
1. **Sync with Enums**: Ensure any new domains or components exist in `schemas/metadata/enums.yaml`.
2. **Modify Approvals**: Update the `agent-routing.yaml` with the new routing requirements.
3. **Guardrail Enforcement**: The `Quality - Metadata Validation` workflow automatically consumes these rules to gate Pull Requests.

---
> [!IMPORTANT]
> This strategy ensures we are "Born Governed," where architectural rigor is baked into the developer workflow rather than added as an after-thought.
