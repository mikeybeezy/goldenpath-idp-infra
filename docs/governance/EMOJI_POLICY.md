---
id: EMOJI_POLICY
title: Emoji Usage Policy
type: policy
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
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
category: governance
status: active
version: 1.0
supported_until: 2028-01-06
breaking_change: false
---

# Emoji Usage Policy

Emojis may be used sparingly and intentionally to improve readability, not to express tone or personality. The goal is to reduce cognitive load, not decorate content.

## 1. Where emojis are allowed

Emojis are permitted only in human-facing, instructional documentation, such as:

- READMEs
- Onboarding guides
- Runbooks
- Operational checklists
- Troubleshooting sections

In these contexts, emojis act as semantic markers to help scanning and comprehension.

## 2. Where emojis are not allowed

Emojis must not be used in authoritative or contractual documents, including:

- Architecture Decision Records (ADRs)
- Governance documents
- Policies
- Contracts
- Schemas (`*.schema.yaml`)
- Metadata definitions
- Security documentation

These documents are long-lived, auditable, and must remain neutral and unambiguous.

## 3. Approved emoji set

Only the following emojis are approved for use:

- ⚠️ Warning / risk
- 🚫 Not allowed / unsupported
- ✅ Required / valid
- 🔒 Security-related note
- 🧪 Experimental / non-production
- 🧭 Guidance / recommendation
- 📌 Important / callout

Expressive or celebratory emojis (e.g. 😁 😂 🔥 🙌 😲) are not permitted.

## 4. Usage rules

- **Semantic Reinforcement**: Emojis must reinforce meaning, not add tone.
- **Section-Level**: Use at most one emoji per section or callout.
- **Heading Placement**: Emojis should appear at the start of headings or callouts, not inline mid-sentence.
- **Preference for Text**: If meaning is clear without an emoji, prefer no emoji.
