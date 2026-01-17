---
id: EC-0005-kubernetes-operator-framework
title: Kubernetes Operator Framework for GoldenPath
type: extension_capability
status: proposed
relates_to:
  - INDEX
  - ROADMAP
  - ADR-0002-platform-Kong-as-ingress-API-gateway
  - EC-0002-shared-parser-library
dependencies:
  - EKS (existing)
  - ArgoCD (existing)
  - Kong Ingress Controller (existing)
  - Python scripts (existing)
priority: high
vq_class: velocity
estimated_roi: $25,000/year (reduced manual reconciliation + faster app onboarding)
effort_estimate: 6-12 weeks (phased)
owner: platform-team
---

## Executive Summary

Extend GoldenPath IDP by leveraging the Kubernetes API, controllers, and reconciliation loops to provide declarative, self-healing platform capabilities. Instead of CI-triggered scripts, platform resources are defined as Custom Resource Definitions (CRDs) that Kubernetes controllers continuously reconcile.

**Key Benefits**:
- **Declarative**: Define desired state, controller ensures reality matches
- **Self-Healing**: Drift automatically corrected via reconciliation
- **GitOps-Native**: CRDs stored in Git, synced by ArgoCD
- **Unified API**: All platform resources accessible via `kubectl`

**Estimated ROI**: $25,000/year from reduced manual reconciliation, faster app onboarding, and eliminated drift.

**Strategic Fit**: 5/5 - Natural evolution of existing contract-driven patterns into Kubernetes-native resources.

## Problem Statement

Current GoldenPath self-service flows rely on:

1. **CI-Triggered Scripts**: Parsing YAML contracts and executing Terraform/kubectl
2. **Point-in-Time Execution**: No continuous reconciliation after initial apply
3. **Manual Drift Detection**: No automatic correction when state diverges
4. **Fragmented APIs**: Different interfaces for different resources (Backstage, GitHub, kubectl)

This creates:
- Drift between desired and actual state (discovered too late)
- Manual intervention required for recovery
- No unified "platform API" for all resources
- Slower onboarding (wait for CI pipelines)

## Proposed Solution

### Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GoldenPath Operator Framework                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │  GoldenPathApp   │    │  DatabaseClaim   │    │  IngressRequest  │      │
│  │      CRD         │    │      CRD         │    │      CRD         │      │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘      │
│           │                       │                       │                 │
│           ▼                       ▼                       ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Metacontroller / Kopf                             │  │
│  │                    (Python Webhook Handlers)                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│           │                       │                       │                 │
│           ▼                       ▼                       ▼                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐     │
│  │  Deployment  │    │   RDS Instance   │    │  Kong Ingress +      │     │
│  │  Service     │    │   (via Crossplane│    │  KongPlugin          │     │
│  │  HPA         │    │    or Terraform) │    │                      │     │
│  │  PodMonitor  │    │                  │    │                      │     │
│  └──────────────┘    └──────────────────┘    └──────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Custom Resource Definitions

#### 1. GoldenPathApp CRD

One resource to deploy a complete application stack:

```yaml
apiVersion: goldenpath.io/v1alpha1
kind: GoldenPathApp
metadata:
  name: payments-api
  namespace: payments
  labels:
    goldenpath.io/team: payments-team
    goldenpath.io/tier: production
spec:
  # Container configuration
  image: 123456789.dkr.ecr.eu-west-2.amazonaws.com/payments-api:v1.2.3
  replicas: 2
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Ingress configuration (generates Kong resources)
  ingress:
    enabled: true
    host: api.goldenpath.dev
    path: /api/v1/payments
    plugins:
      - type: rate-limiting
        config:
          minute: 100
      - type: key-auth

  # Database configuration (generates DatabaseClaim)
  database:
    enabled: true
    type: postgresql
    size: small  # maps to db.t3.micro

  # Secrets to inject (generates ExternalSecrets)
  secrets:
    - name: db-credentials
      source: goldenpath/prod/payments/postgres
      keys:
        - POSTGRES_USER
        - POSTGRES_PASSWORD
    - name: api-keys
      source: goldenpath/prod/payments/api-keys

  # Autoscaling
  scaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilization: 70

  # Observability (generates ServiceMonitor, alerts)
  monitoring:
    enabled: true
    alerting:
      enabled: true
      slackChannel: "#payments-alerts"
```

