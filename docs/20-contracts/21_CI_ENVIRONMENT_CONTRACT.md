<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 21_CI_ENVIRONMENT_CONTRACT
title: CI Environment Contract
type: contract
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - 02_PLATFORM_BOUNDARIES
  - 04_PR_GUARDRAILS
  - 26_AI_AGENT_PROTOCOLS
  - 32_TERRAFORM_STATE_AND_LOCKING
  - 33_IAM_ROLES_AND_POLICIES
  - 36_STATE_KEY_STRATEGY
  - 39_GOLDEN_PATH_VALIDATION
  - ADR-0017-platform-policy-as-code
  - ADR-0028-platform-dev-branch-gate
  - ADR-0029-platform-dev-plan-gate
  - ADR-0030-platform-precreated-iam-policies
  - ADR-0033-platform-ci-orchestrated-modes
  - ADR-0034-platform-ci-environment-contract
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ADR-0044-platform-infra-checks-ref-mode
  - ADR-0046-platform-pr-plan-validation-ownership
  - ADR-0051-platform-reliability-metrics-contract-minimums
  - ADR-0060-platform-ephemeral-update-workflow
  - CI_TERRAFORM_WORKFLOWS
  - RB-0019-relationship-extraction-script
  - RELATIONSHIP_EXTRACTION_GUIDE
  - agent_session_summary
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CI Environment Contract

Doc contract:

- Purpose: Define the CI input contract and environment variables used by workflows.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md, docs/40-delivery/17_BUILD_RUN_FLAGS.md, docs/40-delivery/25_PR_TERRAFORM_PLAN.md, docs/adrs/ADR-0034-platform-ci-environment-contract.md, ci-workflows/CI_WORKFLOWS.md

This document defines the environment variables used by GoldenPath CI pipelines.
It serves as the contract between:

- CI workflows
- Terraform
- Bootstrap scripts
- GitOps reconciliation

These variables are intentionally explicit to support deterministic behavior and safe automation.

---

## Contract minimums (V1)

These inputs are the minimum required to keep lifecycle runs deterministic:

- `env` for all workflows.
- `lifecycle` for plan/apply/bootstrap/teardown workflows.
- `build_id` when `lifecycle=ephemeral`.
- `new_build=true` when creating a new ephemeral state key (plan/apply workflows).
- `confirm_apply=apply` for infra apply workflows.
- `confirm_irsa_apply=true` for bootstrap when IRSA service accounts are applied.

## Workflow inputs and env vars

This section lists GitHub Actions inputs, environment variables, and secrets
currently used by workflows in this repo, with their context.

### Infra Terraform Checks (`infra-terraform.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.env` | workflow_dispatch input | Target environment for plan. |
| `inputs.lifecycle` | workflow_dispatch input | State lifecycle (`ephemeral` or `persistent`). |
| `inputs.build_id` | workflow_dispatch input | Build ID used for ephemeral state keys. |
| `inputs.new_build` | workflow_dispatch input | Explicit confirmation for new ephemeral builds. |
| `secrets.TF_AWS_IAM_ROLE_DEV` | repo secret | OIDC role for dev plan. |
| `secrets.TF_AWS_IAM_ROLE_TEST` | repo secret | OIDC role for test plan. |
| `secrets.TF_AWS_IAM_ROLE_STAGING` | repo secret | OIDC role for staging plan. |
| `secrets.TF_AWS_IAM_ROLE_PROD` | repo secret | OIDC role for prod plan. |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

This workflow is **manual-only**; it is not auto-dispatched by PR plans.
Use it when you want an extra validation pass on a specific branch.

### Infra Terraform Apply (dev) (`infra-terraform-apply-dev.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.confirm_apply` | workflow_dispatch input | Manual confirmation for apply. |
| `inputs.lifecycle` | workflow_dispatch input | State lifecycle (`ephemeral` or `persistent`). |
| `inputs.build_id` | workflow_dispatch input | Build ID used for ephemeral state keys. |
| `inputs.new_build` | workflow_dispatch input | Explicit confirmation for new ephemeral builds. |
| `secrets.TF_AWS_IAM_ROLE_DEV_APPLY` | repo secret | OIDC role for dev apply (write). |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

Apply in this workflow is attached to the `dev` GitHub Environment. If required
reviewers are configured, apply waits for approval; otherwise it runs immediately.

