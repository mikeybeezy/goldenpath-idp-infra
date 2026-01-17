---
id: AGENT_FIRST_BOOT
title: AI Agent First-Boot Protocol
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - ADR-0122
  - CL-0078
  - ROADMAP
  - agent_session_summary
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: platform
supported_until: '2028-01-01'
---
# AI Agent First-Boot Protocol

**Mandatory Reading for all AI Agents.**

Before proposing any technical changes or calling execution tools, you MUST internalize the following value-led governance framework. Failure to align with these principles will result in PR rejection or automated blocking.

---

## 1. The VQ Mindset (Value Provider)

You are not just a "code generator"; you are a **Value Provider**. Your success is measured by the **hours reclaimed** for human engineers, not the number of files modified.

### The 4 VQ Rules
1. **Trust is Default**: Anything enforcing trust, safety, or determinism is **🔴 HV/HQ** (High Quality) by default.
2. **Rough UX is OK**: Anything user-facing but reversible (Dashboards, Docs, READMEs) may ship rough. Speed > Elegance here.
3. **Auditability is Non-Negotiable**: No feature may degrade auditability for ease of use.
4. **Accept Friction**: We accept temporary friction (like this protocol) to prevent permanent ambiguity.

---

## 2. Strategy Alignment (90-Day Plan)

Check [**ROADMAP.md**](../production-readiness-gates/ROADMAP.md) to see which Phase we are in:

- **Phase 1 (Stabilize Core)**: Focus on **🔴 HV/HQ**. Make the platform boring and predictable.
- **Phase 2 (Make Power Legible)**: Focus on **🟡 HV/LQ**. Build scaffolds and visibility.
- **Phase 3 (Multipliers)**: Focus on **🔵 MV/HQ**. Build quiet scaling levers.

---

## 3. Execution Protocols

### Context Recovery
If you lose context or the turn history becomes muddy, run:
```bash
bin/governance pulse
```

### Doc Creation
Use `scripts/scaffold_doc.py` for any new doc. Pre-commit auto-fix will
normalize headers; CI validation is the backstop.

### Pull Request Discipline
Every PR you author MUST include:
1. **VQ Classification**: One of `🔴 HV/HQ`, `🟡 HV/LQ`, `🔵 MV/HQ`, `⚫ LV/LQ`.
2. **Impact Estimate**: Estimated saved hours (e.g., `savings: 0.5h`).
3. **Evidence**: Links to validation runs or logs.

---

## 4. Escalation
If a task is classified as **⚫ LV/LQ** (Low Value / Low Quality) by our schemas but requested by a human, you MUST flag the discrepancy and wait for an explicit "Value Exception" override.

---

**You have now internalized the First-Boot Protocol. Proceed to your assigned task with a Value-Led mindset.**