**Controller generates**:
- Deployment with proper labels, annotations, resource limits
- Service (ClusterIP)
- Ingress with Kong annotations
- KongPlugin resources (rate-limiting, key-auth)
- HorizontalPodAutoscaler
- ServiceMonitor for Prometheus
- PrometheusRule for alerts
- ExternalSecret for AWS Secrets Manager sync

#### 2. DatabaseClaim CRD

Self-service database provisioning:

```yaml
apiVersion: goldenpath.io/v1alpha1
kind: DatabaseClaim
metadata:
  name: payments-db
  namespace: payments
spec:
  engine: postgresql
  version: "15"
  size: small  # small/medium/large/xlarge
  storage:
    size: 20Gi
    maxSize: 100Gi
  backup:
    enabled: true
    retentionDays: 7
  highAvailability: false  # true for prod

  # Where to store credentials
  secretRef:
    name: payments-db-credentials

  # Access control
  allowedNamespaces:
    - payments
    - payments-worker
```

**Controller reconciles**:
- Creates/updates RDS instance (via Crossplane or Terraform)
- Generates credentials in Secrets Manager
- Creates ExternalSecret to sync to K8s
- Sets up security groups for namespace access

#### 3. IngressRequest CRD

Self-service Kong ingress configuration:

```yaml
apiVersion: goldenpath.io/v1alpha1
kind: IngressRequest
metadata:
  name: payments-api-ingress
  namespace: payments
spec:
  host: api.goldenpath.dev
  path: /api/v1/payments
  service:
    name: payments-api
    port: 8080

  plugins:
    - type: rate-limiting
      config:
        minute: 100
        policy: local
    - type: cors
      config:
        origins: ["https://app.goldenpath.dev"]
        methods: ["GET", "POST", "PUT", "DELETE"]
    - type: key-auth
      config:
        keyNames: ["apikey", "x-api-key"]
        hideCredentials: true

  # Traffic management
  traffic:
    retries: 3
    timeout: 30s

  # TLS configuration
  tls:
    enabled: true
    secretName: api-goldenpath-tls
```

**Controller generates**:
- Kubernetes Ingress with Kong annotations
- KongPlugin resources for each plugin
- KongConsumer if auth is enabled

#### 4. SecretSync CRD

Continuous secret synchronization:

```yaml
apiVersion: goldenpath.io/v1alpha1
kind: SecretSync
metadata:
  name: payments-secrets
  namespace: payments
spec:
  source:
    provider: aws-secrets-manager
    region: eu-west-2
    secrets:
      - path: goldenpath/prod/payments/postgres
        keys:
          - sourceKey: username
            targetKey: POSTGRES_USER
          - sourceKey: password
            targetKey: POSTGRES_PASSWORD
      - path: goldenpath/prod/payments/api-keys
        keys:
          - sourceKey: stripe_key
            targetKey: STRIPE_API_KEY

  target:
    secretName: payments-env

  refreshInterval: 1h

  # Restart deployments when secrets change
  restartTargets:
    - kind: Deployment
      name: payments-api
```

### Controller Implementation Options

| Approach | Language | Complexity | GoldenPath Fit | Recommendation |
|----------|----------|------------|----------------|----------------|
| **Metacontroller** | Python (webhooks) | Low | Excellent | **V1 - Start Here** |
| **Kopf** | Python | Medium | Excellent | V1 Alternative |
| **Kubebuilder** | Go | High | Good | V2+ |
| **Crossplane** | YAML + Go | Medium | Good | Infrastructure CRDs |

### V1: Metacontroller + Python Webhooks

Metacontroller is ideal for V1 because:
- Reuses existing Python expertise from GoldenPath scripts
- No need to learn Go or controller-runtime
- Simple HTTP webhook interface
- Handles watch/reconcile mechanics automatically

**Metacontroller Installation**:
```yaml
# gitops/kustomize/base/platform-system/metacontroller/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - https://github.com/metacontroller/metacontroller/manifests/production
```