Apply also accepts a successful **PR Terraform Plan** for the same commit SHA.
If apply runs on a merge commit, the guard will also accept the PR plan tied to
the merged PR head SHA (manual `infra-terraform.yml` remains optional).

### Documentation guardrails (`session-capture-guard.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| (none) | n/a | Enforces append-only updates in `session_capture/**` with timestamped update headers. |

### Infra Terraform Apply (test) (`infra-terraform-apply-test.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.confirm_apply` | workflow_dispatch input | Manual confirmation for apply. |
| `inputs.lifecycle` | workflow_dispatch input | State lifecycle (`ephemeral` or `persistent`). |
| `inputs.build_id` | workflow_dispatch input | Build ID used for ephemeral state keys. |
| `inputs.new_build` | workflow_dispatch input | Explicit confirmation for new ephemeral builds. |
| `secrets.TF_AWS_IAM_ROLE_TEST_APPLY` | repo secret | OIDC role for test apply (write). |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

Apply in this workflow is attached to the `test` GitHub Environment. If required
reviewers are configured, apply waits for approval; otherwise it runs immediately.

### Infra Terraform Apply (staging) (`infra-terraform-apply-staging.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.confirm_apply` | workflow_dispatch input | Manual confirmation for apply. |
| `inputs.lifecycle` | workflow_dispatch input | State lifecycle (`ephemeral` or `persistent`). |
| `inputs.build_id` | workflow_dispatch input | Build ID used for ephemeral state keys. |
| `inputs.new_build` | workflow_dispatch input | Explicit confirmation for new ephemeral builds. |
| `secrets.TF_AWS_IAM_ROLE_STAGING_APPLY` | repo secret | OIDC role for staging apply (write). |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

Apply in this workflow is attached to the `staging` GitHub Environment. If required
reviewers are configured, apply waits for approval; otherwise it runs immediately.

### Infra Terraform Apply (prod) (`infra-terraform-apply-prod.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.confirm_apply` | workflow_dispatch input | Manual confirmation for apply. |
| `inputs.lifecycle` | workflow_dispatch input | State lifecycle (`ephemeral` or `persistent`). |
| `inputs.build_id` | workflow_dispatch input | Build ID used for ephemeral state keys. |
| `inputs.new_build` | workflow_dispatch input | Explicit confirmation for new ephemeral builds. |
| `secrets.TF_AWS_IAM_ROLE_PROD_APPLY` | repo secret | OIDC role for prod apply (write). |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

Apply in this workflow is attached to the `prod` GitHub Environment. If required
reviewers are configured, apply waits for approval; otherwise it runs immediately.

### Infra Terraform Plan Pipeline (`infra-terraform-dev-pipeline.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.env` | workflow_dispatch input | Target environment for plan. |
| `inputs.lifecycle` | workflow_dispatch input | State lifecycle (`ephemeral` or `persistent`). |
| `inputs.build_id` | workflow_dispatch input | Build ID used for ephemeral state keys. |
| `inputs.new_build` | workflow_dispatch input | Explicit confirmation for new ephemeral builds. |
| `inputs.require_state` | workflow_dispatch input | Fail if persistent state object is missing. |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

This pipeline is plan-only; apply happens in `infra-terraform-apply-dev.yml`
or other environment-specific apply workflows.

Manual plan/apply workflows pass `-var` overrides so workflow inputs take
precedence over `envs/<env>/terraform.tfvars`. PR plans continue to read the
repo values in `envs/dev/terraform.tfvars` by design. For ephemeral runs,
`new_build=true` is required alongside a valid `build_id`.

CI bootstrap supports two configuration sources:

- **repo (default):** uses `envs/<env>/terraform.tfvars` for full config.
- **inputs:** accepts a base64-encoded tfvars payload via `inputs.tfvars_b64`.

