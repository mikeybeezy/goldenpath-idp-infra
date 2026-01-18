---
id: EC-0007-kpack-buildpacks-integration
title: kpack and Cloud Native Buildpacks Integration
type: extension_capability
status: proposed
owner: platform-team
domain: platform-core
relates_to:
  - EC-0006-competitor-analysis-tap
  - EC-0005-kubernetes-operator-framework
  - ADR-0148-seamless-build-deployment-with-immutability
  - INDEX
priority: high
vq_class: velocity
estimated_roi: $20K/year
effort_estimate: 4-6 weeks
---

## Executive Summary

kpack is a Kubernetes-native build service that automatically creates OCI container images from source code using Cloud Native Buildpacks. This eliminates the need for developers to write Dockerfiles, enabling a `cf push`-style experience where developers simply push code and the platform handles containerization.

**Key Benefits**:
- Zero-Dockerfile deployments for supported languages
- Automatic base image updates (CVE patching)
- Consistent, reproducible builds
- Kubernetes-native reconciliation (fits EC-0005 vision)

**Estimated ROI**: $20K/year from reduced Dockerfile maintenance, faster onboarding, and automated security patching.

## Problem Statement

### Current Developer Experience

```text
Developer Journey Today:
1. Write application code
2. Write/maintain Dockerfile          ← Friction
3. Debug Docker build issues          ← Friction
4. Push to ECR via GitHub Actions
5. Update Kubernetes manifests
6. Wait for ArgoCD sync
```

### Pain Points

1. **Dockerfile Expertise Required**: Not all developers know Docker best practices
2. **Inconsistent Base Images**: Each team picks their own, leading to sprawl
3. **Security Patching Lag**: When base images have CVEs, manual rebuilds required
4. **Build Debugging**: "Works on my machine" Docker issues waste time
5. **Onboarding Friction**: New apps need Dockerfile boilerplate

### Current Metrics (Estimated)

| Metric | Current State |
|--------|---------------|
| Time to first deployment (new app) | 2-4 hours |
| Dockerfile-related support tickets | 5-10/month |
| Base image CVE patch time | Days to weeks |
| Docker build failures in CI | ~15% of builds |

## Proposed Solution

### What is kpack?

kpack is the open-source core of Tanzu Build Service. It runs on Kubernetes and watches for source code changes, automatically building container images using Cloud Native Buildpacks.

### How It Works

```text
┌─────────────────────────────────────────────────────────────────┐
│                        kpack Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐     ┌──────────────┐     ┌──────────────┐        │
│   │   Git    │────▶│  kpack       │────▶│    ECR       │        │
│   │  Repo    │     │  Controller  │     │   Registry   │        │
│   └──────────┘     └──────┬───────┘     └──────────────┘        │
│                          │                                       │
│                          ▼                                       │
│                   ┌──────────────┐                               │
│                   │ ClusterBuilder│                              │
│                   │  (Buildpacks) │                              │
│                   └──────────────┘                               │
│                          │                                       │
│        ┌─────────────────┼─────────────────┐                    │
│        ▼                 ▼                 ▼                    │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                │
│   │  Java   │      │  Node   │      │ Python  │                │
│   │Buildpack│      │Buildpack│      │Buildpack│                │
│   └─────────┘      └─────────┘      └─────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Developer Experience with kpack

```text
Developer Journey with kpack:
1. Write application code
2. git push                           ← That's it!
3. kpack detects, builds, pushes
4. ArgoCD deploys new image
```

### Key Resources

**ClusterBuilder** - Defines available buildpacks:

```yaml
apiVersion: kpack.io/v1alpha2
kind: ClusterBuilder
metadata:
  name: default
spec:
  tag: <ECR_REPO>/builder:default
  stack:
    name: base
    kind: ClusterStack
  order:
    - group:
        - id: paketo-buildpacks/java
        - id: paketo-buildpacks/nodejs
        - id: paketo-buildpacks/python
        - id: paketo-buildpacks/go
```

**Image** - Per-application build definition:

```yaml
apiVersion: kpack.io/v1alpha2
kind: Image
metadata:
  name: payments-api
  namespace: apps
spec:
  tag: <ECR_REPO>/payments-api
  source:
    git:
      url: https://github.com/org/payments-api
      revision: main
  builder:
    name: default
    kind: ClusterBuilder
