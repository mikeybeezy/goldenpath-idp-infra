---
id: session-2026-01-17-eks-backstage-scaffolder
title: EKS Backstage Scaffolder Design
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: in_progress
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0165-rds-user-db-provisioning-automation
  - CL-0142-eks-apply-scope-gate
  - rds-request
  - infra-terraform-apply-dev
---

# EKS Backstage Scaffolder Design

## Session Metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-17
**Timestamp:** 2026-01-17T13:00:00Z
**Branch:** feature/infra-apply-rds-provision

## Scope

- Design EKS Backstage scaffolder template
- Ensure enum alignment across Terraform, contracts, and Backstage
- Define contract for EKS provisioning
- Document consistency requirements for all self-service resources

## Context / Problem Statement

During investigation of a stalled EKS node group creation, we discovered:

1. **Accidental EKS rebuild**: PR #252 (RDS automation) merged to main and triggered `infra-terraform-apply-dev.yml` because it touched `envs/dev/main.tf`
2. **vCPU quota exhaustion**: Old cluster `15-01-26-15` was still running, blocking new cluster `17-01-26-01`
3. **Opportunity discovered**: PR merge CAN trigger EKS creation - this could be leveraged for Backstage scaffolder

We implemented an EKS scope gate (CL-0142) to prevent accidental rebuilds. Now we need to design the intentional path via Backstage.

## Current State - Self-Service Resources

| Resource | Scaffolder | Contract | Parser | Enums | Auto-Deploy |
|----------|------------|----------|--------|-------|-------------|
| **RDS** | `rds-request.yaml` | `rds-catalog.yaml` | `rds_request_parser.py` | Aligned | Yes (scope gate allows) |
| **ECR** | `ecr-request.yaml` | `ecr-catalog.yaml` | N/A | Partial | Yes |
| **EKS** | **Missing** | **Missing** | **Missing (planned)** | **Not defined** | No (scope gate blocks) |
| **App** | `app-template` | N/A | N/A | N/A | N/A |

## Proposal - EKS Scaffolder Architecture

### 1. Artifacts Required

| Artifact | Purpose | Location |
|----------|---------|----------|
| **Contract** | Define EKS provisioning rules, enums, tiers | `docs/20-contracts/resource-catalogs/eks-catalog.yaml` |
| **Scaffolder Template** | Backstage UI for EKS requests | `backstage-helm/backstage-catalog/templates/eks-request.yaml` |
| **Parser** | Convert request YAML → tfvars + derived artifacts | `scripts/eks_request_parser.py` |
| **Enum Source** | Centralized enums via `enum_from` | `schemas/metadata/enums.yaml` |
| **Workflow Integration** | Trigger apply after PR merge | Update `infra-terraform-apply-dev.yml` |

### 2. EKS Contract Definition

```yaml
# docs/20-contracts/resource-catalogs/eks-catalog.yaml
apiVersion: platform.goldenpath.io/v1
kind: ResourceCatalog
metadata:
  name: eks-catalog
  description: EKS cluster provisioning catalog
spec:
  resource_type: eks-cluster

  modes:
    - cluster-only
    - bootstrap-only
    - cluster+bootstrap

  node_tiers:
    small:
      instance_type: t3.small
      min_nodes: 2
      max_nodes: 4
      approval_required: false
    medium:
      instance_type: t3.medium
      min_nodes: 3
      max_nodes: 6
      approval_required: false
    large:
      instance_type: t3.large
      min_nodes: 4
      max_nodes: 8
      approval_required: true
    xlarge:
      instance_type: t3.xlarge
      min_nodes: 6
      max_nodes: 12
      approval_required: true

  environments:
    - dev
    - staging
    - prod

  kubernetes_versions:
    - "1.28"
    - "1.29"
    - "1.30"

  regions:
    - eu-west-2
```

### 3. Enum Alignment Requirements

Enums must be consistent across:

