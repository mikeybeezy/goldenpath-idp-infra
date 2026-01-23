---
id: ADR-0179-dynamic-hostname-generation-ephemeral-clusters
title: 'ADR-0179: Dynamic Hostname Generation for Ephemeral Clusters'
type: adr
status: proposed
domain: platform-core
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 20.0
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
  - ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
  - ADR-0175-externaldns-wildcard-ownership
  - 21_CI_ENVIRONMENT_CONTRACT
supersedes: []
superseded_by: []
tags:
  - dns
  - ephemeral
  - hostname
  - buildid
  - v2
inheritance: {}
supported_until: 2028-01-23
version: '1.0'
breaking_change: false
---

# ADR-0179: Dynamic Hostname Generation for Ephemeral Clusters

- **Status:** Proposed (V2 Roadmap)
- **Date:** 2026-01-23
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Implementation
- **Implements:** ADR-0178 (DNS Ownership Contract)

---

## Context

ADR-0178 establishes that ephemeral clusters must use the `*.b-{buildid}.{env}.goldenpathidp.io` namespace to prevent DNS collisions. This ADR defines **how** the `buildId` flows through the system to generate unique hostnames.

### The Challenge

The `buildId` originates in CI workflows but must propagate to:
1. Terraform variables
2. Helm values
3. Ingress manifests
4. ExternalDNS ownership tags

Without a clear mechanism, each component might implement hostname generation differently, leading to inconsistency and potential namespace violations.

## Decision

We will implement a **BuildId Propagation Chain** with validation gates at each stage.

### BuildId Propagation Chain

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   CI Workflow    │───▶│  Terraform Vars  │───▶│   Helm Values    │
│   build_id=X     │    │  build_id = "X"  │    │  hostSuffix: ... │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                        ┌───────────────────────────────┘
                        ▼
              ┌──────────────────┐    ┌──────────────────┐
              │  Ingress Host    │───▶│   ExternalDNS    │
              │  backstage.b-X.. │    │  Creates record  │
              └──────────────────┘    └──────────────────┘
```

### Stage 1: CI Workflow Input

```yaml
# .github/workflows/infra-terraform-apply-*.yml
workflow_dispatch:
  inputs:
    build_id:
      description: "Build identifier (e.g., 23-01-26-01)"
      required: true
    lifecycle:
      description: "Cluster lifecycle"
      type: choice
      options: [ephemeral, persistent]
```

**Validation:** CI rejects ephemeral runs without a `build_id`.

### Stage 2: Terraform Variables

```hcl
# envs/dev/variables.tf
variable "build_id" {
  type        = string
  description = "Unique build identifier for ephemeral clusters"
  default     = ""  # Empty string for persistent clusters
}

variable "lifecycle" {
  type        = string
  description = "Cluster lifecycle: ephemeral or persistent"
  default     = "persistent"
}

locals {
  # Computed host suffix based on lifecycle
  host_suffix = var.lifecycle == "ephemeral" ? "b-${var.build_id}.${var.env}.goldenpathidp.io" : "${var.env}.goldenpathidp.io"

  # ExternalDNS ownership ID
  dns_owner_id = var.lifecycle == "ephemeral" ? "ephemeral-${var.build_id}" : "persistent-${var.env}"
}
```

**Output:** Terraform passes `host_suffix` and `dns_owner_id` to Helm values generation.

### Stage 3: Helm Values Generation

```yaml
# Generated values for ephemeral cluster
global:
  lifecycle: ephemeral
  buildId: "23-01-26-01"
  hostSuffix: "b-23-01-26-01.dev.goldenpathidp.io"
  dnsOwnerId: "ephemeral-23-01-26-01"

# Generated values for persistent cluster
global:
  lifecycle: persistent
  buildId: ""
  hostSuffix: "dev.goldenpathidp.io"
  dnsOwnerId: "persistent-dev"
```

### Stage 4: Chart Templates

All charts MUST use the `hostSuffix` variable for hostname generation:

```yaml
# backstage/templates/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backstage
spec:
  rules:
    - host: "backstage.{{ .Values.global.hostSuffix }}"
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: backstage
                port:
                  number: 7007

# argocd/templates/ingress.yaml
spec:
  rules:
    - host: "argocd.{{ .Values.global.hostSuffix }}"

# keycloak/templates/ingress.yaml (persistent only)
spec:
  rules:
    - host: "keycloak.{{ .Values.global.hostSuffix }}"
