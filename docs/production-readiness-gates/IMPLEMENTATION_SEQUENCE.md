---
id: IMPLEMENTATION_SEQUENCE
title: Golden Path IDP - Implementation Sequence
type: implementation-plan
status: proposed
owner: platform-team
priority: critical
vq_class: 🔴 HV/HQ
relates_to:
  - ROADMAP
  - EC-0003-kong-backstage-plugin
  - EC-0007-kpack-buildpacks-integration
  - ADR-0162-kong-ingress-dns-strategy
---

# Golden Path IDP - Implementation Sequence

This document provides an ordered implementation plan for bringing the Golden Path IDP to production readiness.

## Overview

**Goal**: Spin up cluster, configure app scaffolding (stateless + stateful), test Backstage templates, enable AWS resource creation via Backstage, integrate Route53 with goldenpathidp.io domain, configure Kong ingress, and establish end-to-end image deployment.

---

## Phase 0: Prerequisites & Domain Setup (Day 1)

### 0.1 Route53 Domain Configuration

**Status**: Gap - No Terraform automation exists

| Task | Owner | Dependency |
|------|-------|------------|
| Create Route53 hosted zone for `goldenpathidp.io` | platform-team | Domain purchased |
| Update domain registrar NS records | platform-team | Hosted zone created |
| Create Terraform module for Route53 | platform-team | None |

**Files to Create**:

```
modules/aws_route53/
├── main.tf           # Hosted zone, records
├── variables.tf      # Domain name, records list
├── outputs.tf        # Zone ID, nameservers
└── README.md
```

**DNS Record Strategy**:

| Record | Type | Target | Environment |
|--------|------|--------|-------------|
| `*.dev.goldenpathidp.io` | CNAME | Kong LB (dev) | dev |
| `*.staging.goldenpathidp.io` | CNAME | Kong LB (staging) | staging |
| `*.goldenpathidp.io` | CNAME | Kong LB (prod) | prod |
| `argocd.dev.goldenpathidp.io` | A/Alias | Kong LB | dev |
| `backstage.dev.goldenpathidp.io` | A/Alias | Kong LB | dev |
| `grafana.dev.goldenpathidp.io` | A/Alias | Kong LB | dev |

### 0.2 Create Custom Backstage Image Repository

**Status**: Gap - No custom image build pipeline

| Task | Owner | Dependency |
|------|-------|------------|
| Create GitHub repo `goldenpath-backstage` | platform-team | None |
| Add Dockerfile with plugin dependencies | platform-team | Repo created |
| Create GitHub Actions build workflow | platform-team | Dockerfile |
| Push to ECR | platform-team | ECR repo exists |

**Repository Structure**:

```
goldenpath-backstage/
├── Dockerfile
├── packages/
│   ├── app/                    # Frontend customizations
│   │   └── src/
│   └── backend/                # Backend customizations
│       └── src/
├── plugins/                    # Custom plugins
│   └── kong-catalog/           # EC-0003 implementation
├── app-config.yaml             # Base config
├── app-config.production.yaml  # Production overrides
├── catalog-info.yaml           # Self-registration
└── .github/
    └── workflows/
        └── build-push.yml      # CI/CD pipeline
```

---

## Phase 1: Infrastructure Foundation (Day 1-2)

### 1.1 Spin Up EKS Cluster

**Status**: Exists - Use existing Terraform + Bootstrap

```bash
# Generate Build ID
export BUILD_ID=$(date +%d-%m-%y)-01

# Initialize and deploy
make deploy ENV=dev BUILD_ID=$BUILD_ID
```

**Verification**:

```bash
kubectl get nodes
kubectl get namespaces
```

### 1.2 Bootstrap Platform Tooling

**Status**: Exists - Automated via bootstrap scripts

The `make deploy` command executes:

1. `10_argocd_helm.sh` - ArgoCD installation
2. `20_argocd_admin_access.sh` - Admin credentials
3. `20_kong_ingress.sh` - Kong deployment
4. `30_keycloak.sh` - Identity provider
5. `40_external_secrets.sh` - Secrets management
6. `50_cert_manager.sh` - TLS certificates

**Verification**:

```bash
kubectl get pods -n argocd
kubectl get pods -n kong-system
kubectl get svc -n kong-system kong-kong-proxy  # Get LB address
```

### 1.3 Configure Route53 DNS Records

**Status**: Gap - Manual step required

```bash
# Get Kong Load Balancer address
KONG_LB=$(kubectl get svc -n kong-system kong-kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Create DNS records (manual or via Terraform)
# *.dev.goldenpathidp.io -> $KONG_LB
```

**Suggested Terraform**:

```hcl
# envs/dev/route53.tf
resource "aws_route53_record" "wildcard_dev" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "*.dev.goldenpathidp.io"
  type    = "CNAME"
  ttl     = 300
  records = [data.kubernetes_service.kong_proxy.status[0].load_balancer[0].ingress[0].hostname]
}
```

---

## Phase 2: Kong Ingress Configuration (Day 2-3)

