---
id: EC-0001-knative-integration
title: Knative Integration for Serverless Workloads
status: proposed
dependencies:
  - EKS cluster (ADR-0148)
  - ArgoCD (existing)
  - Istio or Contour (new dependency)
relates_to:
  - ADR-0148
  - ROADMAP.md
type: extension_capability
priority: medium
vq_class: efficiency
estimated_roi: $13,000/year
effort_estimate: 9 weeks
---

## Executive Summary

Knative provides a Kubernetes-native serverless platform that could enhance Golden Path IDP by enabling:

- **Cost Optimization**: Scale-to-zero for development/staging workloads (~$13K/year savings)
- **Developer Self-Service**: Event-driven microservices without Kubernetes expertise
- **Operational Efficiency**: Automated scaling and traffic management

**Estimated ROI**: $13,000/year from compute savings alone, plus developer velocity improvements.

**Strategic Fit**: 4/5 - Strong alignment with platform goals, moderate integration complexity.

## Problem Statement

Golden Path IDP currently lacks native serverless capabilities. Development teams face:

1. **Over-provisioned Resources**: Dev/staging services run 24/7 even when idle
2. **Complex Scaling Configuration**: Manual HPA setup for each service
3. **Traffic Management Overhead**: Blue/green deployments require custom configuration
4. **Event-Driven Gaps**: No native event subscription model for microservices

## Proposed Solution

Integrate Knative to provide two core capabilities:

### 1. Knative Serving

- Serverless containers with scale-to-zero
- Automatic traffic splitting for canary deployments
- Built-in revision management

### 2. Knative Eventing

- CloudEvents-native event routing
- Event source bindings (AWS EventBridge, SQS, Kafka)
- Declarative event subscriptions

## Architecture Integration

### Current Stack Enhancement

```text
┌─────────────────────────────────────────────────────┐
│                  Golden Path IDP                     │
├─────────────────────────────────────────────────────┤
│  ArgoCD (GitOps)                                    │
│    ↓                                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  EKS Cluster (ADR-0148)                      │  │
│  │                                               │  │
│  │  ┌──────────────┐    ┌──────────────────┐   │  │
│  │  │   Existing   │    │   NEW: Knative   │   │  │
│  │  │  Workloads   │    │                  │   │  │
│  │  │              │    │  - Serving       │   │  │
│  │  │  - Standard  │    │  - Eventing      │   │  │
│  │  │    Deploys   │    │  - Istio/Contour │   │  │
│  │  └──────────────┘    └──────────────────┘   │  │
│  │                                               │  │
│  │  Shared: Metrics, Logs, IAM (IRSA), Storage  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Governance Model

Knative resources follow Born Governed principles:

```yaml
# docs/catalogs/services/api/dev/SVC-0042.yaml
apiVersion: goldenpath.io/v1
kind: ServiceRequest
type: knative_service
id: SVC-0042
title: "Events API - Serverless"
owner: events-team
metadata:
  service: events-api
  environment: dev
spec:
  serving:
    image: 123456789012.dkr.ecr.eu-west-2.amazonaws.com/events-api:latest
    minScale: 0  # Scale to zero
    maxScale: 10
    targetConcurrency: 100
  eventing:
    triggers:
      - broker: default
        filter:
          type: com.goldenpath.order.created