### CI Bootstrap (Stub) (`ci-bootstrap.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `ENV` | workflow env | Target environment name. |
| `AWS_REGION` | workflow env | AWS region for bootstrap. |
| `CLUSTER_NAME` | workflow env | Cluster name override. |
| `BUILD_ID` | workflow env | Build ID for ephemeral runs. |
| `CLUSTER_LIFECYCLE` | workflow env | `ephemeral` or `persistent`. |
| `inputs.config_source` | workflow input | Choose repo `terraform.tfvars` or workflow-provided tfvars. |
| `inputs.tfvars_b64` | workflow input | Base64-encoded tfvars when `config_source=inputs`. |
| `inputs.bootstrap_only` | workflow input | Skip Terraform apply; run bootstrap only. |
| `inputs.confirm_irsa_apply` | workflow input | Confirm IRSA service-account apply (needed for LB + autoscaler; future EFS/EBS). |
| `inputs.min_ready_nodes` | workflow input | Minimum Ready node count required. |
| `inputs.new_build` | workflow input | Fail if ephemeral state already exists (prevents accidental append). |
| `STATE_KEY` | workflow step | Backend state key resolved from lifecycle + Build ID. |
| `TF_DIR` | workflow env | Terraform root for environment. |
| `TFVARS_PATH` | workflow env | Explicit tfvars path used for bootstrap IRSA apply. |
| `LB_CLEANUP_ATTEMPTS` | workflow env | Load balancer cleanup retries. |
| `LB_CLEANUP_INTERVAL` | workflow env | Seconds between cleanup retries. |
| `REMOVE_K8S_SA_FROM_STATE` | workflow env | Cleanup flag during teardown. |
| `ENABLE_TF_K8S_RESOURCES` | workflow env | Enable TF-managed K8S resources. |
| `TF_AUTO_APPROVE` | workflow env | Terraform auto-approve flag. |
| `TF_VAR_cluster_lifecycle` | step env | Terraform variable for lifecycle. |
| `TF_VAR_build_id` | step env | Terraform variable for build ID. |
| `TF_VAR_owner_team` | step env | Terraform variable for ownership. |
| `NODE_INSTANCE_TYPE` | step env | Node type for bootstrap (stub). |
| `SKIP_ARGO_SYNC_WAIT` | step env | Skip Argo sync wait (stub). |
| `SKIP_CERT_MANAGER_VALIDATION` | step env | Skip cert-manager check (stub). |
| `COMPACT_OUTPUT` | step env | Output formatting flag (stub). |
| `SCALE_DOWN_AFTER_BOOTSTRAP` | step env | Scale down toggle (stub). |
| `TEARDOWN_CONFIRM` | step env | Guardrail for teardown. |
| `RELAX_PDB` | step env | Allow PDB relax for teardown. |
| `DRAIN_TIMEOUT` | step env | Drain timeout during teardown. |
| `HEARTBEAT_INTERVAL` | step env | Teardown heartbeat interval. |

## CI bootstrap modes (intent-based)

The CI bootstrap workflow supports explicit modes to reduce operator error:

- **bootstrap-only**: skip apply, reuse existing cluster/build (default).
- **build + bootstrap**: apply infra, then bootstrap tooling.
- **teardown**: run the dedicated teardown workflow to destroy the environment.

See `docs/adrs/ADR-0033-platform-ci-orchestrated-modes.md` for the decision and tradeoffs.

## Approval modes (vendor-neutral)

GoldenPath supports two manual-approval patterns for infrastructure changes:

1) **Default (vendor-neutral):** separate plan and apply workflows. Apply runs
   only when a human triggers `workflow_dispatch` and confirms intent.
2) **Optional (GitHub Environments):** apply workflows can attach to a GitHub
   Environment (for example, `dev`). If required reviewers are configured, apply
   waits for approval; if not, it runs immediately.

The platform does **not** require GitHub Environments to be useful. Environments
are treated as an optional convenience for teams already using that feature.

## End-to-end flow (authoritative)

This diagram is the single source of truth for the CI flow.

```text
PR opened
  |
  v
PR Terraform Plan (auto)
  |
  v
PR merged (human approval in code review)
  |
  v
Infra Terraform Apply (manual workflow_dispatch)
  |  (optional: GitHub Environment approval gate)
  v
CI Bootstrap (manual workflow_dispatch)
  |
  v
CI Teardown (manual workflow_dispatch)
```

Optional: run `infra-terraform.yml` manually for an extra validation pass.

Note: `pr-terraform-plan.yml` is PR-triggered only and is not manually runnable.

### CI Teardown (`ci-teardown.yml`)

This workflow is manual and separate from bootstrap to avoid automatic destroy
immediately after bootstrap. It uses the same build ID and cluster naming
resolution to target the correct environment.