```

**Rule:** No chart may hardcode a hostname. All must reference `.Values.global.hostSuffix`.

### Stage 5: ExternalDNS Configuration

```yaml
# externaldns/values-ephemeral.yaml
args:
  - --source=ingress
  - --provider=aws
  - --txt-owner-id={{ .Values.global.dnsOwnerId }}
  - --domain-filter=b-{{ .Values.global.buildId }}.{{ .Values.env }}.goldenpathidp.io

# externaldns/values-persistent.yaml
args:
  - --source=ingress
  - --provider=aws
  - --txt-owner-id={{ .Values.global.dnsOwnerId }}
  - --domain-filter={{ .Values.env }}.goldenpathidp.io
```

## Validation Gates

### CI Gate: Hostname Validation

```bash
#!/bin/bash
# .github/scripts/validate-ephemeral-hostnames.sh

LIFECYCLE="${1}"
BUILD_ID="${2}"

if [[ "$LIFECYCLE" == "ephemeral" ]]; then
  echo "Validating ephemeral hostnames contain build prefix..."

  # Find all rendered ingress hostnames
  HOSTS=$(grep -rh "host:" gitops/rendered/ | grep -oP 'host:\s*"\K[^"]+')

  for host in $HOSTS; do
    # Skip if it's the persistent Keycloak reference
    if [[ "$host" == keycloak.*.goldenpathidp.io ]] && [[ "$host" != *"b-"* ]]; then
      echo "ALLOWED: $host (persistent Keycloak reference)"
      continue
    fi

    # All other hosts must contain build prefix
    if [[ "$host" != *"b-${BUILD_ID}"* ]]; then
      echo "ERROR: Ephemeral cluster cannot use base namespace: $host"
      exit 1
    fi
  done

  echo "All hostnames validated successfully"
fi
```

### Terraform Gate: Lifecycle/BuildId Consistency

```hcl
# modules/platform/validation.tf
resource "null_resource" "validate_ephemeral_build_id" {
  count = var.lifecycle == "ephemeral" && var.build_id == "" ? 1 : 0

  provisioner "local-exec" {
    command = "echo 'ERROR: Ephemeral clusters require a build_id' && exit 1"
  }
}
```

### Helm Gate: hostSuffix Required

```yaml
# charts/backstage/templates/_helpers.tpl
{{- define "backstage.hostname" -}}
{{- if not .Values.global.hostSuffix -}}
{{- fail "global.hostSuffix is required" -}}
{{- end -}}
backstage.{{ .Values.global.hostSuffix }}
{{- end -}}
```

## Cleanup Strategy

When tearing down an ephemeral cluster:

```bash
# Delete all DNS records owned by this build
aws route53 list-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --query "ResourceRecordSets[?contains(Name, 'b-${BUILD_ID}')]" \
  | jq -r '.[].Name'

# ExternalDNS TXT records automatically cleaned by owner-id matching
```

## Migration Path

| Phase | Action |
|-------|--------|
| V1.1 | Add `global.hostSuffix` to all charts with default value |
| V1.2 | Update CI to pass `build_id` for ephemeral runs |
| V2.0 | Enable validation gates, enforce namespace separation |

## Consequences

### Positive

- Single source of truth for hostname generation
- BuildId propagates consistently through all layers
- Validation gates catch namespace violations before deployment
- Cleanup is deterministic (match on `b-{buildid}`)

### Tradeoffs

- All charts must be updated to use `hostSuffix`
- CI workflows require `build_id` parameter for ephemeral
- Additional validation steps in pipeline

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Chart forgets hostSuffix | Helm lint + CI validation gate |
| BuildId not passed | Terraform validation fails |
| Typo in buildId | Standardize format: `YY-MM-DD-NN` |

## Testing Strategy

```bash
# Test ephemeral hostname generation
helm template backstage ./charts/backstage \
  --set global.lifecycle=ephemeral \
  --set global.buildId=test-01 \
  --set global.hostSuffix=b-test-01.dev.goldenpathidp.io \
  | grep "host:" | grep -q "b-test-01"

# Test persistent hostname generation
helm template backstage ./charts/backstage \
  --set global.lifecycle=persistent \
  --set global.hostSuffix=dev.goldenpathidp.io \
  | grep "host:" | grep -qv "b-"
```

## References

- ADR-0178: Ephemeral vs Persistent DNS Ownership Contract (defines the "what")
- ADR-0175: ExternalDNS Wildcard Ownership
- 21_CI_ENVIRONMENT_CONTRACT: CI variable standards
