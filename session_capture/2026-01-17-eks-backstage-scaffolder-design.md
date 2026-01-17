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

### Update - 2026-01-17T14:54:14Z

**What changed**
- Captured the implementation status and current git working set.

**Artifacts touched**
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

**Current state**
- New EKS request artifacts are in place (schema, parser, workflows, sample request).
- Existing local changes also include unrelated files: `docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md`, `envs/dev/README.md`, `envs/dev/terraform.tfvars`.

**Next steps**
- Decide whether to include unrelated files in the same commit or split.

Signed: Claude Opus 4.5 (2026-01-17T14:54:14Z)

### Update - 2026-01-17T15:29:02Z

**What changed**
- Parameterized EKS apply workflow by environment/region and added non-dev approval guard.
- Aligned parser outputs to mode (apply_kubernetes_addons toggled by mode+gitops_install).
- Marked advisory fields in schema and emitted warnings for non-wired settings.

**Artifacts touched**
- `.github/workflows/eks-request-apply.yml`
- `scripts/eks_request_parser.py`
- `schemas/requests/eks.schema.yaml`
- `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`

**Validation**
- Not run (doc update only).

Signed: Claude Opus 4.5 (2026-01-17T15:29:02Z)

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

### Review Feedback: EKS Request Parser & Workflows (Claude Opus 4.5 - 2026-01-17T15:10:00Z)

#### `scripts/eks_request_parser.py`

**What's Strong**

| Aspect | Assessment |
|--------|------------|
| Metadata header | Follows SCRIPT-0043 pattern with dry-run, test, risk profile |
| Dataclass usage | Clean, type-annotated `EksRequest` with frozen=True for immutability |
| Flexible field parsing | Handles multiple field name variants (e.g., `node_pool.tier` OR `node_pool.node_tier`) |
| Validation logic | Good - checks required fields, min/desired/max ordering, enum enforcement |
| Mode handling | Correctly requires `build_id` only for cluster-creating modes |
| Enum-based validation | Loads from centralized `schemas/metadata/enums.yaml` - good alignment |

**Issues and Gaps**

| Issue | Line(s) | Impact | Recommendation |
|-------|---------|--------|----------------|
| No schema validation | - | Parser does validation manually; no JSON Schema validation | Consider adding `jsonschema` validation as a first pass before parsing |
| Output path mismatch | 249-256 | `envs/<env>/clusters/generated/<id>.auto.tfvars.json` but Terraform expects files in `envs/<env>/` | Verify Terraform reads from `clusters/generated/` subdirectory |
| Missing gitops/ingress in tfvars | 259-286 | `gitops_*`, `ingress_*`, `irsa_enabled`, `ssm_break_glass` parsed but not in output | Either include these in tfvars or document they're for validation-only |
| No audit record | - | Unlike RDS parser, no audit trail output | Consider adding `--audit-file` for governance alignment |
| `owner` enum check | 110, 246 | Uses `owners` from enums but RDS uses `owner` | Potential inconsistency - verify enum key naming |
| No `--verbose` flag | - | Hard to debug failures | Add verbose mode for troubleshooting |

**Code Quality Notes**

- Line 63: `build_id: str` - should this be `Optional[str]` since bootstrap-only doesn't need it?
- Line 183-185: Good defensive casting to `int` with sensible default for `node_min`
- Line 323-326: Good guard against generating tfvars for bootstrap-only mode

---

#### `.github/workflows/eks-request-apply.yml`

**What's Strong**

| Aspect | Assessment |
|--------|------------|
| Manual trigger only | Good - EKS is high-impact, requires explicit `workflow_dispatch` |
| Two-phase flow | Validate → Generate → Commit → Terraform - clear separation |
| Bootstrap guard | Line 96-99: Correctly skips Terraform for `bootstrap-only` requests |
| Build ID state key | Lines 122-126: Build-specific state path for ephemeral clusters |
| allow_build_id_reuse | Safety flag for edge cases (line 13-17) |