**Default cleanup behavior**

- `cleanup_mode=delete` by default (set `dry_run` or `none` to override).
- Cleanup targets resources tagged for the platform; untagged resources are out of scope.
- Teardown role must allow `tag:GetResources` for orphan discovery.
- Teardown resolves the backend state key from `lifecycle` + `build_id`.

**Key inputs**

- `teardown_version` – select teardown runner (`v1` default, `v2` optional).
- `force_delete_lbs` – delete cluster-scoped LBs if ENIs persist (default `true`).
- `lb_cleanup_max_wait` – cap LB/ENI wait loops before retry logic (default `900`).

### CI Backstage (Stub) (`ci-backstage.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `ENV` | workflow env | Target environment name. |
| `IMAGE_TAG` | workflow env | Image tag to deploy. |

### AWS OIDC Test (`aws-oidc.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `secrets.AWS_IAM_ROLE` | repo secret | OIDC test role for AWS STS call. |

## Secrets (Referenced, Not Defined)

Secrets are **not** defined here.
They are provided via:

- Repository secrets (role ARNs)
- AWS OIDC role assumption
- AWS Secrets Manager / SSM

---

## Terraform state and locking (dev)

State is stored in S3 and locked via DynamoDB. The plan role must be able to read
the state object and acquire a lock, even though it does not write infra.

**Dev backend**

- S3 bucket: `goldenpath-idp-dev-bucket`
- Lock table: `goldenpath-idp-dev-db-key`
- State keys:
  - Persistent: `envs/dev/terraform.tfstate`
  - Ephemeral (per BuildId): `envs/dev/builds/<build_id>/terraform.tfstate`