```

## Integration with GoldenPath

### Proposed Flow

```text
┌─────────────────────────────────────────────────────────────────┐
│                  GoldenPath + kpack Integration                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Backstage                                                       │
│  ┌─────────────────┐                                            │
│  │ "Deploy App"    │                                            │
│  │  Scaffolder     │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐     ┌─────────────────┐                    │
│  │  App Contract   │────▶│  GitHub Actions │                    │
│  │  (YAML in git)  │     │  (Validation)   │                    │
│  └─────────────────┘     └────────┬────────┘                    │
│                                   │                              │
│           ┌───────────────────────┴───────────────────┐         │
│           ▼                                           ▼         │
│  ┌─────────────────┐                        ┌─────────────────┐ │
│  │  kpack Image CR │                        │  ArgoCD App CR  │ │
│  │  (Build config) │                        │  (Deploy config)│ │
│  └────────┬────────┘                        └────────┬────────┘ │
│           │                                          │          │
│           ▼                                          ▼          │
│  ┌─────────────────┐                        ┌─────────────────┐ │
│  │  kpack builds   │───────────────────────▶│  ArgoCD syncs   │ │
│  │  pushes to ECR  │      (image ready)     │  to EKS cluster │ │
│  └─────────────────┘                        └─────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### New Contract Type: AppDeployment

```yaml
apiVersion: goldenpath.io/v1
kind: AppDeploymentRequest
id: APP-0001
environment: dev
owner: payments-team
application: payments-api

spec:
  source:
    git:
      url: https://github.com/org/payments-api
      branch: main

  build:
    type: buildpack  # or "dockerfile" for opt-out
    builder: default

  runtime:
    replicas: 2
    resources:
      memory: 512Mi
      cpu: 250m

  ingress:
    enabled: true
    host: payments-api.dev.goldenpath.io

  bindings:
    - type: database
      name: payments-db  # References RDS-0001
```

### Backstage Template

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: deploy-app
  title: Deploy Application
spec:
  parameters:
    - title: Application Details
      properties:
        appName:
          title: Application Name
          type: string
        gitRepo:
          title: Git Repository URL
          type: string
        environment:
          title: Environment
          type: string
          enum: [dev, test, staging, prod]
        buildType:
          title: Build Type
          type: string
          enum: [buildpack, dockerfile]
          default: buildpack

  steps:
    - id: generate-contract
      name: Generate App Contract
      action: fetch:template
      input:
        url: ./skeletons/app-deployment
        values:
          appName: ${{ parameters.appName }}
          gitRepo: ${{ parameters.gitRepo }}
          environment: ${{ parameters.environment }}
          buildType: ${{ parameters.buildType }}

    - id: create-pr
      name: Create Pull Request
      action: publish:github:pull-request
```

## Implementation Roadmap

### Phase 1: kpack Installation (Week 1-2)

**Deliverables**:
- Install kpack controller on EKS clusters
- Configure ECR authentication
- Create base ClusterStack and ClusterBuilder
- Test with sample Java/Node apps

**Tasks**:
```bash
# Install kpack
kubectl apply -f https://github.com/buildpacks-community/kpack/releases/download/v0.13.0/release.yaml

# Configure ECR secret
kubectl create secret docker-registry ecr-creds \
  --docker-server=$AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password)