**Issues and Gaps**

| Issue | Line(s) | Impact | Severity |
|-------|---------|--------|----------|
| Hardcoded bucket name | 129 | `goldenpath-idp-dev-bucket` - doesn't work for staging/prod | High - needs parameterization |
| Hardcoded region | 109, 131 | `eu-west-2` everywhere | Medium - should be derived from request or config |
| No approval gate for prod | - | Any manual trigger applies - no env-based approval | High for prod safety |
| Missing error on bootstrap-only | 96-99 | Echoes but doesn't fail or guide user to bootstrap workflow | Low - could be clearer |
| No post-apply bootstrap step | - | `cluster+bootstrap` mode creates cluster but doesn't bootstrap | Medium - incomplete flow |
| Commit message lacks request ID | 68 | Generic `[skip ci]` - hard to trace | Low - should include `$EKS_ID` |
| No Terraform plan step | - | Goes straight to apply | Medium - consider plan → approval → apply for safety |

**Security Considerations**

- Line 110: `secrets.TF_AWS_IAM_ROLE_DEV_APPLY` - assumes dev; need staging/prod variants
- Line 68-69: Bot commits without PR review - acceptable for generated files but note the bypass

---

#### `.github/workflows/ci-eks-request-validation.yml`

**What's Strong**

| Aspect | Assessment |
|--------|------------|
| Path-scoped trigger | Lines 7-14: Only runs when relevant files change |
| Smart change detection | Lines 29-57: Distinguishes request vs schema/parser changes |
| Full validation on schema change | Line 52: Re-validates all requests if schema changes |
| Read-only permissions | Line 18: `contents: read` - principle of least privilege |
| Summary output | Lines 83-94: Good visibility in GitHub Actions UI |

**Issues and Gaps**

| Issue | Line(s) | Impact | Recommendation |
|-------|---------|--------|----------------|
| Python version mismatch | 68 vs apply:34 | CI uses 3.10, Apply uses 3.11 | Align to same version |
| requirements-dev.txt dependency | 73 | May fail if file doesn't exist or is stale | Pin `pyyaml` directly like apply workflow |
| No JSON Schema validation | - | Only runs parser validation, not schema validation | Add `check-jsonschema` step |
| Glob pattern in multiline output | 81 | `--input-files ${{ ... }}` with newlines may break | Use `xargs` or array handling |
| No approval check for large nodes | - | Unlike RDS, no guard for `large`/`xlarge` tiers | Consider adding `eks-size-approval-guard.yml` |

---

#### Summary Table

| File | Status | Critical Issues |
|------|--------|-----------------|
| `eks_request_parser.py` | 85% ready | Output path needs verification, missing fields in tfvars |
| `eks-request-apply.yml` | 70% ready | Hardcoded bucket/region, no prod gates, incomplete cluster+bootstrap flow |
| `ci-eks-request-validation.yml` | 90% ready | Python version mismatch, glob handling edge case |

---

#### Recommended Priority Fixes

| Priority | Action | File |
|----------|--------|------|
| P0 | Parameterize bucket name and region based on environment | `eks-request-apply.yml` |
| P0 | Add approval gate for staging/prod environments | `eks-request-apply.yml` |
| P1 | Include `gitops_*`, `ingress_*`, `irsa_enabled` in tfvars output or remove from parser | `eks_request_parser.py` |
| P1 | Verify Terraform can read from `clusters/generated/` path | Both |
| P2 | Align Python versions (recommend 3.11) | `ci-eks-request-validation.yml` |
| P2 | Add size/tier approval guard workflow | New file |
| P3 | Add audit record output for governance alignment | `eks_request_parser.py` |

Signed: Claude Opus 4.5 (2026-01-17T15:10:00Z)

### Update - 2026-01-17T15:45:00Z

**What changed**

