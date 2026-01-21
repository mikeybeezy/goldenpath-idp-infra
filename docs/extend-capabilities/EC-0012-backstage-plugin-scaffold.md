---
id: EC-0012-backstage-plugin-scaffold
title: Backstage Plugin Scaffold - Vanilla Template with Pipeline Integration
type: extension-capability
status: proposed
relates_to:
  - EC-0003-kong-backstage-plugin
  - EC-0004-backstage-copilot-plugin
  - ADR-0171-platform-application-packaging-strategy
  - ADR-0172-cd-promotion-strategy-with-approval-gates
  - agent_session_summary
dependencies:
  - Backstage Scaffolder
  - GitHub Actions
  - ECR + ArgoCD GitOps write-back
priority: medium
vq_class: 🟡 HV/LQ
estimated_roi: Faster time-to-demo + reusable plugin delivery template
effort_estimate: 2-3 weeks
---

## Executive Summary

Create a **vanilla Backstage plugin scaffold** that generates a minimal, working
plugin repo and auto-wires it into the GoldenPath pipeline. The scaffold serves
three goals: (1) a fast proof that the platform works end-to-end, (2) a repeatable
template for extending Backstage, and (3) a foundation for monetization through
paid plugin accelerators.

The scaffold should be intentionally small: one UI page, one API route, a demo
change (visible in the browser), and default CI/CD wiring to ECR and ArgoCD.

## Problem Statement

We need a reliable way to prove the platform pipeline works without hand-crafted
apps, while also enabling teams to create Backstage plugins consistently. Today,
plugin creation is ad-hoc, integration steps are manual, and demo success is not
obvious to non-operators.

## Proposed Solution

### 1) Scaffolder Template

Provide a Backstage Scaffolder template that creates a plugin repo with:
- Plugin UI + backend (minimal, working defaults).
- Built-in demo change (e.g., theme toggle or banner) to prove deployment.
- Standard README and runbook stub.

### 2) Pipeline Auto-Wiring

On creation, the template should:
- Add CI workflow for build + image push to ECR.
- Add GitOps write-back for image tag updates.
- Register the plugin in the Backstage catalog.
- Include ArgoCD app manifest or values entry for deployment.

### 3) Monetization Hooks (Optional)

Keep optional stubs for:
- License check or feature flag.
- Telemetry marker (opt-in).
- “Pro” feature placeholder sections.

## Architecture Integration

- **Backstage**: uses scaffolder template and catalog registration.
- **CI**: standard build pipeline (image build, scan, push).
- **GitOps**: ArgoCD app or values repo entry.
- **ECR**: image repository and tagging strategy.

## Strategic Use Cases

1. **Golden Path demo**: one-click plugin creation + deploy + browser proof.
2. **Internal platform extensions**: consistent plugin structure for teams.
3. **Partner packages**: paid plugin packs or enablement services.
4. **Training**: canonical example for new dev onboarding.

## Implementation Roadmap

### Phase 1: MVP Scaffold (1 week)
- Basic plugin template with working UI route.
- Demo indicator (color/banner change).
- Minimal CI pipeline + catalog registration.

### Phase 2: Pipeline Wiring (1 week)
- ECR push and GitOps write-back.
- ArgoCD app manifest entry.
- Deployment instructions + smoke check.

### Phase 3: Monetization Hooks (optional)
- License/telemetry stubs (opt-in).
- Add-on module structure for premium features.

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-automation hides complexity | Medium | Keep template minimal and transparent |
| CI/Argo assumptions drift | Medium | Pin versions + document required inputs |
| Monetization scope creep | Medium | Keep paid hooks optional and isolated |

## Alternatives Considered

- **Manual plugin setup**: too slow for demos and inconsistent for teams.
- **Monorepo-only plugins**: limits reuse and external collaboration.

## Cost Analysis

Infrastructure cost is minimal (CI minutes + ECR storage). The primary cost is
engineering time to design the template and maintain it.

## Monitoring and Success Metrics

- Scaffold to deployed plugin in <30 minutes.
- One-click demo success rate >90%.
- At least 2 internal teams adopt the template within the first month.