**Plan role policy (dev)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformStateRead",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::goldenpath-idp-dev-bucket",
        "arn:aws:s3:::goldenpath-idp-dev-bucket/envs/dev/terraform.tfstate"
      ]
    },
    {
      "Sid": "TerraformStateLock",
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:eu-west-2:593517239005:table/goldenpath-idp-dev-db-key"
    }
  ]
}
```

Ephemeral runs store state under `envs/dev/builds/<build_id>/terraform.tfstate`.
Apply roles should allow `s3:GetObject`/`s3:PutObject` for the `envs/dev/builds/*`
prefix in the state bucket.

---

## Pre-created IAM policy ARNs (V1)

To keep the apply role least-privilege, the Cluster Autoscaler and AWS Load Balancer Controller
policies are **pre-created** and passed into Terraform as ARNs.

- `iam_config.autoscaler_policy_arn`
- `iam_config.lb_controller_policy_arn`

These are stored in `envs/dev/terraform.tfvars` (or provided via `TF_VAR_*` in CI).
See `docs/adrs/ADR-0030-platform-precreated-iam-policies.md` for rationale and follow-ups.

---

## Invariants

- Pipelines must behave deterministically given the same inputs.
- No variable should change behavior silently.
- Defaults must be explicit and documented.

## V2 multi-account boundary (planned)

Environments may map to different AWS accounts. CI will assume a per-environment
role in the target account (no shared global role). This keeps blast radius
bounded as more teams adopt the platform. See `docs/60-security/33_IAM_ROLES_AND_POLICIES.md`.

## Related docs

- `docs/60-security/33_IAM_ROLES_AND_POLICIES.md`

---

## Terraform plan IAM policy (read-only)

This policy is attached to the **plan** OIDC role so Terraform can resolve
state and read infrastructure metadata without allowing any changes. It is
required because Terraform cannot build a valid plan without read access to
the AWS APIs and state backend.

Use this as the baseline for the plan role and keep apply permissions separate.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyInfrastructure",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "eks:Describe*",
        "eks:List*",
        "iam:Get*",
        "iam:List*",
        "kms:DescribeKey",
        "kms:List*",
        "autoscaling:Describe*",
        "elasticloadbalancing:Describe*",
        "acm:Describe*",
        "acm:List*",
        "route53:List*",
        "route53:Get*",
        "cloudwatch:Describe*",
        "cloudwatch:Get*",
        "cloudwatch:List*",
        "logs:Describe*",
        "logs:Get*",
        "logs:List*",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    },
    {
      "Sid": "StateBackendReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::goldenpath-idp-dev-bucket",
        "arn:aws:s3:::goldenpath-idp-dev-bucket/*"
      ]
    },
    {
      "Sid": "DynamoDBStateLockRead",
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:eu-west-2:YOUR_ACCOUNT_ID:table/goldenpath-idp-dev-db-key"
    }
  ]
}

```

Replace `YOUR_ACCOUNT_ID` and adjust bucket/table ARNs for other environments.

---

## Dev branch gate flow (Option 4)

```text
Legend:
[PLAN] = terraform plan workflow (read-only role)
[APPLY] = terraform apply workflow (write role)
[STATE] = S3 + DynamoDB backend
-->    = trigger

+---------------+
|  Feature Branches (feat/*)|
|  - Devs implement change  |
+-------+-------+
              |
              | PR merge --> dev
              v
+---------------+        [QUALITY GATE]
|  dev branch (gate)        |  -------------+
|  - Shared pre-merge gate  |                           |
+-------+-------+                           |
              |                                         |
              | manual trigger                          |
              v                                         |
+---------------+                            |
|  [PLAN] infra-terraform   |                            |
|  - OIDC: TF_AWS_IAM_ROLE  |                            |
|  - init/plan (dev)        |                            |
+-------+-------+                            |
              |                                         |
              | manual trigger                          |
              v                                         |
+---------------+                            |
|  [APPLY] infra-terraform  |                            |
|  - OIDC: TF_AWS_IAM_ROLE  |                            |
|    _DEV_APPLY             |                            |
|  - apply dev              |                            |
+-------+-------+                            |
              |                                         |
              | success --> allow merge to main         |
              v                                         |
+---------------+                            |
|  main branch              | <--------------+
|  - Only after dev apply   |
+-------+-------+
              |
              | optional promotion
              v
+---------------+
|  staging / prod gates     |
|  - Manual promotion       |
|  - Separate roles         |
+---------------+

+---------------+
|  [STATE] Backend          |
|  - S3 bucket (dev state)  |
|  - DynamoDB lock table    |
+---------------+

```

## Branch protection (required)

To enforce the dev gate:

- `main` only allows merges from `dev`.
- `dev` requires PRs and required checks (plan + apply gate).
- Direct pushes to `main` and `dev` are blocked.

### GitHub ruleset steps (exact)

**Ruleset: protect-dev**

1) Repo → Settings → Rules → Rulesets → New ruleset
2) Name: `protect-dev`
3) Target: Branches
4) Branch name pattern: `dev`
5) Rules:
   - Require a pull request before merging
   - Require status checks to pass (select `pre-commit`, `PR Terraform Plan`, `Infra Terraform Apply (dev)` or your chosen checks)
   - Require branches to be up to date before merging
   - Block force pushes
   - Block deletions
6) Save ruleset.

**Ruleset: protect-main**

1) Repo → Settings → Rules → Rulesets → New ruleset
2) Name: `protect-main`
3) Target: Branches
4) Branch name pattern: `main`
5) Rules:
   - Require a pull request before merging
   - Require status checks to pass (select the dev gate checks)
   - Require branches to be up to date before merging
   - Restrict who can push (optional but recommended)
   - Block force pushes
   - Block deletions
6) Save ruleset.

**Enforce “main only from dev”**

- Use “Restrict who can push” on `main` to allow only a maintainer/team that merges from `dev`.
- Keep required checks aligned with the dev gate so main only receives validated changes.

---

## Dev plan gate (apply safety)

Dev apply must only proceed after the **latest successful dev plan**.

```text
Current (problem):
+---------+     plan (any env)     +----------+
|  Commit (SHA)    |  --------->  |  Plan Success?     |
+---------+                        +----------+
                                               |
                                               | (no env check)
                                               v
                                        +---------+
                                        | Apply DEV        |
                                        | (allowed)        |
                                        +---------+

Risk: a plan for staging/prod can unlock dev apply.

---

Recommended (fix):
+---------+     plan (DEV only)    +----------+
|  Latest dev plan |  --------->  | Plan Success?      |
+---------+                        | env == dev        |
                                            +----------+
                                               |
                                               | only if dev plan
                                               v
                                        +---------+
                                        | Apply DEV        |
                                        | (allowed)        |
                                        +---------+

```

## Ownership

This contract is owned by the platform.
Changes require:

- an ADR if behavior changes
- doc update in the same PR
