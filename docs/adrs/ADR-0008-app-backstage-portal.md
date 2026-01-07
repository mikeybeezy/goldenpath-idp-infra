---
id: ADR-0008-app-backstage-portal
title: 'ADR-0008: Use Backstage as the developer portal and the V1 demo application
  for env promotion'
type: adr
status: active
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0008
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0008: Use Backstage as the developer portal and the V1 demo application for env promotion

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Application
- **Decision type:** Architecture | UX | Product
- **Related:** docs/10-governance/01_GOVERNANCE.md, docs/00-foundations/18_BACKSTAGE_MVP.md

## Context

We want the IDP to feel like a product, not just installed tooling. We also
need a credible demonstration that:

- CI builds an application image
- GitOps promotes it through environments
- ingress + secrets + observability work end-to-end

Backstage is both:

- a developer portal (long-term platform surface)
- a real application that exercises the whole delivery chain

## Decision

Deploy **Backstage** as the developer portal via GitOps and use it as the **V1
demo application** to prove promotion across dev/test/stage/prod.

Backstage will be packaged as a container image built via CI (Yarn build →
Docker image) and deployed to Kubernetes using GitOps-managed manifests/Helm
values.

Initial Backstage customization will be minimal; deeper UX/plugin enhancements
are deferred until the promotion loop is stable.

## Scope

- Applies to: V1 portal deployment and promotion demo.
- Out of scope (V1):
  - extensive custom plugin development
  - complex catalog modelling across many domains
  - “actions” automation (write operations) beyond PR-based workflows

## Consequences

### Positive

- Strong, visible proof of platform capability (promotion, ingress, secrets,

  rollback).

- Portal becomes a natural home for Golden Path docs, runbooks, and later

  templates.

- Improves portfolio narrative and product credibility.

### Tradeoffs / Risks

- Backstage adds operational surface area (Node app lifecycle, config,

  dependencies).

- Without discipline, Backstage work can become a distraction (UX rabbit hole).
- Requires careful config/secrets separation per environment.

### Operational impact

- Backstage deployment must follow platform principles:
  - config via ConfigMap per env
  - secrets via External Secrets (AWS as system of record)
  - ingress via Kong (internal NLB posture)
  - logs routed to platform sink
- CI must:
  - build and push Backstage image
  - open PRs to bump image tag in env values
  - promote tags dev → test → stage → prod via PR workflow
- SSO integration with Keycloak is planned but not required for initial

  bootstrap.

## Alternatives considered

- **Hello-world sample app**: rejected as insufficient proof and too contrived.
- **Backstage later**: rejected because it is a strong “demo app” and should be

  installed early (even if minimally configured).

- **Use a managed portal**: rejected due to desire for portability and

  customization.

## Follow-ups

- Create a minimal Backstage app repo (or folder) and a production-grade Docker

  build.

- Add Backstage Helm values/manifests for each environment.
- Define and implement the promotion workflow (PR-based tag bumps).
- Add smoke tests: health endpoint + Argo health + ingress reachability.