### 2.1 Configure Kong for Tooling Stack

**Status**: Partial - Kong deployed, ingress rules needed

| Service | Hostname | Path | Auth |
|---------|----------|------|------|
| ArgoCD | `argocd.dev.goldenpathidp.io` | `/` | SSO |
| Backstage | `backstage.dev.goldenpathidp.io` | `/` | SSO |
| Grafana | `grafana.dev.goldenpathidp.io` | `/` | SSO |
| Keycloak | `keycloak.dev.goldenpathidp.io` | `/` | Public |

**Files to Create/Update**:

```yaml
# gitops/kustomize/overlays/dev/platform/kong/ingress-tooling.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: platform-tooling
  namespace: platform
  annotations:
    konghq.com/strip-path: "false"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: kong
  tls:
    - hosts:
        - "*.dev.goldenpathidp.io"
      secretName: wildcard-dev-tls
  rules:
    - host: argocd.dev.goldenpathidp.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  number: 80
    - host: backstage.dev.goldenpathidp.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: backstage
                port:
                  number: 7007
```

### 2.2 Configure TLS Certificates

**Status**: Exists - Cert-manager installed

```yaml
# gitops/kustomize/base/cert-manager/cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: platform-team@goldenpathidp.io
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: kong
```

---

## Phase 3: Backstage Deployment & Templates (Day 3-4)

### 3.1 Deploy Backstage with Custom Image

**Status**: Partial - Helm chart exists, custom image needed

**Update values**:

```yaml
# gitops/helm/backstage/values/dev.yaml
image:
  repository: <account>.dkr.ecr.eu-west-2.amazonaws.com/goldenpath-backstage
  tag: latest
  pullPolicy: Always

ingress:
  enabled: true
  className: kong
  hosts:
    - host: backstage.dev.goldenpathidp.io
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: backstage-tls
      hosts:
        - backstage.dev.goldenpathidp.io
```

### 3.2 Test Existing Backstage Templates

| Template | Test Case | Expected Outcome |
|----------|-----------|------------------|
| `app-template` | Scaffold stateless app | PR created with app manifests |
| `ecr-request` | Request ECR repo | GitHub workflow triggered, ECR created |
| `eks-request` | Request ephemeral cluster | GitHub workflow triggered |
| `secret-request` | Request secret | Secret created in AWS Secrets Manager |

**Verification Steps**:

```bash
# Access Backstage
open https://backstage.dev.goldenpathidp.io

# Navigate to Create > Templates
# Run each template with test values
```

### 3.3 Create Stateful App Template

**Status**: Gap - Only stateless template exists

**File to Create**:

```yaml
# backstage-helm/backstage-catalog/templates/stateful-app-template.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: stateful-app-template
  title: Create Stateful Application
  description: Scaffold a new stateful application with RDS database
  tags:
    - stateful
    - database
    - rds
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Service Details
      required:
        - name
        - owner
      properties:
        name:
          title: Service Name
          type: string
        owner:
          title: Owner
          type: string
          ui:field: OwnerPicker
    - title: Database Configuration
      required:
        - db_engine
        - db_size
      properties:
        db_engine:
          title: Database Engine
          type: string
          enum: [postgres]
          default: postgres
        db_size:
          title: Instance Size
          type: string
          enum: [small, medium, large, xlarge]
          default: small
        db_name:
          title: Database Name
          type: string
  steps:
    - id: fetch
      name: Fetch Base
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          owner: ${{ parameters.owner }}
    - id: rds-request
      name: Create RDS Request
      action: github:actions:dispatch
      input:
        repoUrl: github.com?owner=mikeybeezy&repo=goldenpath-idp-infra
        workflowId: rds-request-apply.yml
        branchOrTagName: development
        workflowInputs:
          app_name: ${{ parameters.name }}
          db_engine: ${{ parameters.db_engine }}
          db_size: ${{ parameters.db_size }}
          db_name: ${{ parameters.db_name }}
          environment: dev
```

---

## Phase 4: AWS Resource Creation via Backstage (Day 4-5)

### 4.1 Verify ECR Request Flow

**Status**: Exists

```bash
# Test via Backstage UI
# 1. Navigate to Create > ECR Request
# 2. Fill form with test values
# 3. Verify GitHub workflow runs
# 4. Verify ECR repo created in AWS
```

### 4.2 Implement RDS Request Flow

**Status**: Gap - Template exists but workflow incomplete

**Files to Create/Update**:

```yaml
# .github/workflows/rds-request-apply.yml
name: RDS Request Apply
on:
  workflow_dispatch:
    inputs:
      app_name:
        required: true
      db_engine:
        required: true
      db_size:
        required: true
      environment:
        required: true

jobs:
  apply:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create RDS Request File
        run: |
          cat > docs/20-contracts/rds-requests/${{ inputs.app_name }}/RDS-REQUEST.yaml <<EOF
          apiVersion: goldenpath.io/v1
          kind: RDSRequest
          metadata:
            name: ${{ inputs.app_name }}
            owner: ${{ github.actor }}
          spec:
            engine: ${{ inputs.db_engine }}
            size: ${{ inputs.db_size }}
            environment: ${{ inputs.environment }}
          EOF
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
```

