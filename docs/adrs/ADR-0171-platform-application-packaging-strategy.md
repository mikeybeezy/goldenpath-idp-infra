---
id: ADR-0171-platform-application-packaging-strategy
title: 'ADR-0171: Application Packaging Strategy - Helm vs Kustomize'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: high
  potential_savings_hours: 4.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 20_TOOLING_APPS_MATRIX
  - 42_APP_EXAMPLE_DEPLOYMENTS
  - ADR-0020-platform-helm-kustomize-hybrid
  - ADR-0172-cd-promotion-strategy-with-approval-gates
  - CL-0148
  - EC-0005-kubernetes-operator-framework
  - agent_session_summary
  - audit-20260103
  - session-capture-2026-01-18-local-dev-hello-app
supersedes:
  - ADR-0020-platform-helm-kustomize-hybrid
superseded_by: []
tags:
  - packaging
  - helm
  - kustomize
  - gitops
inheritance: {}
supported_until: 2028-01-18
version: '1.0'
breaking_change: false
---

# ADR-0171: Application Packaging Strategy - Helm vs Kustomize

- **Status:** Active
- **Date:** 2026-01-18
- **Owners:** platform-team
- **Domain:** Platform
- **Decision type:** Architecture
- **Supersedes:** ADR-0020-platform-helm-kustomize-hybrid
- **Related:** `docs/40-delivery/42_APP_EXAMPLE_DEPLOYMENTS.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

ADR-0020 established that we use a hybrid approach (Helm + Kustomize) but did
not provide clear guidance on **when to choose each tool**. This led to
inconsistent decisions and confusion about whether new applications should use
Helm charts or Kustomize bases.

We need explicit criteria that teams can follow when packaging applications.

---

## Decision

### The Core Principle

**Helm is for distribution. Kustomize is for deployment.**

| Tool | Mental Model | Primary Use Case |
| ---- | ------------ | ---------------- |
| Helm | Package manager (like npm/apt) | Third-party apps, distributable packages |
| Kustomize | Overlay system (like CSS) | Your apps, environment-specific patches |

### Decision Tree

```text
Will someone OUTSIDE your team deploy this app with their own configuration?
    │
    ├── YES → Use Helm
    │         • Open source projects
    │         • Vendor/platform software distributed to customers
    │         • Internal platform tools consumed by multiple teams
    │         • Apps with 10+ configurable options
    │
    └── NO → Use Kustomize
             • Your team's microservices (any scale)
             • Internal tools with fixed configuration
             • Apps where you control all deployments
             • Environment-specific patches (image tags, replicas, env vars)
```

### Specific Guidelines

#### Use Helm When

1. **Installing third-party software** (Grafana, Keycloak, Loki, Kong)
   - Upstream maintains the chart
   - You customize via `values.yaml`

2. **Building distributable platform tooling**
   - Other teams will `helm install` with their own values
   - Requires extensive configuration options
   - Needs versioned releases and upgrade paths

3. **Complex applications with many variants**
   - 10+ configurable parameters
   - Multiple deployment modes (standalone vs HA)
   - Optional components that can be enabled/disabled

#### Use Kustomize When

1. **Deploying your own microservices**
   - You own the manifests
   - Configuration is environment-specific (dev/staging/prod)
   - Scales to thousands of services (Netflix, Google pattern)

2. **Applying environment-specific patches**
   - Image tags
   - Replica counts
   - Environment variables
   - Resource limits

3. **Simple internal tools**
   - Fixed configuration
   - No external consumers
   - Straightforward deployment

### Combined Pattern (When Both Apply)

For platform apps that are **both distributed AND deployed internally**:

```text
gitops/helm/<app>/           ← Helm chart (for distribution)
  ├── Chart.yaml
  ├── values.yaml
  └── templates/

gitops/kustomize/overlays/   ← Kustomize (for env patches)
  ├── dev/
  ├── staging/
  └── prod/
```

Argo CD can use Helm with Kustomize post-rendering for this pattern.

---

## Scope

Applies to all application packaging decisions in this repository and any
applications scaffolded via Backstage templates.

---

## Consequences

### Positive

- Clear, actionable guidance for packaging decisions
- Consistent patterns across the platform
- Reduced confusion for new team members
- Aligns with industry best practices (CNCF patterns)

### Tradeoffs / Risks

- Two toolchains to maintain (unchanged from ADR-0020)
- Teams must understand both tools at a basic level
- Edge cases may require judgment calls

### Operational Impact

- Update Backstage templates to use Kustomize for scaffolded apps
- Document the decision tree in onboarding materials
- Review existing apps for alignment (non-breaking)

---

## Alternatives Considered

- **Helm-only:** Rejected. Values files become hard to audit for environment
  diffs. Templating overhead for simple apps.

- **Kustomize-only:** Rejected. Weaker packaging story for third-party apps.
  No native dependency management.

- **Jsonnet/CUE:** Rejected. Higher learning curve, less ecosystem support.

---

## Examples

### Example 1: hello-goldenpath-idp (Internal Microservice)

**Decision:** Kustomize

**Why:** Internal app, team owns all deployments, simple config (image tag, env vars).

```text
hello-goldenpath-idp/
└── deploy/
    ├── base/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── kustomization.yaml
    └── overlays/
        ├── local/
        ├── dev/
        └── prod/
```

### Example 2: Grafana Tempo (Third-Party)

**Decision:** Helm

**Why:** Upstream chart exists, complex configuration, we customize via values.

```text
gitops/helm/tempo/
└── values/
    ├── dev.yaml
    ├── staging.yaml
    └── prod.yaml
```

### Example 3: Platform RDS Provisioner (Internal Tool, Multi-Team)

**Decision:** Helm (if distributed) or Kustomize (if single deployment)

**Why:** If other teams need to deploy with different configs → Helm.
If only platform team deploys → Kustomize.

---

## Follow-ups

- [ ] Update Backstage app template to scaffold Kustomize structure
- [ ] Add decision tree to developer onboarding docs
- [ ] Review existing apps in `apps/` for alignment

---

## Notes

This decision does not mandate migration of existing apps. Teams should apply
this guidance to new applications and consider alignment during major refactors.

The decision tree is a guideline, not a strict rule. Use judgment for edge cases
and document exceptions in the app's README.