- Confirmed secrets flow is complete and working
- Reviewed modifications to `eks-request-apply.yml` (parameterized backend, non-dev guard)
- Reviewed modifications to `eks_request_parser.py` (mode-aware outputs, warning emissions)
- Session capture updated with EKS parser/workflow review feedback

**Secrets Flow Verified**

| Component | Status |
|-----------|--------|
| Backstage Scaffolder (`secret-request.yaml`) | Working - triggers workflow dispatch |
| Workflow (`request-app-secret.yml`) | Working - creates request YAML, runs parser, creates PR |
| Parser (`secret_request_parser.py`) | Working - generates tfvars + ExternalSecret YAML |
| Approval Guard (`secret-approval-guard.yml`) | Working - blocks high-risk until label added |

**EKS Improvements Applied (by user)**

- `eks-request-apply.yml`: Added `allow_non_dev` input, parameterized bucket/lock table/role by environment
- `eks_request_parser.py`: Added mode-aware `enable_k8s_resources` and `apply_kubernetes_addons`, added warnings for non-wired fields

**Alignment Matrix (Updated)**

| Resource | Scaffolder | Parser | Approval Guard | Status |
|----------|------------|--------|----------------|--------|
| RDS | `rds-request.yaml` | `rds_request_parser.py` | `rds-size-approval-guard.yml` | Complete |
| ECR | `ecr-request.yaml` | N/A | N/A | Complete |
| Secrets | `secret-request.yaml` | `secret_request_parser.py` | `secret-approval-guard.yml` | Complete |
| EKS | TODO | `eks_request_parser.py` | TODO | In Progress (parser/workflows done) |

**Next steps**

- Create EKS Backstage scaffolder template
- Add EKS size/tier approval guard workflow
- Test end-to-end EKS request flow

Signed: Claude Opus 4.5 (2026-01-17T15:45:00Z)

### Update - 2026-01-17T16:30:00Z - RDS Coupled Mode Architecture Fix

**Problem Identified**

Build `17-01-26-02` failed with "resource already exists" errors:
- `RDS DB Subnet Group (goldenpath-dev-goldenpath-platform-db-subnet-group)`
- `Secrets Manager Secret (goldenpath/dev/rds/master)`
- `RDS DB Parameter Group (goldenpath-dev-goldenpath-platform-db-params)`

**Root Cause Analysis**

1. Build `17-01-26-01` created RDS resources (coupled mode with `rds_config.enabled=true`)
2. Teardown ran with `BUILD_ID=17-01-26-01` but **did not delete RDS resources**
3. New build `17-01-26-02` with fresh state tried to create same resources → conflict

**Why Teardown Didn't Delete RDS**