**CompositeController Definition**:
```yaml
# gitops/kustomize/base/platform-system/goldenpath-controller/controller.yaml
apiVersion: metacontroller.k8s.io/v1alpha1
kind: CompositeController
metadata:
  name: goldenpath-app-controller
spec:
  generateSelector: true
  parentResource:
    apiVersion: goldenpath.io/v1alpha1
    resource: goldenpathapps
  childResources:
    - apiVersion: apps/v1
      resource: deployments
      updateStrategy:
        method: InPlace
    - apiVersion: v1
      resource: services
    - apiVersion: networking.k8s.io/v1
      resource: ingresses
    - apiVersion: configuration.konghq.com/v1
      resource: kongplugins
    - apiVersion: autoscaling/v2
      resource: horizontalpodautoscalers
    - apiVersion: monitoring.coreos.com/v1
      resource: servicemonitors
  hooks:
    sync:
      webhook:
        url: http://goldenpath-controller.platform-system:8080/sync/app
    finalize:
      webhook:
        url: http://goldenpath-controller.platform-system:8080/finalize/app
```

**Python Webhook Handler**:
```python
# controllers/goldenpath_controller/app.py
"""
---
id: SCRIPT-0038
type: controller
owner: platform-team
status: active
maturity: 1
---
GoldenPath App Controller - Metacontroller webhook handler
"""

from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/sync/app', methods=['POST'])
def sync_app():
    """Reconcile GoldenPathApp to child resources."""
    req = request.get_json()
    parent = req['parent']
    children = req.get('children', {})

    spec = parent['spec']
    metadata = parent['metadata']
    name = metadata['name']
    namespace = metadata['namespace']
    labels = metadata.get('labels', {})

    desired_children = []

    # Generate Deployment
    desired_children.append(generate_deployment(name, namespace, spec, labels))

    # Generate Service
    desired_children.append(generate_service(name, namespace, spec, labels))

    # Generate Ingress + Kong Plugins if enabled
    if spec.get('ingress', {}).get('enabled'):
        ingress, plugins = generate_ingress(name, namespace, spec, labels)
        desired_children.append(ingress)
        desired_children.extend(plugins)

    # Generate HPA if scaling enabled
    if spec.get('scaling', {}).get('enabled'):
        desired_children.append(generate_hpa(name, namespace, spec))

    # Generate ServiceMonitor if monitoring enabled
    if spec.get('monitoring', {}).get('enabled'):
        desired_children.append(generate_service_monitor(name, namespace, spec, labels))

    return jsonify({
        'children': desired_children,
        'status': {
            'phase': 'Running',
            'replicas': spec.get('replicas', 1),
            'observedGeneration': metadata.get('generation', 1)
        }
    })


def generate_deployment(name, namespace, spec, labels):
    """Generate Deployment from GoldenPathApp spec."""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {
                'app': name,
                'goldenpath.io/managed': 'true',
                **labels
            }
        },
        'spec': {
            'replicas': spec.get('replicas', 1),
            'selector': {
                'matchLabels': {'app': name}
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': name,
                        **labels
                    }
                },
                'spec': {
                    'containers': [{
                        'name': name,
                        'image': spec['image'],
                        'resources': spec.get('resources', {
                            'requests': {'cpu': '100m', 'memory': '256Mi'},
                            'limits': {'cpu': '500m', 'memory': '512Mi'}
                        }),
                        'ports': [{'containerPort': 8080}],
                        'envFrom': generate_env_from(spec.get('secrets', []))
                    }]
                }
            }
        }
    }


def generate_service(name, namespace, spec, labels):
    """Generate Service from GoldenPathApp spec."""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {'app': name, **labels}
        },
        'spec': {
            'selector': {'app': name},
            'ports': [{'port': 8080, 'targetPort': 8080}]
        }
    }


def generate_ingress(name, namespace, spec, labels):
    """Generate Ingress and KongPlugins from GoldenPathApp spec."""
    ingress_spec = spec['ingress']
    plugins = []
    plugin_names = []

    for plugin_config in ingress_spec.get('plugins', []):
        plugin_name = f"{name}-{plugin_config['type']}"
        plugin_names.append(plugin_name)
        plugins.append({
            'apiVersion': 'configuration.konghq.com/v1',
            'kind': 'KongPlugin',
            'metadata': {
                'name': plugin_name,
                'namespace': namespace,
                'labels': {'app': name, **labels}
            },
            'plugin': plugin_config['type'],
            'config': plugin_config.get('config', {})
        })

    ingress = {
        'apiVersion': 'networking.k8s.io/v1',
        'kind': 'Ingress',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {'app': name, **labels},
            'annotations': {
                'konghq.com/plugins': ','.join(plugin_names),
                'konghq.com/strip-path': 'true'
            }
        },
        'spec': {
            'ingressClassName': 'kong',
            'rules': [{
                'host': ingress_spec['host'],
                'http': {
                    'paths': [{
                        'path': ingress_spec['path'],
                        'pathType': 'Prefix',
                        'backend': {
                            'service': {
                                'name': name,
                                'port': {'number': 8080}
                            }
                        }
                    }]
                }
            }]
        }
    }

    return ingress, plugins


def generate_hpa(name, namespace, spec):
    """Generate HorizontalPodAutoscaler from GoldenPathApp spec."""
    scaling = spec['scaling']
    return {
        'apiVersion': 'autoscaling/v2',
        'kind': 'HorizontalPodAutoscaler',
        'metadata': {'name': name, 'namespace': namespace},
        'spec': {
            'scaleTargetRef': {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'name': name
            },
            'minReplicas': scaling.get('minReplicas', 1),
            'maxReplicas': scaling.get('maxReplicas', 10),
            'metrics': [{
                'type': 'Resource',
                'resource': {
                    'name': 'cpu',
                    'target': {
                        'type': 'Utilization',
                        'averageUtilization': scaling.get('targetCPUUtilization', 70)
                    }
                }
            }]
        }
    }


def generate_service_monitor(name, namespace, spec, labels):
    """Generate ServiceMonitor for Prometheus from GoldenPathApp spec."""
    return {
        'apiVersion': 'monitoring.coreos.com/v1',
        'kind': 'ServiceMonitor',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {'app': name, **labels}
        },
        'spec': {
            'selector': {'matchLabels': {'app': name}},
            'endpoints': [{'port': 'http', 'interval': '30s'}]
        }
    }


def generate_env_from(secrets):
    """Generate envFrom for secrets."""
    return [{'secretRef': {'name': s['name']}} for s in secrets]


@app.route('/finalize/app', methods=['POST'])
def finalize_app():
    """Handle GoldenPathApp deletion."""
    req = request.get_json()
    # Cleanup logic here (e.g., delete RDS, cleanup secrets)
    return jsonify({'finalized': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

## Strategic Use Cases

### Use Case 1: One-Command App Deployment

**Before**: Create Deployment, Service, Ingress, KongPlugins, HPA, ServiceMonitor separately.
**After**: `kubectl apply -f payments-app.yaml` creates everything.

**Value**: App deployment time reduced from 30 min to 2 min.

### Use Case 2: Self-Healing Configuration

**Before**: Someone manually edits Ingress, drift goes unnoticed.
**After**: Controller detects drift, reconciles back to desired state.

**Value**: Zero configuration drift, reduced incidents.

### Use Case 3: Unified Platform API

**Before**: Different interfaces for different resources.
**After**: `kubectl get goldenpathapps -A` shows all apps.

**Value**: Single pane of glass for platform resources.

### Use Case 4: GitOps-Native Everything

**Before**: Some resources in Git, some manual.
**After**: All platform resources as CRDs in Git, synced by ArgoCD.

**Value**: Complete audit trail, easy rollback.

## Implementation Roadmap

### Phase 1: Metacontroller + GoldenPathApp (Weeks 1-3)

- [ ] Install Metacontroller via ArgoCD
- [ ] Define GoldenPathApp CRD
- [ ] Implement Python webhook handler (SCRIPT-0038)
- [ ] Deploy controller to platform-system namespace
- [ ] Test with sample app
- [ ] Add to ArgoCD ApplicationSet

**Deliverables**:
- Working GoldenPathApp CRD
- Controller generating Deployment, Service, Ingress, HPA
- Documentation and examples

### Phase 2: IngressRequest + SecretSync (Weeks 4-6)

- [ ] Define IngressRequest CRD
- [ ] Define SecretSync CRD
- [ ] Implement webhook handlers
- [ ] Integrate with existing Kong setup
- [ ] Integrate with External Secrets Operator

**Deliverables**:
- Self-service Kong configuration via CRD
- Continuous secret sync from AWS

### Phase 3: DatabaseClaim + Crossplane (Weeks 7-10)

- [ ] Install Crossplane
- [ ] Define DatabaseClaim CRD
- [ ] Create Crossplane Compositions for RDS
- [ ] Integrate with existing RDS patterns
- [ ] Add cost controls and quotas

**Deliverables**:
- Self-service RDS provisioning
- Database lifecycle management

### Phase 4: Migration + Documentation (Weeks 11-12)

- [ ] Migrate existing apps to GoldenPathApp CRDs
- [ ] Create Backstage plugin for CRD management
- [ ] Write runbooks and troubleshooting guides
- [ ] Training for app teams

**Deliverables**:
- All platform apps using CRDs
- Complete documentation

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Controller Failure** | High | Deploy HA (2+ replicas), add liveness probes, alerting |
| **Reconciliation Loop** | Medium | Add generation tracking, rate limiting |
| **Breaking Changes** | Medium | Version CRDs (v1alpha1 → v1beta1 → v1), conversion webhooks |
| **Learning Curve** | Low | Reuse Python skills, good docs, Backstage integration |
| **Metacontroller Dependency** | Medium | Metacontroller is mature; fallback to Kopf if needed |

## Cost Analysis

### Implementation Cost

| Phase | Effort | Cost (@ $80/hr) |
|-------|--------|-----------------|
| Phase 1 | 3 weeks | $9,600 |
| Phase 2 | 3 weeks | $9,600 |
| Phase 3 | 4 weeks | $12,800 |
| Phase 4 | 2 weeks | $6,400 |
| **Total** | 12 weeks | **$38,400** |

### Operational Savings

| Metric | Before | After | Annual Savings |
|--------|--------|-------|----------------|
| App onboarding time | 2 hours | 10 min | $8,000 |
| Drift remediation | 4 hrs/month | 0 | $3,840 |
| Platform team toil | 5 hrs/week | 1 hr/week | $16,640 |
| **Total Annual Savings** | | | **$28,480** |

### ROI Calculation

- Year 1: $28,480 - $38,400 = -$9,920 (investment)
- Year 2+: $28,480/year net savings
- **Payback Period**: ~16 months

## Monitoring & Success Metrics

### Technical Metrics

- **Reconciliation Latency**: P95 < 5 seconds
- **Drift Detection Time**: < 1 minute
- **Controller Availability**: 99.9%
- **CRD Adoption**: 100% of new apps using GoldenPathApp

### Business Metrics

- **App Onboarding Time**: 2 hours → 10 minutes
- **Configuration Incidents**: -80%
- **Platform Team Toil**: -75%

## Alternatives Considered

### Option 1: Continue with CI-Only Approach

**Pros**: No new infrastructure, simpler
**Cons**: No continuous reconciliation, drift accumulates

**Decision**: Rejected - doesn't solve core problems

### Option 2: Full Kubebuilder Operator

**Pros**: Production-grade, full control
**Cons**: Requires Go expertise, longer development time

**Decision**: Deferred to V2+ if Metacontroller insufficient

### Option 3: Crossplane Only

**Pros**: Mature, infrastructure-focused
**Cons**: Overkill for K8s-native resources, complex

**Decision**: Use for Phase 3 (DatabaseClaim), not for app resources

## Files to Create

| File | Purpose |
|------|---------|
| `crds/goldenpath.io_goldenpathapps.yaml` | GoldenPathApp CRD definition |
| `crds/goldenpath.io_ingressrequests.yaml` | IngressRequest CRD definition |
| `crds/goldenpath.io_secretsyncs.yaml` | SecretSync CRD definition |
| `crds/goldenpath.io_databaseclaims.yaml` | DatabaseClaim CRD definition |
| `controllers/goldenpath_controller/` | Python webhook handlers |
| `gitops/kustomize/base/platform-system/metacontroller/` | Metacontroller install |
| `gitops/kustomize/base/platform-system/goldenpath-controller/` | Controller deployment |
| `docs/85-how-it-works/OPERATOR_FRAMEWORK.md` | Architecture documentation |
| `docs/70-operations/runbooks/RB-0036-operator-troubleshooting.md` | Runbook |

## Governance Compliance

### Born Governed Checklist

- [ ] CRD schemas with validation
- [ ] Controller metadata header (SCRIPT-0038)
- [ ] ADR documentation (ADR-0171)
- [ ] Changelog entry (CL-0147)
- [ ] Runbook creation (RB-0036)
- [ ] ArgoCD GitOps deployment
- [ ] Prometheus metrics + alerts

## Additional Recommendations

- **CRD scope boundaries**: start with narrow CRDs (App, Ingress, Secrets) and keep infra-heavy resources (RDS, EKS) behind existing Terraform gates until reconciliation is proven.
- **Admission control**: add a validating webhook (OPA/Gatekeeper or Kyverno) to block unsafe CRD specs (public ingress, weak encryption, missing ownership).
- **Finalizers for teardown**: ensure CR deletions trigger cleanup (revoking IAM, deleting ExternalSecrets, draining Ingress rules) before CR removal.
- **Drift repair policy**: decide which fields are authoritative in-cluster vs Git, and document which drift is auto-corrected vs flagged.
- **Observability contract**: emit controller metrics (reconcile duration, error rate), and include `reason` in Kubernetes Events for auditability.
- **Bootstrap safety**: add a canary namespace and feature flags to roll out controllers gradually.
- **Naming conventions**: use CamelCase for CRD kinds and snake_case for controller Python modules to align with repo standards.


# Harnessing the K8s API: Moving Beyond Scripts

## Context
The current platform relies heavily on "One-Off Triggers" (GitHub Actions -> Python Scripts) for automation. To scale, we must move towards **"Continuous Reconciliation"** (Operator -> Desired State Loop) inherent to the Kubernetes API.

## Extensibility Strategy: The 3 Levels

### 1. Compliance Controllers (Policy-as-Code)
*   **The Problem**: Validation logic is scattered in CI pipelines or Python scripts.
*   **The K8s Solution**: **Kyverno** (Cluster Admission Controller).
*   **Mechanism**: Define `ClusterPolicy` CRDs. The API server validates requests before they persist.
*   **Example**: "All `SecretRequests` must have a `risk` label."
*   **Benefit**: Rejects bad data at the gate. Cleaner than imperative `if/else` logic.
*   **Action**: Adopt Kyverno policies to replace custom Python validation logic.

### 2. Infrastructure Controllers (Composite Resources)
*   **The Problem**: Imperative provisioning scripts (`rds_provision.py`) are brittle. If they crash, resources are left in inconsistent states.
*   **The K8s Solution**: **Crossplane**.
*   **Mechanism**:
    1.  Define a `CompositeResourceDefinition` (XRD) (e.g., `GoldenPathDatabase`).
    2.  Create a `Composition` mapping the XRD to real resources (AWS RDS Instance + K8s Secret + Helm Release).
    3.  **Reconciliation**: The controller continuously watches the resource. If changed/deleted externally, it is immediately self-healed.
*   **Benefit**: Declarative Infrastructure-as-Data. No more "Create vs Delete" scripts.
*   **Action**: Prioritize replacing `rds_provision.py` with a Crossplane Composition.

### 3. Custom Controllers (The "Operator Pattern")
*   **The Problem**: Complex "Glue" logic (e.g., `goldenpath-idp-teardown-v3.sh`) exists to clean up hanging dependencies like ALBs.
*   **The K8s Solution**: **Finalizer Operator**.
*   **Mechanism**: A custom controller (Kubebuilder/Kopf) watches resources. On deletion, it executes cleanup logic *before* removing the finalizer and allowing deletion.
*   **Benefit**: Elimination of massive Bash cleanup scripts. Lifecycle logic lives inside the cluster.

---

## Verdict & Recommendation

**Recommendation for V1:**
Avoid writing custom operators (Level 3) initially as they incur high maintenance.

**Strategic Pivot:**
1.  **Skip Level 3 (Custom Operators)** for now.
2.  **Adopt Level 2 (Crossplane)** immediately. It standardizes the "Golden Path" definition into Kubernetes CRDs, effectively replacing the current imperative Python/Terraform wrapping.

---
**Signed:** Antigravity Agent
**Timestamp:** 2026-01-17T23:00:19Z

## References

- [Metacontroller Documentation](https://metacontroller.github.io/metacontroller/)
- [Kopf - Kubernetes Operators in Python](https://kopf.readthedocs.io/)
- [Kubebuilder Book](https://book.kubebuilder.io/)
- [Crossplane Documentation](https://crossplane.io/docs/)
- [Kubernetes Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)

## Approval Workflow

- [ ] Platform team review
- [ ] Architecture approval
- [ ] Security review (RBAC, webhook security)
- [ ] Roadmap prioritization

---

**Status**: Proposed (awaiting platform team review)
**Next Action**: Discuss at next platform architecture meeting
**Contact**: @platform-team for questions
