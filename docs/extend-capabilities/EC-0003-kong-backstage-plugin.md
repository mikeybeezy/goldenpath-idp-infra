---
id: EC-0003-kong-backstage-plugin
title: Kong Self-Service Backstage Plugin
type: extension-capability
status: proposed
relates_to:
  - ADR-0002-platform-Kong-as-ingress-API-gateway
  - ADR-0162
  - INDEX
  - RB-0035-s3-request
  - ROADMAP
  - SECRET_REQUEST_FLOW
  - agent_session_summary
dependencies:
  - Kong Ingress Controller (existing)
  - Backstage (existing)
  - ArgoCD (existing)
priority: high
vq_class: 🔴 HV/HQ
estimated_roi: $110K/year (license avoidance + productivity + toil reduction)
effort_estimate: 4 weeks
owner: platform-team
---
## Executive Summary

Enable teams to self-service Kong ingress configuration through Backstage, following the established contract-driven pattern. This removes the platform team as a bottleneck for:

- **Ingress Configuration**: Teams request routes for their services via PR
- **Plugin Management**: Rate limiting, auth, CORS via governed templates
- **Traffic Policies**: Blue/green, canary via declarative config

**Estimated ROI**: $110K/year from Kong Enterprise license avoidance ($50K), developer productivity gains ($45K), reduced platform team toil ($7K), and incident response improvements ($3.6K).

**Strategic Fit**: 5/5 - Direct extension of existing patterns (EKS, RDS, Secret requests).

## Problem Statement

Currently, teams needing Kong ingress configuration must:

1. **Ask Platform Team**: Create ticket, wait for response
2. **Manual YAML**: Write KongIngress/KongPlugin manifests without validation
3. **No Discoverability**: Can't see what Kong resources exist for their services
4. **Config Drift**: Manual changes not tracked in GitOps

This creates:
- Platform team bottleneck (~2 hours/week on Kong requests)
- Inconsistent configurations across teams
- No audit trail for ingress changes

## Proposed Solution

### Contract-Driven Kong Requests

Follow the established pattern:

```yaml
# docs/20-contracts/kong-requests/payments/dev/KONG-0001.yaml
apiVersion: goldenpath.io/v1
kind: KongIngressRequest
id: KONG-0001
metadata:
  owner: payments-team
  environment: dev
  service: payments-api
  namespace: payments
spec:
  host: api.goldenpath.dev
  path: /api/v1/payments
  service_port: 8080
  plugins:
    - type: rate-limiting
      config:
        minute: 100
        policy: local
    - type: key-auth
      config:
        key_names: [apikey]
        hide_credentials: true
    - type: cors
      config:
        origins: ["https://app.goldenpath.dev"]
        methods: ["GET", "POST"]
```

### Backstage Software Template

```yaml
# backstage-helm/backstage-catalog/templates/kong-request.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: kong-ingress-request
  title: Request Kong Ingress
  description: Request ingress and plugins for your service
spec:
  type: request
  parameters:
    - title: Service Details
      properties:
        service_name:
          type: string
          description: Name of your service (must exist in cluster)
        namespace:
          type: string
          enum: [payments, orders, inventory, platform]
        environment:
          type: string
          enum: [dev, staging, prod]
    - title: Ingress Configuration
      properties:
        host:
          type: string
          default: api.goldenpath.dev
        path:
          type: string
          description: URL path prefix (e.g., /api/v1/payments)
    - title: Plugins
      properties:
        enable_rate_limiting:
          type: boolean
          default: true
        rate_limit_per_minute:
          type: integer
          default: 100
        enable_auth:
          type: boolean
          default: false
        auth_type:
          type: string
          enum: [key-auth, jwt, oidc]
```

### Request Flow

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Backstage: Team fills out "Request Kong Ingress" form    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PR Created: docs/20-contracts/kong-requests/KONG-XXXX.yaml│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CI Validation: kong_request_parser.py --mode validate    │
│    - Schema validation                                       │
│    - Service exists check                                    │
│    - Plugin config validation                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Platform Review + Merge                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. CI Apply: kong_request_parser.py --mode generate         │
│    - Generates KongIngress, KongPlugin, KongConsumer CRDs   │
│    - Outputs to gitops/kustomize/overlays/<env>/apps/<app>/ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. ArgoCD Sync: Kong Ingress Controller picks up new config │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Integration

### Files to Create

| File | Purpose |
|------|---------|
| `schemas/requests/kong.schema.yaml` | JSON Schema for request validation |
| `scripts/kong_request_parser.py` | Parser script (SCRIPT-0036) |
| `backstage-helm/backstage-catalog/templates/kong-request.yaml` | Backstage template |
| `backstage-helm/backstage-catalog/templates/skeletons/kong-request/` | Skeleton files |
| `.github/workflows/ci-kong-request-validation.yml` | CI validation |
| `.github/workflows/kong-request-apply.yml` | Apply workflow |
| `docs/85-how-it-works/self-service/KONG_REQUEST_FLOW.md` | Documentation |

### Generated Output Example