The teardown script (`delete_rds_instances_for_build`) searches for RDS by:
1. `BuildId` tag → RDS had no BuildId tag (ephemeral mode doesn't apply BuildId to persistent resources)
2. `kubernetes.io/cluster/${cluster_name}` tag → RDS has no cluster tag
3. `ClusterName` tag → RDS had no ClusterName tag
4. Name pattern → Mismatch between cluster suffix and RDS naming

**Architecture Problem**

Two deployment modes exist but had conflicting assumptions:

| Mode | Cluster Lifecycle | RDS Coupled | What Should Happen |
|------|-------------------|-------------|-------------------|
| Ephemeral | `ephemeral` | `rds_config.enabled=true` | **SHOULD BE BLOCKED** - RDS orphaned on teardown |
| Persistent | `persistent` | `rds_config.enabled=true` | Allowed - teardown captures RDS |
| Standalone | Any | `rds_config.enabled=false` | Use `envs/dev-rds/` separately |

**Fix Implemented**

1. **Fail-fast guard** added to [envs/dev/main.tf](envs/dev/main.tf#L574-L597):
   - Blocks `rds_config.enabled=true` when `cluster_lifecycle=ephemeral`
   - Clear error message with remediation options

2. **Module count updated** to [envs/dev/main.tf](envs/dev/main.tf#L599-L602):
   - `count = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? 1 : 0`
   - RDS only created in persistent mode

3. **ClusterName tag added** to [envs/dev/main.tf](envs/dev/main.tf#L653-L660):
   - Enables teardown discovery in persistent mode
   - Added `Component = "platform-rds-coupled"` for clarity

**Behavior Matrix (After Fix)**

| Scenario | Result |
|----------|--------|
| Ephemeral + `rds_config.enabled=true` | **Fails fast** with clear error |
| Persistent + `rds_config.enabled=true` | Works, teardown finds RDS via ClusterName tag |
| Any + `rds_config.enabled=false` + standalone RDS | Works independently |

**Files Modified**

- `envs/dev/main.tf` - Added fail-fast guard, ClusterName tag, count condition
- `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md` - No changes needed (already documents both modes)
- `envs/dev/terraform.tfvars` - No changes (kept `rds_config.enabled=true`)

**Key Insight**

The original error happened because:
- `cluster_lifecycle = "ephemeral"` was set
- `rds_config.enabled = true` was also set
- This combination creates RDS without proper tagging for teardown
- The fail-fast guard now prevents this invalid configuration

**Next Steps**

- User must decide: switch to `cluster_lifecycle = "persistent"` OR set `rds_config.enabled = false` and use standalone RDS
- For immediate unblock: manually delete orphaned RDS resources from build `17-01-26-01` in AWS Console

Signed: Claude Opus 4.5 (2026-01-17T16:30:00Z)

### Update - 2026-01-17T17:50:17Z

**What changed**
- Finalized `eks-catalog.yaml` and moved EKS catalog to active status in the catalog README.
- Added Backstage EKS request scaffolder + skeleton to generate request YAMLs via PR.
- Added the EKS request flow doc for parity with RDS/ECR.
- Added EKS size/tier approval guard workflow (warn-only).
- Regenerated script index and script certification matrix to include the EKS parser.
- Validated the sample EKS request with the parser.

**Artifacts touched**
- `docs/20-contracts/resource-catalogs/eks-catalog.yaml`
- `docs/20-contracts/resource-catalogs/README.md`
- `backstage-helm/backstage-catalog/templates/eks-request.yaml`
- `backstage-helm/backstage-catalog/templates/skeletons/eks-request/${{ values.request_id }}.yaml`
- `docs/85-how-it-works/self-service/EKS_REQUEST_FLOW.md`
- `.github/workflows/eks-size-approval-guard.yml`
- `scripts/index.md`
- `docs/10-governance/SCRIPT_CERTIFICATION_MATRIX.md`

**Validation**
- `python scripts/eks_request_parser.py --mode validate --input-files docs/20-contracts/eks-requests/dev/EKS-0001.yaml --enums schemas/metadata/enums.yaml`

**Next steps**
- Exercise the end-to-end EKS request flow (Backstage PR -> apply workflow).
- Decide the bootstrap-only execution path (workflow vs runbook).

Signed: Codex (2026-01-17T17:50:17Z)

### Update - 2026-01-17T18:15:00Z - Persistent vs Ephemeral Teardown Architecture

**Context**

Following the RDS coupled mode architecture fix (Update 2026-01-17T16:30:00Z), we clarified how teardown works for persistent vs ephemeral builds.

**Terraform State Keys by Mode**

| Mode | State Key | Command |
|------|-----------|---------|
| Ephemeral | `envs/dev/builds/{build_id}/terraform.tfstate` | `make init ENV=dev BUILD_ID=17-01-26-03` |
| Persistent | `envs/dev/terraform.tfstate` | `make init ENV=dev CLUSTER_LIFECYCLE=persistent` (no BUILD_ID) |

**Teardown Workflow by Mode**

| Mode | Current Makefile Target | Notes |
|------|-------------------------|-------|
| Ephemeral | `make teardown ENV=dev BUILD_ID=17-01-26-03 CLUSTER=goldenpath-dev-eks REGION=eu-west-2` | Works - requires BUILD_ID |
| Persistent | **None** | Makefile requires BUILD_ID; persistent doesn't use one |

**Problem Identified**

The Makefile enforces BUILD_ID for teardown:

```makefile
teardown:
	@if [ -z "$(BUILD_ID)" ]; then echo "ERROR: BUILD_ID required"; exit 1; fi
	# ... rest of teardown logic
```

Persistent mode doesn't use BUILD_ID, so there's no Makefile path to tear it down.

**Proposed Solution: `teardown-persistent` Target**

```makefile
################################################################################
# Teardown - Persistent Mode
################################################################################

teardown-persistent:
	@if [ -z "$(ENV)" ]; then echo "ERROR: ENV required"; exit 1; fi
	@if [ -z "$(CLUSTER)" ]; then echo "ERROR: CLUSTER required"; exit 1; fi
	@if [ -z "$(REGION)" ]; then echo "ERROR: REGION required"; exit 1; fi
	@if [ "$(CONFIRM_DESTROY)" != "yes" ]; then \
		echo "WARNING: This will destroy all persistent resources for $(ENV)"; \
		echo "Set CONFIRM_DESTROY=yes to proceed"; exit 1; \
	fi
	cd envs/$(ENV) && terraform init \
		-backend-config="bucket=$(TF_STATE_BUCKET)" \
		-backend-config="key=envs/$(ENV)/terraform.tfstate" \
		-backend-config="region=$(REGION)" \
		-backend-config="dynamodb_table=$(TF_LOCK_TABLE)"
	cd envs/$(ENV) && terraform destroy -auto-approve
	# Run teardown script for remaining AWS resources
	bash bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh \
		--cluster-name $(CLUSTER) \
		--region $(REGION) \
		--skip-terraform
```

**Key Differences**

| Aspect | Ephemeral Teardown | Persistent Teardown |
|--------|-------------------|---------------------|
| State location | `builds/{build_id}/terraform.tfstate` | `terraform.tfstate` (root) |
| Resource tagging | Uses `BuildId` tag | Uses `ClusterName` tag |
| RDS handling | Skipped (not allowed in ephemeral) | Captured via ClusterName tag |
| Safety gate | None (BUILD_ID is unique) | `CONFIRM_DESTROY=yes` required |

**Current Workaround (Until Target Added)**

For persistent teardown without Makefile target:

```bash
# 1. Initialize with persistent state key
cd envs/dev && terraform init \
  -backend-config="bucket=goldenpath-idp-dev-bucket" \
  -backend-config="key=envs/dev/terraform.tfstate" \
  -backend-config="region=eu-west-2" \
  -backend-config="dynamodb_table=goldenpath-idp-dev-lock"

# 2. Destroy via Terraform
cd envs/dev && terraform destroy

# 3. Run teardown script for AWS cleanup
bash bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh \
  --cluster-name goldenpath-dev-eks \
  --region eu-west-2 \
  --skip-terraform
```

**RDS Resource Cleanup Commands (One-Time)**

For orphaned RDS resources from build `17-01-26-01`:

```bash
# Delete DB Subnet Group
aws rds delete-db-subnet-group \
  --db-subnet-group-name goldenpath-dev-goldenpath-platform-db-subnet-group \
  --region eu-west-2

# Delete DB Parameter Group
aws rds delete-db-parameter-group \
  --db-parameter-group-name goldenpath-dev-goldenpath-platform-db-params \
  --region eu-west-2

# Delete Secrets Manager Secrets (with 7-day recovery)
aws secretsmanager delete-secret \
  --secret-id goldenpath/dev/rds/master \
  --recovery-window-in-days 7 \
  --region eu-west-2

aws secretsmanager delete-secret \
  --secret-id goldenpath/dev/keycloak/postgres \
  --recovery-window-in-days 7 \
  --region eu-west-2

aws secretsmanager delete-secret \
  --secret-id goldenpath/dev/backstage/postgres \
  --recovery-window-in-days 7 \
  --region eu-west-2
```

**Note**: RDS instance requires deletion protection to be disabled first via AWS Console.

**Next Steps**

- Add `teardown-persistent` target to Makefile
- Document in `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
- Consider adding `--lifecycle` flag to existing teardown for mode detection

Signed: Claude Opus 4.5 (2026-01-17T18:15:00Z)

### Update - 2026-01-17T18:05:16Z

**What changed**
- Added a persistent cluster teardown runbook with explicit backend init and safety gate.
- Updated the runbooks index to include the new persistent teardown runbook.
- Added a changelog entry for the persistent teardown documentation.

**Artifacts touched**
- `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md`
- `docs/70-operations/runbooks/README.md`
- `docs/changelog/entries/CL-0145-persistent-cluster-teardown-runbook.md`

**Validation**
- Not run (documentation updates only).

Signed: Codex (2026-01-17T18:05:16Z)

### Update - 2026-01-17T18:14:22Z

**What changed**
- Documented EKS lifecycle alignment rules in the RDS architecture doc.
- Added explicit RDS expectations to the EKS request flow doc.

**Artifacts touched**
- `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
- `docs/85-how-it-works/self-service/EKS_REQUEST_FLOW.md`

**Validation**
- Not run (documentation updates only).

Signed: Codex (2026-01-17T18:14:22Z)

### Update - 2026-01-17T18:42:31Z

**What changed**
- Added lifecycle field to the EKS request UI (ephemeral only for now).
- Added a dedicated bootstrap-only workflow triggered after PR approval/merge.
- Updated the EKS request flow doc to describe the bootstrap-only workflow.

**Artifacts touched**
- `backstage-helm/backstage-catalog/templates/eks-request.yaml`
- `backstage-helm/backstage-catalog/templates/skeletons/eks-request/${{ values.request_id }}.yaml`
- `schemas/requests/eks.schema.yaml`
- `docs/20-contracts/eks-requests/dev/EKS-0001.yaml`
- `scripts/eks_request_parser.py`
- `.github/workflows/eks-bootstrap-only.yml`
- `docs/85-how-it-works/self-service/EKS_REQUEST_FLOW.md`

**Validation**
- Not run (workflow + doc updates only).

Signed: Codex (2026-01-17T18:42:31Z)

### Update - 2026-01-17T18:43:08Z

**What changed**
- Re-validated the sample EKS request after lifecycle gating changes.

**Validation**
- `python scripts/eks_request_parser.py --mode validate --input-files docs/20-contracts/eks-requests/dev/EKS-0001.yaml --enums schemas/metadata/enums.yaml`

Signed: Codex (2026-01-17T18:43:08Z)

### Update - 2026-01-17T18:49:40Z

**What changed**
- Required platform approval for all EKS request PRs.
- Added platform approval input gates to EKS apply and bootstrap-only workflows.
- Restricted lifecycle selection to `ephemeral` in the EKS request contract/UI.

**Artifacts touched**
- `.github/workflows/ci-eks-request-validation.yml`
- `.github/workflows/eks-request-apply.yml`
- `.github/workflows/eks-bootstrap-only.yml`
- `backstage-helm/backstage-catalog/templates/eks-request.yaml`
- `backstage-helm/backstage-catalog/templates/skeletons/eks-request/${{ values.request_id }}.yaml`
- `schemas/requests/eks.schema.yaml`
- `docs/20-contracts/eks-requests/dev/EKS-0001.yaml`
- `scripts/eks_request_parser.py`
- `docs/85-how-it-works/self-service/EKS_REQUEST_FLOW.md`

**Validation**
- `python scripts/eks_request_parser.py --mode validate --input-files docs/20-contracts/eks-requests/dev/EKS-0001.yaml --enums schemas/metadata/enums.yaml`

Signed: Codex (2026-01-17T18:49:40Z)

### Update - 2026-01-17T19:07:05Z

**What changed**
- Closed out the EKS scaffolder session with current readiness and open items.

**Current state**
- EKS request system, scaffolder, and workflows are in place with platform approval gates.
- Lifecycle is visible in Backstage but restricted to ephemeral.

**Follow-ups**
- Run an end-to-end EKS request (Backstage -> PR -> CI -> apply/boot).
- Decide if non-dev should require a second label beyond platform-approval.

Signed: Codex (2026-01-17T19:07:05Z)

### Update - 2026-01-17T22:05:28Z

**What changed**
- Added `test` to EKS environment enums for request validation.

**Artifacts touched**
- `schemas/metadata/enums.yaml`

**Validation**
- Not run (enum update only).

Signed: Codex (2026-01-17T22:05:28Z)

### Update - 2026-01-17T22:06:23Z

**What changed**
- Re-enabled `test` in the Backstage EKS environment dropdown.

**Artifacts touched**
- `backstage-helm/backstage-catalog/templates/eks-request.yaml`

**Validation**
- Not run (template update only).

Signed: Codex (2026-01-17T22:06:23Z)

### Update - 2026-01-17T22:07:06Z

**What changed**
- Added `id-token: write` permission to the EKS apply workflow for OIDC role assumption.

**Artifacts touched**
- `.github/workflows/eks-request-apply.yml`

**Validation**
- Not run (workflow permission update only).

Signed: Codex (2026-01-17T22:07:06Z)

### Update - 2026-01-17T18:45:00Z - Persistent Mode Makefile Targets Implemented

**What changed**

Implemented full persistent mode support in the Makefile, providing equivalent targets for clusters that don't use BUILD_ID.

**New Makefile Targets**

| Target | Purpose | Usage |
|--------|---------|-------|
| `apply-persistent` | Terraform apply without BUILD_ID | `make apply-persistent ENV=dev REGION=eu-west-2` |
| `bootstrap-persistent` | Bootstrap without BUILD_ID | `make bootstrap-persistent ENV=dev REGION=eu-west-2` |
| `deploy-persistent` | Full deploy (apply + rds-provision + bootstrap) | `make deploy-persistent ENV=dev REGION=eu-west-2` |
| `teardown-persistent` | Destroy with safety gate | `make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes` |

**Key Implementation Details**

1. **Cluster name auto-detection**: Reads `cluster_name` from tfvars or defaults to `goldenpath-<env>-eks`
2. **Lifecycle override**: `apply-persistent` passes `-var="cluster_lifecycle=persistent"` to Terraform
3. **Safety gate**: `teardown-persistent` requires explicit `CONFIRM_DESTROY=yes`
4. **RDS integration**: `deploy-persistent` includes `rds-provision-auto` step
5. **Logging**: All operations logged to `logs/build-timings/`

**Mode Comparison**

| Aspect | Ephemeral | Persistent |
|--------|-----------|------------|
| Deploy | `make deploy ENV=dev BUILD_ID=17-01-26-03` | `make deploy-persistent ENV=dev REGION=eu-west-2` |
| Apply only | `make apply ENV=dev BUILD_ID=17-01-26-03` | `make apply-persistent ENV=dev REGION=eu-west-2` |
| Bootstrap only | `make bootstrap ENV=dev BUILD_ID=17-01-26-03` | `make bootstrap-persistent ENV=dev REGION=eu-west-2` |
| Teardown | `make teardown ENV=dev BUILD_ID=17-01-26-03 CLUSTER=... REGION=...` | `make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes` |
| State key | `envs/dev/builds/17-01-26-03/terraform.tfstate` | `envs/dev/terraform.tfstate` |
| RDS allowed | No (fail-fast guard) | Yes |

**Artifacts Modified**

- `Makefile` - Added persistent mode section with 4 new targets, updated `.PHONY`, updated help section

**Validation**

- Syntax validated via linter (auto-applied fixes)

**Next Steps**

- Test `deploy-persistent` end-to-end
- Consider adding `init-persistent` target for explicit state initialization

Signed: Claude Opus 4.5 (2026-01-17T18:45:00Z)