### 4.3 Implement S3 Request Flow

**Status**: Exists - Template and workflow in place

Verify end-to-end flow works.

---

## Phase 5: End-to-End Image Deployment (Day 5-6)

### 5.1 Build Pipeline Setup

**Status**: Partial - ECR exists, build workflow needed per app

**Standard Build Workflow**:

```yaml
# Template for app repos: .github/workflows/build-deploy.yml
name: Build and Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and Push
        run: |
          docker build -t $ECR_REPO:${{ github.sha }} .
          docker push $ECR_REPO:${{ github.sha }}

      - name: Update GitOps
        run: |
          # Update image tag in gitops repo
          # ArgoCD Image Updater will auto-sync
```

### 5.2 ArgoCD Image Updater Configuration

**Status**: Exists - Needs per-app annotations

```yaml
# Per-app annotation in ArgoCD Application
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: app=<ecr-repo>
    argocd-image-updater.argoproj.io/app.update-strategy: latest
```

### 5.3 End-to-End Test: Commit to Deploy

| Step | Actor | Outcome |
|------|-------|---------|
| 1. Developer commits code | Developer | Push to main branch |
| 2. GitHub Actions builds image | CI | Image pushed to ECR |
| 3. Image Updater detects new image | ArgoCD | Updates deployment manifest |
| 4. ArgoCD syncs deployment | ArgoCD | New pods deployed |
| 5. Kong routes traffic | Kong | Users see new version |

---

## Phase 6: Custom Backstage Image & Plugins (Day 6-7)

### 6.1 Create Custom Backstage Repository

**Status**: Gap - Completely missing

**Repository Setup**:

```bash
# Create new repo
gh repo create mikeybeezy/goldenpath-backstage --public

# Clone and initialize
npx @backstage/create-app@latest --path goldenpath-backstage
cd goldenpath-backstage

# Add custom plugins
yarn add @backstage/plugin-kubernetes
yarn add @backstage/plugin-techdocs
```

### 6.2 Build Pipeline for Backstage Image

```yaml
# goldenpath-backstage/.github/workflows/build.yml
name: Build Backstage Image
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: Build
        run: yarn build

      - name: Build Docker Image
        run: yarn build-image

      - name: Push to ECR
        if: github.ref == 'refs/heads/main'
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REPO
          docker push $ECR_REPO:${{ github.sha }}
          docker push $ECR_REPO:latest
```

### 6.3 Plugin Development Setup

**Plugins to Build**:

| Plugin | Priority | Description |
|--------|----------|-------------|
| Kong Catalog | High | EC-0003 implementation |
| Cost Dashboard | Medium | AWS cost visibility |
| Platform Health | Medium | Cluster/service health |
| Request Tracker | Low | Track resource requests |

---

## Gap Analysis Summary

| Gap | Severity | Phase | Effort |
|-----|----------|-------|--------|
| Route53 Terraform module | Critical | 0 | 1 day |
| Custom Backstage image repo | Critical | 0 | 1 day |
| Kong ingress for tooling | High | 2 | 0.5 day |
| Stateful app template | High | 3 | 0.5 day |
| RDS request workflow | High | 4 | 1 day |
| End-to-end deploy test | High | 5 | 0.5 day |
| Backstage plugin setup | Medium | 6 | 2 days |
| SSO/OIDC integration | Medium | - | 1 day |
| HA configuration | Low | - | 1 day |
| Monitoring dashboards | Low | - | 1 day |

---

## Suggested Additions Not in Original Request

### 1. Observability Stack Verification

- Prometheus scraping all services
- Grafana dashboards for Kong, ArgoCD, Backstage
- Loki log aggregation
- Alerting rules for critical services

### 2. Security Hardening

- Pod Security Standards enforcement
- Network policies for namespace isolation
- Secret rotation automation
- Image vulnerability scanning gates

### 3. Developer Experience

- Local development environment setup (Kind cluster)
- Service mesh preview (Istio/Linkerd evaluation)
- GitOps PR preview environments
- Documentation portal (TechDocs)

### 4. Cost Management

- AWS Cost Explorer tags alignment
- Per-team cost allocation
- Idle resource detection
- Right-sizing recommendations

---

## Execution Timeline

```
Week 1:
├── Day 1: Phase 0 (Route53 + Backstage repo setup)
├── Day 2: Phase 1 (EKS cluster + bootstrap)
├── Day 3: Phase 2 (Kong ingress configuration)
├── Day 4: Phase 3 (Backstage templates)
└── Day 5: Phase 4 (AWS resource creation)

Week 2:
├── Day 6: Phase 5 (End-to-end deployment)
├── Day 7: Phase 6 (Custom Backstage image)
└── Day 8+: Gap remediation + testing
```

---

**Created**: 2026-01-20
**Author**: platform-team
**Status**: Ready for execution