```

## Strategic Use Cases

### Use Case 1: Cost Optimization for Dev/Staging

**Problem**: Development services consume resources 24/7 despite sporadic usage.

**Solution**:

- Knative Serving with scale-to-zero for non-prod workloads
- Automatic cold-start warming for production-like testing

**Value**:

- Estimated 60% reduction in non-prod compute costs
- $13,000/year savings for 20 dev services

### Use Case 2: Event-Driven Microservices

**Problem**: Teams build custom event handling with Lambda + SQS, creating operational silos.

**Solution**:

- Knative Eventing with CloudEvents standard
- Kubernetes-native event routing with observability

**Value**:

- Unified platform for event-driven services
- Reduced AWS Lambda sprawl
- Built-in tracing and monitoring

### Use Case 3: Developer Self-Service

**Problem**: Developers need Kubernetes expertise for basic deployments.

**Solution**:

- Knative Services as simple abstraction over Deployments/Services/Ingress
- Schema-driven service requests (SVC-XXXX)

**Value**:

- Reduced onboarding time for service deployments
- Platform team focuses on policy, not individual service configs

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3)

- [ ] Choose networking layer (Istio vs. Contour)
- [ ] Create Terraform module for Knative Operator
- [ ] Deploy to dev cluster with basic Serving
- [ ] Create ADR-0149: Knative Integration Architecture

**Deliverables**:

- `modules/knative/` Terraform module
- ADR-0149 approved
- Basic "Hello World" Knative Service deployed

### Phase 2: Governance Integration (Weeks 4-6)

- [ ] Create `schemas/metadata/service_request.schema.yaml`
- [ ] Build `scripts/knative_service_parser.py` (SCRIPT-0051)
- [ ] Integrate with ArgoCD workflow
- [ ] Create first governed service (SVC-0001)

**Deliverables**:

- Schema-driven Knative Service provisioning
- SCRIPT-0051 with Born Governed metadata
- Documentation: RB-0030-knative-operations.md

### Phase 3: Eventing & Observability (Weeks 7-9)

- [ ] Deploy Knative Eventing with AWS EventBridge source
- [ ] Configure CloudEvents routing
- [ ] Integrate with existing Prometheus/Grafana
- [ ] Create runbooks for troubleshooting

**Deliverables**:

- Event-driven service examples
- Grafana dashboards for Knative metrics
- Runbook: RB-0030

## Risk Analysis

|Risk|Impact|Mitigation|
|------|--------|------------|
|**Networking Complexity**|High|Start with Contour (simpler than Istio), defer service mesh|
|**Cold Start Latency**|Medium|Production services keep minScale=1, optimize container images|
|**Team Learning Curve**|Medium|Provide templates, runbooks, and examples first|
|**Cost of Networking Layer**|Low|Contour is lightweight; Istio deferred until needed|
|**Integration Testing**|Medium|Schema validation + dry-run mode in parser script|

## Monitoring & Success Metrics

### Technical Metrics

- **Scale-to-zero effectiveness**: % of time pods at zero replicas
- **Cold start P95**: <2 seconds for dev services
- **Event delivery latency**: P95 <500ms

### Business Metrics

- **Cost savings**: Target 60% reduction in non-prod compute
- **Developer velocity**: Service deployment time <10 minutes
- **Platform adoption**: 20% of services on Knative by Q3

## Alternatives Considered

### Option 1: AWS Lambda + API Gateway

**Pros**: Fully managed, proven serverless
**Cons**:

- Vendor lock-in
- Operational silos (Lambda vs. Kubernetes)
- No CloudEvents standard

**Decision**: Rejected - Breaks unified platform model

### Option 2: KEDA (Kubernetes Event-Driven Autoscaling)

**Pros**: Lighter weight, works with existing Deployments
**Cons**:

- Doesn't provide traffic splitting
- No built-in eventing model
- Still requires manual HPA configuration

**Decision**: Consider for Phase 2 if Knative Serving too heavy

### Option 3: Status Quo (Standard Kubernetes)

**Pros**: No new dependencies
**Cons**:

- Manual scaling configuration
- No scale-to-zero
- Custom solutions for traffic management

**Decision**: Rejected - Misses cost and velocity opportunities

## Technical Deep Dive

### Knative Serving Architecture

```yaml
# Generated by knative_service_parser.py from SVC-0042.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: events-api
  namespace: dev
  annotations:
    goldenpath.io/id: SVC-0042
    goldenpath.io/owner: events-team
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/target: "100"
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      serviceAccountName: events-api  # IRSA for AWS permissions
      containers:
        - image: 123456789012.dkr.ecr.eu-west-2.amazonaws.com/events-api:latest
          env:
            - name: AWS_REGION
              value: eu-west-2
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 1000m
              memory: 512Mi
```

### Integration with ArgoCD Image Updater

Knative Services work seamlessly with existing Image Updater:

```yaml
# ArgoCD Application for Knative Service
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: events-api-dev
  annotations:
    argocd-image-updater.argoproj.io/image-list: events-api=123456789012.dkr.ecr.eu-west-2.amazonaws.com/events-api
    argocd-image-updater.argoproj.io/events-api.update-strategy: latest
