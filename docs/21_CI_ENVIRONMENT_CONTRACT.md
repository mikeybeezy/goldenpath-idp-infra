# CI Environment Contract

This document defines the environment variables used by GoldenPath CI pipelines.
It serves as the contract between:

- CI workflows
- Terraform
- Bootstrap scripts
- GitOps reconciliation

These variables are intentionally explicit to support deterministic behavior and safe automation.

---

## Workflow inputs and env vars

This section lists GitHub Actions inputs, environment variables, and secrets
currently used by workflows in this repo, with their context.

### Infra Terraform Checks (`infra-terraform.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.env` | workflow_dispatch input | Target environment for plan. |
| `secrets.TF_AWS_IAM_ROLE_DEV` | repo secret | OIDC role for dev plan. |
| `secrets.TF_AWS_IAM_ROLE_TEST` | repo secret | OIDC role for test plan. |
| `secrets.TF_AWS_IAM_ROLE_STAGING` | repo secret | OIDC role for staging plan. |
| `secrets.TF_AWS_IAM_ROLE_PROD` | repo secret | OIDC role for prod plan. |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Backend state config per environment. |

### Infra Terraform Apply (dev) (`infra-terraform-apply-dev.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `inputs.confirm_apply` | workflow_dispatch input | Manual confirmation for apply. |
| `secrets.TF_AWS_IAM_ROLE_DEV_APPLY` | repo secret | OIDC role for dev apply (write). |
| `aws-region` (eu-west-2) | workflow step | Region used by AWS provider and backend. |
| `bucket` / `dynamodb_table` | workflow step | Dev backend state config. |

### CI Bootstrap (Stub) (`ci-bootstrap.yml`)

| Variable | Source | Purpose |
| --- | --- | --- |
| `ENV` | workflow env | Target environment name. |
| `AWS_REGION` | workflow env | AWS region for bootstrap. |
| `CLUSTER_NAME` | workflow env | Cluster name override. |
| `BUILD_ID` | workflow env | Build ID for ephemeral runs. |
| `CLUSTER_LIFECYCLE` | workflow env | `ephemeral` or `persistent`. |
| `TF_DIR` | workflow env | Terraform root for environment. |
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

- **build + bootstrap**: apply infra, then bootstrap tooling (default).
- **bootstrap-only**: skip apply, reuse existing cluster/build.
- **teardown**: run the dedicated teardown workflow to destroy the environment.

See `docs/adrs/ADR-0033-platform-ci-orchestrated-modes.md` for the decision and tradeoffs.

### CI Teardown (`ci-teardown.yml`)

This workflow is manual and separate from bootstrap to avoid automatic destroy
immediately after bootstrap. It uses the same build ID and cluster naming
resolution to target the correct environment.

**Default cleanup behavior**
- `CLEANUP_ORPHANS=true` by default.
- Cleanup targets resources tagged for the platform; untagged resources are out of scope.

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
- State key: `envs/dev/terraform.tfstate`
- Lock table: `goldenpath-idp-dev-db-key`

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

## Related docs

- `docs/33_IAM_ROLES_AND_POLICIES.md`

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

+---------------------------+
|  Feature Branches (feat/*)|
|  - Devs implement change  |
+-------------+-------------+
              |
              | PR merge --> dev
              v
+---------------------------+        [QUALITY GATE]
|  dev branch (gate)        |  -------------------------+
|  - Shared pre-merge gate  |                           |
+-------------+-------------+                           |
              |                                         |
              | manual trigger                          |
              v                                         |
+---------------------------+                            |
|  [PLAN] infra-terraform   |                            |
|  - OIDC: TF_AWS_IAM_ROLE  |                            |
|  - init/plan (dev)        |                            |
+-------------+-------------+                            |
              |                                         |
              | manual trigger                          |
              v                                         |
+---------------------------+                            |
|  [APPLY] infra-terraform  |                            |
|  - OIDC: TF_AWS_IAM_ROLE  |                            |
|    _DEV_APPLY             |                            |
|  - apply dev              |                            |
+-------------+-------------+                            |
              |                                         |
              | success --> allow merge to main         |
              v                                         |
+---------------------------+                            |
|  main branch              | <--------------------------+
|  - Only after dev apply   |
+-------------+-------------+
              |
              | optional promotion
              v
+---------------------------+
|  staging / prod gates     |
|  - Manual promotion       |
|  - Separate roles         |
+---------------------------+

+---------------------------+
|  [STATE] Backend          |
|  - S3 bucket (dev state)  |
|  - DynamoDB lock table    |
+---------------------------+

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
+------------------+     plan (any env)     +-------------------+
|  Commit (SHA)    |  ------------------>  |  Plan Success?     |
+------------------+                        +-------------------+
                                               |
                                               | (no env check)
                                               v
                                        +------------------+
                                        | Apply DEV        |
                                        | (allowed)        |
                                        +------------------+

Risk: a plan for staging/prod can unlock dev apply.

---

Recommended (fix):
+------------------+     plan (DEV only)    +-------------------+
|  Latest dev plan |  ------------------>  | Plan Success?      |
+------------------+                        | env == dev        |
                                            +-------------------+
                                               |
                                               | only if dev plan
                                               v
                                        +------------------+
                                        | Apply DEV        |
                                        | (allowed)        |
                                        +------------------+

```

## Ownership

This contract is owned by the platform.
Changes require:

- an ADR if behavior changes
- doc update in the same PR