```yaml
# gitops/kustomize/overlays/dev/apps/payments/kong/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: payments-api
  namespace: payments
  annotations:
    konghq.com/plugins: payments-api-rate-limit,payments-api-key-auth
    konghq.com/strip-path: "true"
    goldenpath.io/id: KONG-0001
    goldenpath.io/owner: payments-team
spec:
  ingressClassName: kong
  rules:
    - host: api.goldenpath.dev
      http:
        paths:
          - path: /api/v1/payments
            pathType: Prefix
            backend:
              service:
                name: payments-api
                port:
                  number: 8080
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: payments-api-rate-limit
  namespace: payments
  annotations:
    goldenpath.io/id: KONG-0001
plugin: rate-limiting
config:
  minute: 100
  policy: local
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: payments-api-key-auth
  namespace: payments
  annotations:
    goldenpath.io/id: KONG-0001
plugin: key-auth
config:
  key_names:
    - apikey
  hide_credentials: true
```

## Strategic Use Cases

### Use Case 1: Team Requests Ingress for New Service

**Before**: Team opens ticket, waits 1-2 days for platform team.
**After**: Team fills Backstage form, PR auto-created, merged same day.

**Value**: Reduced lead time from 2 days to 2 hours.

### Use Case 2: Add Rate Limiting to Existing Service

**Before**: Team asks platform team to add plugin, may get wrong config.
**After**: Team modifies their KONG-XXXX.yaml, submits PR, validated automatically.

**Value**: Self-service with guardrails.

### Use Case 3: Audit Kong Configuration

**Before**: Run `kubectl get kongplugins -A`, no ownership info.
**After**: All Kong resources tagged with `goldenpath.io/id` and `goldenpath.io/owner`.

**Value**: Complete audit trail via contract files.

## Implementation Roadmap

### Phase 1: Schema + Parser (Week 1)

- [ ] Create `schemas/requests/kong.schema.yaml`
- [ ] Implement `scripts/kong_request_parser.py` (SCRIPT-0036)
- [ ] Add to enums.yaml: kong plugin types
- [ ] Unit tests for parser

**Deliverables**:
- Schema validates KONG-XXXX.yaml files
- Parser generates valid Kong CRDs
- `make kong-request-validate` target

### Phase 2: Backstage Template (Week 2)

- [ ] Create `kong-request.yaml` template
- [ ] Create skeleton directory
- [ ] Test PR creation flow
- [ ] Add to Backstage catalog

**Deliverables**:
- Teams can fill form in Backstage
- PR created with valid KONG-XXXX.yaml

### Phase 3: CI Workflows (Week 3)

- [ ] `ci-kong-request-validation.yml` for PR checks
- [ ] `kong-request-apply.yml` for post-merge
- [ ] Integration with governance-registry

**Deliverables**:
- Automated validation on PR
- Automated apply on merge

### Phase 4: Documentation + Rollout (Week 4)

- [ ] `KONG_REQUEST_FLOW.md` documentation
- [ ] Runbook for troubleshooting
- [ ] Migrate existing ad-hoc Kong configs to contracts
- [ ] Announce to teams

**Deliverables**:
- Complete documentation
- Sample requests for each team

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Invalid Config Breaks Ingress** | High | Schema validation + dry-run mode |
| **Teams Request Conflicting Paths** | Medium | Parser checks for path conflicts |
| **Plugin Misconfiguration** | Medium | Preset configs for common use cases |
| **Adoption Resistance** | Low | Make it easier than manual YAML |

## Supported Kong Plugins (Phase 1)

| Plugin | Self-Service | Requires Approval |
|--------|--------------|-------------------|
| `rate-limiting` | Yes | No |
| `cors` | Yes | No |
| `key-auth` | Yes | No |
| `request-transformer` | Yes | No |
| `jwt` | Yes | Platform review |
| `oidc` | No | Platform only |
| `ip-restriction` | No | Platform only |

## Cost Analysis

### Current State (Direct Costs Only)

- Platform team: ~2 hours/week on Kong requests
- Engineer cost: ~$80/hour
- Annual cost: 2 x 52 x $80 = **$8,320/year**

### With Self-Service

- Platform team: ~15 min/week (reviews only)
- Annual cost: 0.25 x 52 x $80 = **$1,040/year**

**Direct Savings**: $8,320 - $1,040 = **$7,280/year**

### Implementation Cost

- 4 weeks engineering: ~$12,800
- Payback period (direct savings only): ~21 months

---

### Revised Total Cost of Ownership Analysis

The $8K/year figure above captures only direct platform team toil. A complete analysis must include:

#### 1. Kong Enterprise License Avoidance

| Feature | Kong Enterprise | Golden Path IDP (OSS) |
|---------|----------------|----------------------|
| Service Catalog / Service Hub | Included ($30-50K/year value) | Backstage (free) |
| Developer Portal | Included ($20-30K/year value) | Backstage Templates (free) |
| API Documentation | Included | Backstage TechDocs (free) |
| Self-Service Registration | Included | This EC-0003 plugin (4 weeks effort) |