spec:
  source:
    path: gitops/apps/events-api/dev
    repoURL: https://github.com/goldenpath/gitops
  destination:
    namespace: dev
```

### Eventing Example: Order Processing

```yaml
# Event Source: AWS EventBridge
apiVersion: sources.knative.dev/v1alpha1
kind: AwsEventBridgeSource
metadata:
  name: order-events
  namespace: prod
spec:
  arn: arn:aws:events:eu-west-2:123456789012:event-bus/orders
  serviceAccountName: eventbridge-source  # IRSA role
  sink:
    ref:
      apiVersion: eventing.knative.dev/v1
      kind: Broker
      name: default

---
# Trigger: Route order.created events to service
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: order-fulfillment
  namespace: prod
spec:
  broker: default
  filter:
    attributes:
      type: com.goldenpath.order.created
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: fulfillment-service
```

## Governance Compliance

### Born Governed Checklist

- [x] Schema-driven provisioning (service_request.schema.yaml)
- [x] Metadata header for scripts (SCRIPT-0051)
- [x] ADR documentation (ADR-0149)
- [x] Changelog entry (CL-0122)
- [x] Runbook creation (RB-0030)
- [x] IRSA integration for AWS permissions
- [x] ArgoCD GitOps workflow
- [x] Audit trail (SVC-XXXX IDs)

### Testing Requirements (TESTING_STANDARDS.md)

### Phase 1: PLAN

- [ ] Test plan for Knative installation
- [ ] Schema validation test cases
- [ ] Cold start performance benchmarks

### Phase 2: SETUP

- [ ] Test cluster isolation
- [ ] Sample Knative Services
- [ ] Event source mocks

### Phase 3: EXECUTE

- [ ] Scale-to-zero verification
- [ ] Traffic splitting validation
- [ ] Event delivery tests

### Phase 4: DOCUMENT

- [ ] Test results in tests/reports/
- [ ] Known issues documented

### Phase 5: VERIFY

- [ ] Runbook validation
- [ ] Rollback procedures tested

## Cost Analysis

### Infrastructure Costs

|Component|Monthly Cost|Annual Cost|
|-----------|--------------|-------------|
|**Contour Ingress**|$50 (2 pods, t3.small)|$600|
|**Knative Operator**|$20 (1 pod, minimal)|$240|
|**Total New Costs**|$70/month|$840/year|

### Savings

|Optimization|Monthly Savings|Annual Savings|
|--------------|-----------------|----------------|
|**Dev Services Scale-to-Zero**|~$800 (20 services)|$9,600|
|**Staging Optimization**|~$300|$3,600|
|**Total Savings**|$1,100/month|$13,200/year|

**Net ROI**: $13,200 - $840 = **$12,360/year** (~1,400% return)

## Open Questions

1. **Networking Layer**: Contour (simpler) or Istio (full service mesh)?
   - **Recommendation**: Start with Contour, defer Istio until service mesh needed

2. **Production Readiness**: Should production services use Knative?
   - **Recommendation**: Dev/staging first, production opt-in after 3 months

3. **Event Sources**: Which AWS services need integration?
   - **Recommendation**: Start with EventBridge, add SQS/SNS in Phase 3

4. **Multi-Tenancy**: How to isolate team events?
   - **Recommendation**: Namespace-scoped Brokers, not cluster-wide

## References

- [Knative Documentation](https://knative.dev/docs/)
- [CloudEvents Specification](https://cloudevents.io/)
- [AWS EventBridge Source](https://github.com/knative-extensions/eventing-awssqs)
- [Contour vs Istio Comparison](https://knative.dev/docs/install/serving/install-serving-with-yaml/)

## Approval Workflow

- [ ] Platform team review
- [ ] Architecture approval (converts to ADR-0149)
- [ ] Security review (IRSA permissions)
- [ ] Cost approval (VQ validation)
- [ ] Roadmap prioritization

---

**Status**: Proposed (awaiting platform team review)
**Next Action**: Discuss at next platform architecture meeting
**Contact**: @platform-team for questions