```

### Phase 2: Builder Configuration (Week 2-3)

**Deliverables**:
- ClusterStack with approved base images
- ClusterBuilder with language buildpacks (Java, Node, Python, Go)
- Automated builder updates via kpack

**Language Support Matrix**:

| Language | Buildpack | Auto-detect |
|----------|-----------|-------------|
| Java (Maven/Gradle) | paketo-buildpacks/java | Yes |
| Node.js | paketo-buildpacks/nodejs | Yes |
| Python | paketo-buildpacks/python | Yes |
| Go | paketo-buildpacks/go | Yes |
| .NET Core | paketo-buildpacks/dotnet-core | Yes |
| Ruby | paketo-buildpacks/ruby | Yes |

### Phase 3: GoldenPath Integration (Week 3-5)

**Deliverables**:
- AppDeploymentRequest schema
- app_deployment_parser.py script
- CI validation workflow
- Backstage "Deploy App" template

**New Files**:
```text
schemas/requests/app-deployment.schema.yaml
scripts/app_deployment_parser.py
.github/workflows/ci-app-deployment-validation.yml
.github/workflows/app-deployment-apply.yml
backstage-helm/backstage-catalog/templates/app-deployment.yaml
docs/20-contracts/app-deployments/{env}/*.yaml
```

### Phase 4: Documentation and Rollout (Week 5-6)

**Deliverables**:
- How-it-works documentation
- Runbook for kpack operations
- Developer onboarding guide
- Pilot with 2-3 application teams

## Supported Languages and Detection

kpack uses Paketo Buildpacks which auto-detect based on project files:

| Language | Detection Files |
|----------|-----------------|
| Java | pom.xml, build.gradle |
| Node.js | package.json |
| Python | requirements.txt, Pipfile, setup.py |
| Go | go.mod |
| .NET | *.csproj, *.fsproj |
| Ruby | Gemfile |

## Automatic Base Image Updates

One of kpack's killer features - when base images are updated (e.g., security patches), all apps are automatically rebuilt:

```text
CVE detected in base image
         ↓
Platform team updates ClusterStack
         ↓
kpack detects stack change
         ↓
All Image resources automatically rebuild
         ↓
New images pushed to ECR
         ↓
ArgoCD syncs updated deployments
         ↓
Zero developer intervention required
```

## Cost Analysis

### Implementation Costs

| Item | Cost |
|------|------|
| Platform team effort (6 weeks) | $30,000 |
| kpack compute overhead | ~$200/month |
| Training and documentation | $2,000 |
| **Total First Year** | **$34,400** |

### Annual Savings

| Category | Savings |
|----------|---------|
| Reduced Dockerfile support tickets | $8,000 |
| Faster developer onboarding | $6,000 |
| Automated CVE patching | $4,000 |
| Consistent builds (fewer failures) | $5,000 |
| **Total Annual Savings** | **$23,000** |

### ROI Calculation

- **Year 1**: -$11,400 (investment)
- **Year 2+**: +$20,600/year net savings
- **Break-even**: ~18 months

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Buildpack doesn't support custom build | Medium | Medium | Allow Dockerfile fallback option |
| kpack controller stability | Low | High | Run in HA mode, monitor closely |
| ECR rate limits during mass rebuild | Medium | Medium | Stagger rebuilds, use pull-through cache |
| Developer resistance to change | Medium | Low | Gradual rollout, maintain Dockerfile option |
| Build times slower than Docker | Low | Low | Leverage kpack caching, benchmark first |

## Alternatives Considered

### Option A: Continue with Dockerfiles Only

**Pros**: No new tooling, developers familiar
**Cons**: Manual CVE patching, inconsistent builds, expertise barrier
**Verdict**: Rejected - doesn't solve core problems

### Option B: GitHub Actions with Buildpacks

**Pros**: No cluster-side components
**Cons**: No automatic rebuilds, imperative not declarative
**Verdict**: Partial - could be stepping stone

### Option C: Tanzu Build Service (Enterprise kpack)

**Pros**: VMware support, additional features
**Cons**: Licensing cost ($50K+/year)
**Verdict**: Rejected - kpack provides 90% of value at $0 cost

### Option D: kpack (Chosen)

**Pros**: Free, Kubernetes-native, automatic rebuilds, active community
**Cons**: Requires cluster resources, learning curve
**Verdict**: Selected - best balance of capability and cost

## Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| New app deployment time | 2-4 hours | < 30 min | 3 months |
| Dockerfile support tickets | 5-10/month | < 2/month | 3 months |
| CVE patch deployment time | Days | Hours (automatic) | Immediate |
| Docker build failures | 15% | < 5% | 3 months |
| Apps using buildpacks | 0% | 50% | 6 months |

## Monitoring and Observability

### kpack Metrics to Track

```yaml
# Prometheus metrics exposed by kpack
- kpack_build_duration_seconds
- kpack_build_status (success/failure)
- kpack_image_rebuilds_total
- kpack_builder_ready
```

### Alerts

```yaml
- alert: KpackBuildFailed
  expr: kpack_build_status{status="failed"} > 0
  for: 5m
  annotations:
    summary: "kpack build failed for {{ $labels.image }}"

- alert: KpackBuilderNotReady
  expr: kpack_builder_ready == 0
  for: 10m
  annotations:
    summary: "kpack ClusterBuilder not ready"
```

## Conclusion

kpack integration addresses a key gap identified in EC-0006 (TAP comparison) - the lack of zero-Dockerfile builds. It provides:

1. **Developer Velocity**: Simpler path to production
2. **Security**: Automatic base image patching
3. **Consistency**: Standardized builds across all apps
4. **Kubernetes-Native**: Fits EC-0005 operator vision

**Recommendation**: Proceed with implementation, starting with Phase 1 on dev cluster.

---

## References

- [kpack GitHub](https://github.com/buildpacks-community/kpack)
- [Paketo Buildpacks](https://paketo.io/)
- [Cloud Native Buildpacks](https://buildpacks.io/)
- [EC-0006: TAP Competitor Analysis](EC-0006-competitor-analysis-tap.md)

---

**Created**: 2026-01-18
**Author**: platform-team
**Last Updated**: 2026-01-18