**Kong Enterprise pricing**: $50-150K/year depending on scale and support tier.

By building Kong + Backstage integration, we avoid the need to upgrade to Kong Enterprise for service catalog capabilities.

**License Avoidance Value**: **$50,000-100,000/year** (conservative: $50K)

#### 2. Developer Productivity Gains

| Metric | Before | After | Value |
|--------|--------|-------|-------|
| Ingress request lead time | 2 days | 2 hours | Faster feature delivery |
| Developer wait time | 10 devs × 4 hrs/month × $75/hr | Eliminated | **$36,000/year** |
| Context switching (tickets) | 10 devs × 1 hr/month × $75/hr | Eliminated | **$9,000/year** |

#### 3. Incident Response Improvements

| Scenario | Without Integration | With Integration |
|----------|--------------------|--------------------|
| "Which team owns this API?" | Manual investigation (~30 min) | Backstage lookup (~2 min) |
| "What rate limits are configured?" | kubectl + grep (~15 min) | Backstage catalog (~1 min) |
| "Who changed this ingress?" | git blame + cross-reference (~20 min) | KONG-XXXX audit trail (~2 min) |

Assuming 2 incidents/month requiring this information:
**MTTR Reduction Value**: 2 × 12 × 1 hr × $150/hr (incident rate) = **$3,600/year**

#### 4. Compliance & Audit Benefits

- Complete audit trail for all API gateway changes
- Automated policy enforcement (rate limits, auth requirements)
- Evidence for SOC2/ISO27001 controls

**Compliance Value**: Hard to quantify, but reduces audit prep time by ~$5,000/year

---

### Revised ROI Summary

| Category | Annual Value |
|----------|-------------|
| Direct platform team savings | $7,280 |
| Kong Enterprise license avoidance | $50,000 |
| Developer productivity gains | $45,000 |
| Incident response improvements | $3,600 |
| Compliance/audit benefits | $5,000 |
| **Total Annual Value** | **$110,880** |

### Revised Implementation ROI

- Implementation cost: $12,800 (4 weeks)
- Annual value: $110,880
- **Payback period: < 2 months**
- **3-year ROI: 2,500%+**

> **Note**: Even using conservative estimates (Kong Enterprise at $50K, lower dev productivity gains), the ROI exceeds **$60,000/year** - significantly higher than the original $8K estimate which only captured direct toil reduction.

## Monitoring & Success Metrics

### Technical Metrics

- **PR to Production**: <4 hours (vs 2 days today)
- **Validation Pass Rate**: >95% on first submission
- **Kong Config Errors**: <1/month (vs ~2/month today)

### Business Metrics

- **Platform Team Toil**: <30 min/week on Kong requests
- **Team Adoption**: 100% of new ingress via self-service by Q3

## Alternatives Considered

### Option 1: Kong Manager UI Access

**Pros**: Teams configure directly in UI
**Cons**:
- No GitOps audit trail
- No validation before apply
- Risk of conflicting changes

**Decision**: Rejected - Breaks governance model

### Option 2: Direct Kubectl Access

**Pros**: Teams create Kong CRDs directly
**Cons**:
- Requires K8s expertise
- No schema validation
- No standardization

**Decision**: Rejected - Too error-prone

### Option 3: Status Quo (Platform Team Handles)

**Pros**: Full control
**Cons**:
- Bottleneck
- Toil for platform team

**Decision**: Rejected - Doesn't scale

## Open Questions

1. **Should we support custom plugins?**
   - Recommendation: No in Phase 1, evaluate for Phase 2

2. **How to handle prod vs non-prod approval?**
   - Recommendation: Prod requires CODEOWNERS approval

3. **Migrate existing Kong configs?**
   - Recommendation: Yes, create KONG-XXXX for each existing ingress

## Governance Compliance

### Born Governed Checklist

- [ ] Schema-driven provisioning (`kong.schema.yaml`)
- [ ] Metadata header for scripts (SCRIPT-0036)
- [ ] ADR documentation (ADR after accepted)
- [ ] Changelog entry (CL-XXXX)
- [ ] Runbook creation (RB-0035)
- [ ] ArgoCD GitOps workflow
- [ ] Audit trail (KONG-XXXX IDs)

## References

- [ADR-0002: Kong as Ingress Gateway](../adrs/ADR-0002-platform-Kong-as-ingress-API-gateway.md)
- [Kong Ingress Controller Docs](https://docs.konghq.com/kubernetes-ingress-controller/)
- [Existing Kong Templates](../../apps/fast-api-app-template/kong/)
- [Secret Request Flow](../85-how-it-works/self-service/SECRET_REQUEST_FLOW.md) (pattern reference)

## Approval Workflow

- [ ] Platform team review
- [ ] Architecture approval
- [ ] Security review (plugin allowlist)
- [ ] Roadmap prioritization

---

**Status**: Proposed (awaiting platform team review)
**Next Action**: Discuss at next platform architecture meeting
**Contact**: @platform-team for questions