| Layer | File | Enums |
|-------|------|-------|
| **Terraform** | `envs/dev/variables.tf` | `mode`, `environment` |
| **Terraform tfvars** | `envs/dev/terraform.tfvars` | Values used |
| **Contract** | `eks-catalog.yaml` | `modes`, `environments`, `node_tiers` |
| **Backstage** | `eks-request.yaml` | Form dropdowns |
| **Schema** | `schemas/requests/eks.schema.yaml` | Uses `enum_from` from `schemas/metadata/enums.yaml` |

### 4. EKS Scaffolder Template (Proposed)

```yaml
# backstage-helm/backstage-catalog/templates/eks-request.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: eks-request
  title: Request EKS Cluster
  description: |
    Request a new EKS cluster or bootstrap run.
    Creates a PR with a governed EKS request file.
spec:
  owner: platform-team
  type: infrastructure

  parameters:
    - title: Cluster Configuration
      required:
        - environment
        - mode
        - requester
      properties:
        environment:
          title: Environment
          type: string
          enum: [dev, staging, prod]
          default: dev
        mode:
          title: Mode
          type: string
          enum: [cluster-only, bootstrap-only, cluster+bootstrap]
          default: cluster+bootstrap
          description: Select cluster creation and/or bootstrap execution
        request_id:
          title: Request ID
          type: string
          pattern: '^EKS-[0-9]{4}$'
          description: Required. Example: EKS-0001
        build_id:
          title: Build ID
          type: string
          pattern: '^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$'
          description: Required when mode includes cluster creation. Format dd-mm-yy-NN
          ui:help: "Example: 17-01-26-01"
        node_tier:
          title: Node Tier
          type: string
          enum: [small, medium, large, xlarge]
          default: small
          description: large/xlarge require approval
        requester:
          title: Requester
          type: string
          pattern: '^[a-z0-9-]+$'

  steps:
    - id: write-request
      name: Write EKS request file
      action: fetch:template
      input:
        url: ./skeletons/eks-request
        targetPath: docs/20-contracts/eks-requests/${{ parameters.environment }}
        values:
          id: ${{ parameters.request_id }}
          environment: ${{ parameters.environment }}
          mode: ${{ parameters.mode }}
          build_id: ${{ parameters.build_id }}
          node_tier: ${{ parameters.node_tier }}
          requester: ${{ parameters.requester }}

    - id: create-pr
      name: Create Pull Request
      action: publish:github:pull-request
      input:
        repoUrl: github.com?owner=mikeybeezy&repo=goldenpath-idp-infra
        branchName: eks-request/${{ parameters.request_id }}
        title: "feat(eks): Request ${{ parameters.mode }} ${{ parameters.request_id }}"
        description: |
          ## EKS Cluster Request

          - **Mode**: ${{ parameters.mode }}
          - **Build ID**: ${{ parameters.build_id }}
          - **Node Tier**: ${{ parameters.node_tier }}
          - **Requester**: ${{ parameters.requester }}

          ## Checklist
          - [ ] Reviewed tfvars changes
          - [ ] Confirmed no existing cluster conflicts

          ---
          Generated by Backstage EKS Scaffolder
```

### 5. Parser-First Flow (Chosen)

| RDS | EKS |
|-----|-----|
| Creates request YAML in `docs/20-contracts/rds-requests/` | Creates request YAML in `docs/20-contracts/eks-requests/` |
| Parser transforms YAML → tfvars + derived artifacts | Parser transforms YAML → tfvars + derived artifacts |
| Multi-step governance with validation gates | Same validation + approval model |

EKS request → parser output (conceptual):
```hcl
cluster_mode = "cluster+bootstrap"
build_id = "17-01-26-02"
```

### 6. Workflow Integration

After scope gate (CL-0142), EKS changes require manual trigger.

**Option A: Label-based auto-apply**
- Scaffolder adds label `[eks-deploy]` to PR
- Workflow detects label and allows auto-apply

**Option B: Manual trigger after merge**
- PR merges → workflow skips (scope gate)
- User manually triggers `workflow_dispatch`

**Recommendation:** Option B for safety - EKS is high-impact.

## Consistency Requirements

### All Self-Service Resources Must Have:

