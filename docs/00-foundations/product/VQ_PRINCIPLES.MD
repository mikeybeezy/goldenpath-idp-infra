---
id: VQ_PRINCIPLES
title: VQ Principles & Philosophy
type: documentation
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
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
status: active
category: platform
---

# VQ Principles & Philosophy: Engineering as Value Delivery

In the Golden Path IDP, **Value Quantification (VQ)** is not just a reporting tool—it is the lens through which we prioritize engineering efforts, justify platform investments, and defend developer experience.

## 🧠 The VQ Mindset
Engineering work that is "invisible" is work that is at risk of being defunded or deprioritized. We transform technical toil into visible business value by asking: *"If we automate this, how many hours do we reclaim for the organization?"*

### Engineers as Value Providers
- We do not "fix bugs"; we **reclaim throughput**.
- We do not "update schemas"; we **limit governance debt**.
- We do not "build features"; we **provision capabilities**.

### VQ Principles:
1. **Trust is Default**: Anything that enforces trust, safety, or determinism is High Quality by default.
2. **Rough UX is OK**: Anything user-facing but reversible may ship rough.
3. **Auditability is Non-Negotiable**: No feature may degrade auditability for ease of use.
4. **Accept Friction**: We accept temporary friction to prevent permanent ambiguity.

---

## 🖐️ The 5 Pillars of VQ

1. **Velocity Reclaim**: Every minute saved in a CI loop or a scaffolding workflow is a minute returned to mission-critical product development.
2. **Friction Reduction**: We quantify the "Friction Tax" of broken gates and manual compliance, ensuring that "De-Friction" is treated as a high-priority feature.
3. **Risk Shielding**: By achieving 100% metadata compliance, we move from "Hope-Based Security" to "Evidence-Based Guardrails."
4. **Architectural O(1)**: We value systems that allow us to evolve our repo-wide governance posture in seconds, not weeks.
5. **Human-In-The-Loop (HITL)**: VQ measures the effectiveness of *guiding* humans rather than *blocking* them.

---

## 🛡️ The Anti-Friction Oath
> "We shall not implement a governance gate unless it provides a clear, actionable path for remediation, and its value in risk mitigation exceeds the cost of developer cognitive load."

---

## 🤝 Alignment with HITL Governance
VQ is the fuel for our **Human-In-The-Loop** philosophy. By quantifying the time spent in CI failures, we can identify which "Hard Gates" are causing excessive friction and transition them into "Auto-Healing Guidance."

### How We Use VQ to Decide
- **Work on it if**: The [VQ Reclamation Value](file:///Users/mikesablaze/goldenpath-idp-infra/docs/product/VQ_TAGGING_GUIDE.md) is high and the "Friction Tax" is currently blocking delivery.
- **Skip it if**: The cost of implementing and maintaining the governance check outweighs the theoretical risk it mitigates.

---

> [!IMPORTANT]
> VQ is our common language between the Terminal and the Boardroom. It ensures that the engineering team’s hardest work is understood as a financial asset.
