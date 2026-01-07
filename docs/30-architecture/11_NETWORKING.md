---
id: 11_NETWORKING
title: Networking Decisions
type: adr
status: active
domain: platform-core
applies_to:
  - infra
owner: platform-team
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle: active
category: architecture
version: '1.0'
dependencies: []
relates_to:
  - 08_INGRESS_STRATEGY
supported_until: 2028-01-01
breaking_change: false
---

# Networking Decisions

This document captures the networking decisions for the platform and the
reasoning behind them. It is a living document and will grow over time.

See also: `docs/30-architecture/08_INGRESS_STRATEGY.md` for ingress front door decisions.

## Desired outcomes

- Fast developer feedback in dev.
- Stronger isolation and access control in higher environments.
- A single, predictable ingress path for external traffic.
- Clear separation between platform tooling access and client application access.

## Environment exposure model

## Dev

- Public-facing ingress is acceptable to unblock iteration.
- Expect minimal friction for engineers validating changes.

## Staging/Prod

- Ingress is private/internal by default.
- Access is limited to approved entry points (VPN, bastion, or SSM forward).

## Future

- As the platform matures, all environments move to internal-facing ingress.

## Kong exposure control (annotations)

Kong is exposed via a Kubernetes `Service` of type `LoadBalancer`. We control
public vs internal exposure via AWS Load Balancer annotations in the Kong
values files (per environment).

Example annotations:

```text

service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
service.beta.kubernetes.io/aws-load-balancer-scheme: "internal"

```text

When we need public access in dev, we omit the `internal` scheme annotation.
When we need internal-only access in staging/prod, we enable it.

## Why this is enforced in higher environments

- Reduced external attack surface.
- Stronger audit and access controls.
- More predictable, compliant change management.
- Fewer emergency changes late in the release cycle.

## VPN choice (starting point)

Decision: Start with Pritunl (self-hosted) for cost-effective access control.
Offer an upgrade path to Pritunl Enterprise or AWS Client VPN for managed
operations and support.

### Option A: Pritunl (self-hosted)

Pros:

- Lowest cost at small scale.
- Fast to deploy and flexible.
- Works well with AWS VPC routing.

Cons:

- You own patching, uptime, and monitoring.
- HA and disaster recovery require extra work.
- Security posture depends on ops maturity.

### Option B: Pritunl Enterprise (managed)

Pros:

- Reduced ops burden.
- Enterprise features and support.
- Straightforward migration from OSS.

Cons:

- Recurring cost.
- Vendor dependency.
- Less cloud-native than AWS Client VPN.

### Option C: AWS Client VPN (managed)

Pros:

- Fully managed with tight AWS integration.
- Easier audits and compliance controls.
- Scales cleanly with multi-account AWS orgs.

Cons:

- Higher recurring cost.
- Less customization.
- Pricing scales with active connections.

### Blind spots to watch

- Access frequency vs pricing (AWS may still be fine for intermittent use).
- HA expectations during incidents.
- Identity integration and off-boarding.
- Audit log retention and SIEM integration.
- Multi-account and multi-region access patterns.