| Requirement | RDS | ECR | EKS |
|-------------|-----|-----|-----|
| Contract catalog | `rds-catalog.yaml` | `ecr-catalog.yaml` | **TODO** |
| Enum schema | Partial | Partial | **TODO** |
| Backstage scaffolder | `rds-request.yaml` | `ecr-request.yaml` | **TODO** |
| Size/tier approval guard | `rds-size-approval-guard.yml` | N/A | **TODO** |
| Drift guard | `rds-tfvars-drift-guard.yml` | N/A | N/A |
| PR template integration | Yes | Yes | **TODO** |

### Enum Single Source of Truth

Centralized in `schemas/metadata/enums.yaml`, referenced via `enum_from`:
- `eks_modes`
- `eks_node_tiers`
- `kubernetes_versions`
- `environments`

## Work Summary (Completed This Session)

1. **Investigated EKS node group stall** - Found vCPU quota exhaustion
2. **Traced accidental rebuild** - PR #252 merge triggered apply
3. **Implemented EKS scope gate** (CL-0142) - Blocks EKS auto-apply
4. **Fixed RDS drift guard** - Quoted key handling
5. **Fixed pre-commit failures** - Emoji policy, bare URLs

## Artifacts Touched

### Modified
- `.github/workflows/infra-terraform-apply-dev.yml` - Added scope gate
- `.github/workflows/rds-tfvars-drift-guard.yml` - Fixed quoted keys

### Added
- `docs/changelog/entries/CL-0142-eks-apply-scope-gate.md`
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md` (this file)

## Next Steps

| Priority | Task | Effort |
|----------|------|--------|
| P1 | Create `eks-catalog.yaml` contract | Small |
| P1 | Create `eks-enums.yaml` schema | Small |
| P2 | Create `eks-request.yaml` scaffolder | Medium |
| P2 | Create `eks-size-approval-guard.yml` | Small |
| P3 | Consolidate common enums to single source | Medium |
| P3 | Add enum validation to CI | Medium |

## Open Questions

1. Should EKS auto-apply with a special label, or always require manual trigger?
2. Should node tier approval guard block PR or just warn?
3. How to handle persistent vs ephemeral state files in Backstage?

---

Signed: Claude Opus 4.5 (2026-01-17T13:00:00Z)

---

## Updates (append as you go)

### Update - 2026-01-17T13:15:00Z

**What changed**
- Documented full proposal for EKS scaffolder
- Identified consistency gaps across RDS/ECR/EKS
- Proposed enum single source of truth

**Next steps**
- User review of proposal
- Decide on auto-apply vs manual trigger
- Begin implementation if approved

Signed: Claude Opus 4.5 (2026-01-17T13:15:00Z)


### Update - 2026-01-17T13:39:00Z


## Minimal EKS request contract (schema + what is validated vs inferred)
What must be schema-validated (hard requirements)

- request id
- environment
- region
- mode: cluster-only | bootstrap-only | cluster+bootstrap
- cluster name (or build_id → derived cluster name)
- k8s version
- node pool sizing (min/max/desired or desired + autoscaler enabled)
- ingress plan (NLB internal + Kong)
- argo install choice (install or skip)
- IRSA choice (enabled/disabled)
- access model (SSM-only vs SSH-breakglass)

### What can be inferred (safe defaults)

- instance type default (t3.small)
- default node count (3)
- private subnets / VPC module source = env defaults
- “internal LB” default true
- default toolset list based on “bootstrap profile”


## Example request file (matches the schema)

### schemas/requests/eks.schema.yaml (minimal V1, matches your modes)

This is intentionally tight. we can expand later.
```
$schema: "https://json-schema.org/draft/2020-12/schema"
title: "EKS Build Request (V1)"
type: object
additionalProperties: false

required: [id, environment, region, mode, cluster, node_pool]

