---
id: ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
title: 'ADR-0178: Ephemeral vs Persistent DNS Ownership and Bootstrap Contract'
type: adr
status: proposed
domain: platform-core
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 40.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0175-externaldns-wildcard-ownership
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - 21_CI_ENVIRONMENT_CONTRACT
supersedes: []
superseded_by: []
tags:
  - dns
  - ephemeral
  - persistent
  - bootstrap
  - keycloak
  - v2
inheritance: {}
supported_until: 2028-01-23
version: '1.0'
breaking_change: true
---

# ADR-0178: Ephemeral vs Persistent DNS Ownership and Bootstrap Contract

- **Status:** Proposed (V2 Roadmap)
- **Date:** 2026-01-23
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Operations
- **Related:** ADR-0158 (Standalone RDS), ADR-0175 (ExternalDNS Ownership)
- **Implemented by:** ADR-0179 (Dynamic Hostname Generation)

---

## Context

V1 treats ephemeral and persistent clusters identically during bootstrap. This creates several collision risks:

1. **DNS collisions**: Multiple ephemeral clusters fight over the same hostnames (`backstage.dev.goldenpathidp.io`)
2. **Keycloak duplication**: Each cluster deploys Keycloak, but ephemeral clusters should share the persistent Keycloak
3. **Resource waste**: Ephemeral clusters deploy services they shouldn't own

### The Core Problem

DNS is a global namespace. Ephemeral clusters are non-global by nature. If ephemeral writes to the same DNS zone as persistent, collisions are inevitable, not edge cases.

```
Ephemeral Cluster A creates: backstage.dev.goldenpathidp.io → ALB-A
Ephemeral Cluster B creates: backstage.dev.goldenpathidp.io → ALB-B
                             └── COLLISION: Record flaps or overwrites
```

## Decision

We will establish a **DNS Ownership Contract** and **Bootstrap Mode Differentiation**:

### DNS Ownership Contract

| Cluster Type | Allowed DNS Namespace | Example |
|--------------|----------------------|---------|
| Persistent | `*.{env}.goldenpathidp.io` | `backstage.dev.goldenpathidp.io` |
| Ephemeral | `*.b-{buildid}.{env}.goldenpathidp.io` | `backstage.b-23-01-26-01.dev.goldenpathidp.io` |

**Rule:** Ephemeral clusters may NEVER create records in the base `*.{env}.goldenpathidp.io` namespace.

### Bootstrap Mode Differentiation

```yaml
bootstrap:
  mode: ephemeral | persistent
```

| Component | Persistent Mode | Ephemeral Mode |
|-----------|-----------------|----------------|
| Keycloak | Deploy (owns identity) | Skip (uses persistent Keycloak) |
| Backstage | Deploy | Deploy (with build-scoped DNS) |
| ArgoCD | Deploy | Deploy (with build-scoped DNS) |
| ExternalDNS | Manages `*.{env}.` | Manages `*.b-{buildid}.{env}.` only |
| RDS | Create (if standalone not exists) | Use standalone RDS |

### Shared Services Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENT SERVICES                          │
│                    (Standalone State)                           │
├─────────────────────────────────────────────────────────────────┤
│  Keycloak (keycloak.dev.goldenpathidp.io)                      │
│  RDS PostgreSQL (goldenpath-dev-platform-db)                   │
│  Route53 Zone (dev.goldenpathidp.io)                           │
└─────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │ Auth               │ Database           │ DNS parent
    ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
    │Persistent│          │Ephemeral│          │Ephemeral│
    │ Cluster  │          │Cluster A│          │Cluster B│
    └──────────┘          └──────────┘         └──────────┘
    backstage.dev.        backstage.b-01.      backstage.b-02.
    goldenpathidp.io      dev.goldenpathidp.io dev.goldenpathidp.io
```

## Implementation

### Phase 1: DNS Contract Enforcement

1. Add `hostSuffix` to Helm values generation:
   ```yaml
   # Computed based on lifecycle
   hostSuffix: "{{ if eq .lifecycle 'ephemeral' }}b-{{ .buildId }}.{{ end }}{{ .env }}.goldenpathidp.io"
   ```

2. Update all charts to use:
   ```yaml
   ingress:
     hostname: "backstage.{{ .Values.hostSuffix }}"
   ```

3. Add CI gate to block ephemeral manifests requesting base DNS

### Phase 2: Bootstrap Mode

1. Add `bootstrap.mode` to cluster configuration
2. Conditional app deployment in app-of-apps:
   ```yaml
   {{- if eq .Values.bootstrap.mode "persistent" }}
   - name: keycloak
   {{- end }}
   ```

3. Configure ephemeral Backstage to use persistent Keycloak:
   ```yaml
   keycloak:
     baseUrl: "https://keycloak.{{ .env }}.goldenpathidp.io"  # Always persistent
   ```

### Phase 3: ExternalDNS Scoping

1. Configure `--txt-owner-id={{ buildId }}` for ephemeral clusters
2. Configure `--domain-filter` to restrict ephemeral to build-scoped subdomains

## TLS Considerations

| Cluster Type | Certificate Scope |
|--------------|-------------------|
| Persistent | `*.dev.goldenpathidp.io` (wildcard) |
| Ephemeral | Per-build cert via cert-manager |

Alternative: Use `*.builds.dev.goldenpathidp.io` zone so ephemeral can use a single wildcard.

## Consequences

### Positive

- Zero DNS collisions between clusters
- Clear ownership boundaries
- Keycloak remains single source of truth for identity
- Ephemeral clusters are truly disposable
- Cleanup is straightforward (delete build-scoped records)

### Tradeoffs

- More complex Helm values generation
- Ephemeral clusters cannot test Keycloak changes (acceptable tradeoff)
- Requires Keycloak wildcard redirect URIs

### Migration

- V1 clusters continue as-is (single cluster per environment)
- V2 introduces the contract when multi-cluster ephemeral is needed

## Alternatives Considered

1. **Separate hosted zones per cluster type**: Cleaner but adds zone management complexity
2. **ExternalDNS txt-owner-id only**: Prevents overwrites but doesn't solve naming collisions
3. **Disable DNS for ephemeral**: Simpler but reduces usability

## Roadmap

- **V1.1**: Document contract, add CI gate for hostname validation
- **V2.0**: Implement bootstrap mode differentiation
- **V2.1**: Full ExternalDNS scoping with txt-owner-id

## References

- ADR-0158: Standalone RDS as Bounded Context
- ADR-0175: ExternalDNS Wildcard Ownership
- ADR-0179: Dynamic Hostname Generation (implements this contract)
- DNS Ownership Contract discussion (2026-01-23)
