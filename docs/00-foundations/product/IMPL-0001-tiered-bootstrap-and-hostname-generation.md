---
id: IMPL-0001-tiered-bootstrap-and-hostname-generation
title: 'Work Order: Tiered Bootstrap and Dynamic Hostname Generation'
type: work-order
status: proposed
relates_to:
  - ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - ADR-0180-argocd-orchestrator-contract
---

# Work Order: Tiered Bootstrap and Dynamic Hostname Generation

**Implements:** ADR-0178, ADR-0179, ADR-0180

---

## Foundation Philosophy

> **Tier-scoped foundation, not blanket gate.**

Persistent clusters are foundational, but not every foundational dependency is required for every tier. The foundation is tier-scoped so lower tiers don't inherit higher-tier dependencies.

---

## Phase 0a: Core Foundation (All Tiers)

**Goal:** Foundational plane infrastructure required for all deployments.
**Depends on:** ADR-0177 (CI IAM permissions)

| Pass | Fail |
|------|------|
| VPC exists with expected subnets | VPC not found |
| Route53 zone `{env}.goldenpathidp.io` exists | Zone not found |
| IRSA OIDC provider configured | OIDC not found |

---

## Phase 0b: Tier 2/3 Prerequisites (Conditional)

**Goal:** Stateful infrastructure for Tier 2+ deployments.
**Depends on:** Phase 0a
**Required when:** `maxTier >= 2` or TLS in scope

| Pass | Fail |
|------|------|
| RDS endpoint reachable from dev VPC | Connection refused |
| Secrets Manager contains `goldenpath/dev/backstage/postgres` | Secret not found |
| ClusterIssuers deployed and Ready | Missing or NotReady |

---

## Phase 1: Helm Values Standardization

**Goal:** All charts use `global.hostSuffix` for hostname generation.
**Depends on:** None

| Pass | Fail |
|------|------|
| `helm template backstage --set global.hostSuffix=test.example.com` produces correct hostname | Hardcoded hostname in output |
| No hardcoded hostnames in any chart | grep finds `goldenpathidp.io` in templates |

---

## Phase 2: Terraform BuildId Propagation

**Goal:** Terraform computes `hostSuffix` from `lifecycle` + `build_id`.
**Depends on:** Phase 1

| Pass | Fail |
|------|------|
| `terraform plan -var="lifecycle=ephemeral" -var="build_id=test-01"` succeeds | Plan fails |
| `terraform plan -var="lifecycle=ephemeral"` (no build_id) fails validation | Plan succeeds without build_id |
| Output `helm_global_values` contains correct `hostSuffix` | Missing or wrong suffix |

---

## Phase 3: CI Workflow Updates

**Goal:** CI passes `lifecycle` and `build_id` to Terraform.
**Depends on:** Phase 2

| Pass | Fail |
|------|------|
| Ephemeral run without `build_id` fails at validation step | Proceeds without build_id |
| Ephemeral run with `build_id` passes values to Terraform | Values not propagated |
| Persistent run ignores `build_id` | Requires build_id |

---

## Phase 4: ArgoCD Bootstrap ConfigMap

**Goal:** Terraform creates ConfigMap with bootstrap values for ArgoCD.
**Depends on:** Phase 3

| Pass | Fail |
|------|------|
| `kubectl get cm argocd-bootstrap-config -n argocd` exists | Not found |
| ConfigMap contains bootstrap/platform/dns values | Missing keys |
| App-of-apps can read values | Template errors |

---

## Phase 5: App-of-Apps Tier Selection

**Goal:** ArgoCD deploys apps based on `maxTier`.
**Depends on:** Phase 4

| Pass | Fail |
|------|------|
| `helm template app-of-apps --set bootstrap.maxTier=1.5` excludes Tier 2+ | Backstage rendered |
| `helm template app-of-apps --set bootstrap.mode=ephemeral` excludes Keycloak | Keycloak rendered |
| All apps have `goldenpath.idp/tier` label | Missing labels |

---

## Phase 6: ExternalDNS Scoping

**Goal:** ExternalDNS only manages build-scoped records for ephemeral.
**Depends on:** Phase 5

| Pass | Fail |
|------|------|
| Ephemeral: `--domain-filter=b-{buildId}.{env}.goldenpathidp.io` | Filters base zone |
| Persistent: `--domain-filter={env}.goldenpathidp.io` | Filters build zone |
| `--txt-owner-id` matches `dnsOwnerId` | Mismatched owner |

---

## Phase 7a: V1 Preflight Validation (CI/Terraform)

**Goal:** Fail early in CI if tier prerequisites are missing.
**Depends on:** Phase 5

| Pass | Fail |
|------|------|
| CI checks RDS exists before persistent Tier 2+ deploy | Deploy proceeds without RDS |
| Terraform data source validates prerequisites | Silent failure at runtime |
| Failure message indicates which prerequisite is missing | Generic error |

**Implementation:**

```yaml
# CI workflow preflight
- name: Preflight Check
  run: |
    if [[ "${{ inputs.lifecycle }}" == "persistent" ]]; then
      aws rds describe-db-instances \
        --db-instance-identifier goldenpath-${{ inputs.environment }} \
        || { echo "RDS not found - deploy RDS first"; exit 1; }
    fi
```

---

## Phase 7b: V2 Preflight Check Jobs (ArgoCD PreSync)

**Goal:** ArgoCD PreSync hooks validate prerequisites with UI visibility.
**Depends on:** Phase 7a stable, operators familiar with ArgoCD troubleshooting

| Pass | Fail |
|------|------|
| RDS unreachable → Backstage sync blocked | Backstage deploys anyway |
| Secrets missing → ESO sync blocked | App crashes on missing secret |
| Preflight job failure visible in ArgoCD UI | Silent failure |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Ephemeral deploy (Tier 0-1.5) | < 10 min |
| DNS collisions | 0 |
| Tier selection accuracy | 100% |

---

**Details:** See ADR-0178, ADR-0179, ADR-0180 for implementation specifics.