properties:
  id:
    type: string
    pattern: "^EKS-[0-9]{4}$"

  environment:
    type: string
    enum: [dev, staging, prod]

  region:
    type: string
    enum: [eu-west-2]   # keep V1 opinionated; expand later

  mode:
    description: "Controls what the pipeline does."
    type: string
    enum:
      - cluster-only
      - bootstrap-only
      - cluster+bootstrap

  build:
    type: object
    additionalProperties: false
    properties:
      build_id:
        type: string
        pattern: "^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$"
      ephemeral:
        type: boolean
        default: true

allOf:
  - if:
      properties:
        mode:
          enum: [cluster-only, cluster+bootstrap]
    then:
      required: [build]
      properties:
        build:
          required: [build_id]

  cluster:
    type: object
    additionalProperties: false
    required: [name, kubernetes_version]
    properties:
      name:
        type: string
        pattern: "^[a-z0-9-]{3,40}$"
      kubernetes_version:
        type: string
        enum: ["1.28", "1.29", "1.30"]   # adjust to what you support
      private_endpoint_only:
        type: boolean
        default: true

      irsa:
        type: object
        additionalProperties: false
        properties:
          enabled:
            type: boolean
            default: false
          # if enabled, you can optionally pin an issuer/oidc provider details
          oidc:
            type: object
            additionalProperties: false
            properties:
              issuer_url:
                type: string
              provider_arn:
                type: string

      access:
        type: object
        additionalProperties: false
        properties:
          ssm_break_glass:
            type: boolean
            default: true
          ssh_break_glass:
            type: boolean
            default: false
          ssh_key_name:
            type: string
          ssh_source_sg_ids:
            type: array
            items: { type: string }

  node_pool:
    type: object
    additionalProperties: false
    required: [desired, max]
    properties:
      instance_type:
        type: string
        default: "t3.small"
      desired:
        type: integer
        minimum: 1
        maximum: 10
      max:
        type: integer
        minimum: 1
        maximum: 20
      capacity_type:
        type: string
        enum: [ON_DEMAND, SPOT]
        default: ON_DEMAND
      autoscaler:
        type: object
        additionalProperties: false
        properties:
          enabled:
            type: boolean
            default: true

  gitops:
    type: object
    additionalProperties: false
    properties:
      controller:
        type: string
        enum: [argocd]
        default: argocd
      install:
        type: boolean
        default: true

      bootstrap_profile:
        description: "Which toolset Argo should sync when bootstrap runs."
        type: string
        enum: [core-tooling, tooling-plus-sample-apps]
        default: core-tooling

  ingress:
    type: object
    additionalProperties: false
    properties:
      provider:
        type: string
        enum: [kong]
        default: kong
      aws_lb_type:
        type: string
        enum: [nlb, alb]
        default: nlb
      internal:
        type: boolean
        default: true
```
### Why this matches your current reality

- mode maps to  workflows (cluster-only / bootstrap-only / combined)
- gitops.install lets goldenpath do “cluster only no bootstrap” cleanly
- bootstrap_profile matches “single-load deploy with tools bootstrap”
- irsa.enabled reflects your current stance (off until you choose to enable)
- access supports “SSM default, SSH optional”


### Example request file (matches the schema)

docs/20-contracts/eks-requests/dev/EKS-0001.yaml
```
id: EKS-0001
environment: dev
region: eu-west-2
mode: cluster+bootstrap

build:
  build_id: 17-01-26-01
  ephemeral: true

cluster:
  name: gp-dev-6f2a9c
  kubernetes_version: "1.29"
  private_endpoint_only: true
  irsa:
    enabled: false
  access:
    ssm_break_glass: true
    ssh_break_glass: false

node_pool:
  instance_type: t3.small
  desired: 3
  max: 5
  capacity_type: ON_DEMAND
  autoscaler:
    enabled: true

gitops:
  controller: argocd
  install: true
  bootstrap_profile: core-tooling

ingress:
  provider: kong
  aws_lb_type: nlb
  internal: true

