<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0175-externaldns-wildcard-ownership
title: 'ADR-0175: ExternalDNS owns wildcard records for env subdomains'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0170-route53-terraform-module
  - PRD-0002-route53-externaldns
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - dns
  - route53
  - external-dns
  - kong
  - gitops
inheritance: {}
supported_until: 2028-01-21
date: 2026-01-21
deciders:
  - platform-team
---

## Status

Accepted

## Context

The wildcard DNS record for `*.{env}.goldenpathidp.io` is tied to the Kong
LoadBalancer hostname. Terraform can set this value during apply, but when the
LoadBalancer changes (teardown/rebuild), DNS drifts unless Terraform is re-run.
We also need a single, authoritative owner for wildcard records to avoid
Terraform and ExternalDNS racing on the same record.

## Decision

ExternalDNS is the owner of wildcard DNS records per environment:

- `*.dev.goldenpathidp.io`
- `*.test.goldenpathidp.io`
- `*.staging.goldenpathidp.io`
- `*.prod.goldenpathidp.io`

Implementation details:

1. ExternalDNS is deployed via Argo CD using the upstream chart.
2. A dedicated IRSA role is created per environment, scoped to the Route53
   hosted zone ID.
3. The Kong proxy Service is annotated with
   `external-dns.alpha.kubernetes.io/hostname` for the wildcard.
4. Terraform no longer creates wildcard records
   (`create_wildcard_record = false` by default).

## Consequences

- ExternalDNS becomes the source of truth for wildcard records.
- Terraform remains the source of truth for the hosted zone and any static
  records not managed by ExternalDNS.
- Bootstrap must include ExternalDNS (or enable it immediately after) so DNS
  stays in sync with LoadBalancer changes.
- Teardown should disable ExternalDNS or allow it to delete managed records
  before cluster removal.

## Alternatives Considered

1. **Terraform-managed wildcard only**: requires manual re-apply on each
   LoadBalancer change and risks stale records.
2. **Manual DNS management**: error-prone and not reproducible.