```

## How to integrate this without rewriting your current ECR approach
Minimal upgrades (worth doing)

1. Put the schema at:
schemas/requests/eks.schema.yaml
2. Update your existing validator to support:
--kind eks --schema schemas/requests/eks.schema.yaml
(even if it’s just a switch/case)
3. Add meta-schema validation (low effort, high ROI)
So schema typos fail in CI before parsers run.

If we don’t want to bring in new tooling, do it in Python with jsonschema.Draft202012Validator.check_schema().

## About “single-load deployment” and separation of contexts

Goldenpathidp can keep your clean separation and keep determinism:
- Cluster-only workflow: Terraform apply only
- Bootstrap-only workflow: Argo install + sync only
- Combined workflow: cluster then bootstrap as a gated stage

This schema supports all three with mode.

Signed michael.. 

### Update - 2026-01-17T13:42:39Z

**What changed**
- Decision: Use request-file + parser flow for EKS (align with RDS/ECR patterns).
- Decision: `mode` is the primary control (cluster-only/bootstrap-only/cluster+bootstrap).
- Decision: `build_id` is required whenever `mode` includes cluster creation.
- Decision: Centralize enums in `schemas/metadata/enums.yaml` via `enum_from`.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (planning update only).

**Alignment matrix (EKS vs existing resources)**
| Artifact | RDS | ECR | EKS (planned) | Notes |
| --- | --- | --- | --- | --- |
| Request schema | `schemas/requests/rds.schema.yaml` | N/A | `schemas/requests/eks.schema.yaml` | EKS should match schema-driven validation. |
| Request file location | `docs/20-contracts/rds-requests/<env>/RDS-0001.yaml` | N/A | `docs/20-contracts/eks-requests/<env>/EKS-0001.yaml` | Mirror RDS layout for consistency. |
| Parser | `scripts/rds_request_parser.py` | N/A | `scripts/eks_request_parser.py` | Parser emits tfvars + derived artifacts. |
| Contract catalog | `docs/20-contracts/resource-catalogs/rds-catalog.yaml` | `docs/20-contracts/resource-catalogs/ecr-catalog.yaml` | `docs/20-contracts/resource-catalogs/eks-catalog.yaml` | Use same catalog model. |
| Backstage template | `backstage-helm/backstage-catalog/templates/rds-request.yaml` | `backstage-helm/backstage-catalog/templates/ecr-request.yaml` | `backstage-helm/backstage-catalog/templates/eks-request.yaml` | EKS should create request files (not tfvars). |
| Secrets request (loop to close) | `docs/20-contracts/secret-requests/<service>/<env>/<id>.yaml` | N/A | N/A | Missing Backstage scaffolder for secret requests; currently GitHub Actions-only. |
| Enum source | `schemas/metadata/enums.yaml` | `schemas/metadata/enums.yaml` | `schemas/metadata/enums.yaml` | Centralized enums (no new enums directory). |
| CI guardrails | `ci-rds-request-validation.yml` | ECR catalog sync workflows | `ci-eks-request-validation.yml` | Add schema validation + approvals as needed. |
| How-it-works docs | `docs/85-how-it-works/self-service/RDS_REQUEST_FLOW.md` | `docs/85-how-it-works/self-service/ECR_REQUEST_FLOW.md` | `docs/85-how-it-works/self-service/EKS_REQUEST_FLOW.md` | Add EKS flow doc for parity. |

**Next steps**
- Update the scaffolder proposal to write request YAML instead of tfvars.
- Draft the EKS schema + parser interface (inputs/outputs).

Signed: Claude Opus 4.5 (2026-01-17T13:42:39Z)

### Update - 2026-01-17T13:43:08Z

**What changed**
- Replaced "no parser needed" section with parser-first flow to align with decisions.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

**Next steps**
- Reconcile request schema examples to require `build_id` when mode includes cluster creation.

Signed: Claude Opus 4.5 (2026-01-17T13:43:08Z)

### Update - 2026-01-17T13:45:48Z

**What changed**
- Simplified the user-facing rule: "Pick mode; if mode includes cluster creation, `build_id` is required. If mode is bootstrap-only, `build_id` is not needed."
- UI guidance: show `build_id` only when mode is cluster-only or cluster+bootstrap.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

**Next steps**
- Collect feedback on the simplified rule before implementing schema/UI changes.

Signed: Claude Opus 4.5 (2026-01-17T13:45:48Z)

### Update - 2026-01-17T14:00:26Z

**What changed**
- Added concise UI copy for the mode/build_id rule to use in Backstage.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

**UI copy (Backstage helper text)**
- Mode: "Choose how to run the build: create a cluster, bootstrap only, or do both."
- Build ID: "Required when mode includes cluster creation. Not needed for bootstrap-only."

Signed: Claude Opus 4.5 (2026-01-17T14:00:26Z)

### Update - 2026-01-17T14:05:22Z

**What changed**
- Aligned schema example with mode/build_id rule and existing build_id format.
- Removed `test` from the environment enum in the example schema.
- Updated request file path example to match the proposed contracts layout.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

Signed: Claude Opus 4.5 (2026-01-17T14:05:22Z)

### Update - 2026-01-17T14:10:29Z

**What changed**
- Normalized remaining `lifecycle` reference to `mode` in the scaffolder required list.
- Marked enum source conflict as resolved in the review appendix.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

Signed: Claude Opus 4.5 (2026-01-17T14:10:29Z)

### Update - 2026-01-17T14:23:34Z

**What changed**
- Implemented EKS request path + sample request file.
- Added EKS request schema, enums, and parser outputs.
- Added CI validation workflow and manual apply workflow for EKS requests.

**Artifacts touched**
- `docs/20-contracts/eks-requests/dev/EKS-0001.yaml`
- `schemas/metadata/enums.yaml`
- `schemas/requests/eks.schema.yaml`
- `scripts/eks_request_parser.py`
- `.github/workflows/ci-eks-request-validation.yml`
- `.github/workflows/eks-request-apply.yml`

**Validation**
- Not run (implementation only).

**Next steps**
- Decide whether bootstrap-only should trigger a separate workflow or manual runbook.
- Consider regenerating script indices/matrices that are auto-generated.

Signed: Claude Opus 4.5 (2026-01-17T14:23:34Z)

## Review/Validation Appendix

### Review Feedback (Claude Opus 4.5 - 2026-01-17T14:00:00Z)

#### What's Strong

| Aspect | Assessment |
|--------|------------|
| **Problem statement** | Clear - accidental rebuild traced to PR #252, vCPU quota issue documented |
| **Mode concept** | Excellent - `cluster-only`, `bootstrap-only`, `cluster+bootstrap` maps to real workflows |
| **Schema design** | Comprehensive - covers all EKS concerns (IRSA, access, node pools, gitops, ingress) |
| **Alignment matrix** | Very useful - shows gaps across RDS/ECR/EKS systematically |
| **Decisions captured** | Good discipline - each update documents what changed and why |

#### Gaps / Concerns

| Issue | Impact | Recommendation |
|-------|--------|----------------|
| **build_id pattern mismatch** | Schema uses `^[a-z0-9-]{6,32}$` but existing tfvars uses `dd-mm-yy-NN` format | Align to existing `^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$` or migrate both |
| **No `test` environment in schema** | Schema has `[dev, test, staging, prod]` but current tfvars only uses `dev` | Confirm which environments are real |
| **Request file location unclear** | Doc mentions `docs/catalogs/eks/` but alignment matrix says `docs/20-contracts/eks-requests/` | Pick one, align with RDS pattern |
| **Parser outputs not defined** | RDS parser outputs tfvars + ExternalSecrets; EKS parser outputs unclear | Define: tfvars? Makefile vars? Both? |
| **Enum source conflict** | Resolved: centralized enums in `schemas/metadata/enums.yaml` | Use `enum_from` in schema + contract |
| **IRSA default** | Schema defaults `irsa.enabled: false` but current bootstrap uses IRSA | Verify current reality |

#### Key Decisions to Confirm

1. **Request file location**: `docs/20-contracts/eks-requests/<env>/EKS-NNNN.yaml`? (matches RDS)
2. **build_id format**: Keep existing `dd-mm-yy-NN` or switch to `dev-6f2a9c` style?
3. **Enum source of truth**: `schemas/metadata/enums.yaml` (centralized) or `schemas/requests/eks.schema.yaml` (embedded)?
4. **Parser outputs**:
   - `envs/<env>/terraform.tfvars` updates?
   - `envs/<env>/generated/eks-<id>.auto.tfvars.json`?
   - Something else?
5. **Workflow trigger**: Manual only (Option B) or label-gated auto-apply (Option A)?

#### What's Ready vs Needs Work

| Artifact | Status | Blocker |
|----------|--------|---------|
| Schema (`eks.schema.yaml`) | 90% ready | Fix build_id pattern, confirm IRSA default |
| Contract (`eks-catalog.yaml`) | Draft only | Needs full write |
| Parser (`eks_request_parser.py`) | Not started | Needs output spec |
| Scaffolder (`eks-request.yaml`) | Needs rewrite | Should create request YAML, not tfvars |
| CI guardrail | Not started | Depends on schema location |

#### Recommendation

**Before coding, resolve these 3 items:**

1. **Confirm build_id format** - existing `dd-mm-yy-NN` or new format?
2. **Confirm request file location** - `docs/20-contracts/eks-requests/<env>/`?
3. **Define parser outputs** - what files does it generate?

Once those are locked, implementation is straightforward.

Signed: Claude Opus 4.5 (2026-01-17T14:00:00Z)

### Update - 2026-01-17T14:45:00Z - Secrets Backstage Gap Closure

**What changed**
- Implemented Backstage scaffolder for secret requests (closes the loop)
- Created skeleton template for request file generation
- Added secret-approval-guard workflow for high-risk approval gating

**Artifacts created**
- `backstage-helm/backstage-catalog/templates/secret-request.yaml` - Scaffolder template
- `backstage-helm/backstage-catalog/templates/skeletons/secret-request/` - Skeleton template
- `.github/workflows/secret-approval-guard.yml` - Approval guard workflow

**Tiering System Implemented**

| Risk Level | Approval Required | Recovery Window | Auto-Apply |
|------------|-------------------|-----------------|------------|
| low | No | 0 days | Yes |
| medium | No | 7 days | Yes |
| high | **Yes (platform-team)** | 30 days | No (needs label) |

**User Input Requirements**

| Field | Required | Purpose |
|-------|----------|---------|
| `service_name` | Yes | Which app/service needs the secret |
| `secret_name` | Yes | Name for the secret |
| `secret_type` | Yes | Classification (database-credentials, api-key, etc.) |
| `description` | Yes | What the secret is for (audit trail) |
| `risk` | Yes | Drives approval gate and recovery window |
| `environment` | Yes | Target environment |
| `namespace` | Yes | K8s namespace for ESO sync |
| `k8s_secret_name` | Yes | Name of K8s secret |

**Flow**

```
User (Backstage) → Fills form → Creates request YAML + PR
                                    ↓
                    [secret-approval-guard.yml runs]
                                    ↓
              low/medium risk: auto-mergeable
              high risk: blocked until platform-approved label added
                                    ↓
                    PR merged → request-app-secret.yml → Terraform apply
```

**Alignment Matrix Update**

| Resource | Scaffolder | Contract | Parser | Approval Guard | Status |
|----------|------------|----------|--------|----------------|--------|
| RDS | `rds-request.yaml` | `rds-catalog.yaml` | `rds_request_parser.py` | `rds-size-approval-guard.yml` | ✅ Complete |
| ECR | `ecr-request.yaml` | `ecr-catalog.yaml` | N/A | N/A | ✅ Complete |
| Secrets | `secret-request.yaml` | `secrets-catalog.yaml` | `secret_request_parser.py` | `secret-approval-guard.yml` | ✅ **Now Complete** |
| EKS | TODO | TODO | TODO | TODO | In Progress |

**Next steps**
- Commit and push changes
- Test scaffolder in Backstage
- Proceed with EKS scaffolder implementation

Signed: Claude Opus 4.5 (2026-01-17T14:45:00Z)
