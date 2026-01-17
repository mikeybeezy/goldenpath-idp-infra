---
id: ECR_REQUEST_FLOW
title: 'How It Works: ECR Request Flow'
type: documentation
relates_to:
  - ADR-0095-self-service-registry-creation
  - ADR-0159-backstage-catalog-registry-sync
  - CATALOG_SYSTEMS
---
## How It Works: ECR Request Flow

This document explains the technical lifecycle of an ECR (Elastic Container Registry) request, from the developer "Wizard" in Backstage to the automated provisioning in AWS.

## 0. High-Level Architecture

The platform uses a "Bounded Context" approach to ECR provisioning, ensuring that registry creation is deterministic and decoupled from the rest of the infrastructure state.

```text
+---------------+       +-----------------------+
|   Backstage   | ----> | GitHub Actions Dispatch|
+---------------+       +-----------------------+
                                    |
                        ( 1. Run scaffold_ecr.py )
                                    |
            +-----------------------+-------+-----------------------+
            |                               |                       |
+-----------------------+       +-----------------------+   +-----------------------+
|  Update ECR Catalog   |       |  Update env tfvars    |   |   Validation & Enums  |
+-----------------------+       +-----------------------+   +-----------------------+
            |                               |                       |
            +-----------------------+-------+-----------------------+
                                    |
                          ( 2. Create PR + Plan )
                                    |
+-----------------------+           |
|  Platform Approval    | <---------+ (PR Merged)
+-----------------------+
        |
        |       +---------------------------------------+
        +-----> | Targeted TF Apply (-target=module...) |
                +---------------------------------------+
                                |
                        +---------------+
                        | AWS ECR Repo  |
                        +---------------+
```

## 1. Trigger: Backstage Dispatch

Application teams use a "Self-Service" template in the Backstage Software Catalog. Instead of creating a PR directly (which is brittle), Backstage uses `github:actions:dispatch`.

- **Benefit**: Keeps Backstage simple and offloads complex Git operations to GitHub Actions.
- **Inputs**: Registry Name, Owner, Risk Tier, and Target Environment.

## 2. Processing: Deterministic Scaffolding

The GHA workflow runs the specialized `scripts/scaffold_ecr.py` engine. This engine ensures the request follows the platform's governance contract:

- **Catalog Sync**: Adds the registry to `docs/20-contracts/resource-catalogs/ecr-catalog.yaml`.
- **Infrastructure Bind**: Injects the repository definition into `envs/{env}/terraform.tfvars`.
- **Naming Enforcement**: Validates that registry names and IDs follow the required regex (e.g., `REGISTRY_APP_NAME`).

## 3. Review: Targeted Planning

The platform creates a Pull Request and automatically runs a **Targeted Terraform Plan**.

- **Command**: `terraform plan -target="module.ecr_repositories[\"registry-name\"]"`
- **Why?**: This ensures the plan only shows the creation of the *requested* registry, ignoring unrelated drift in the wider cluster or VPC state. It makes the PR review extremely fast and safe.

## 4. Execution: Auto-Apply on Merge

Once the platform team approves the PR and merges it into the `development` branch, the `ecr-auto-apply.yml` workflow takes over.

- **Trigger**: Label `ecr-registry` + Merged status.
- **Automation**: Runs the targeted `terraform apply` without human intervention, as the plan was already reviewed in the PR.

## 5. Summary: The Value Loop

By abstracting the complexity of Terraform variables and state targeting, the platform provides:

- **Zero Bottlenecks**: Teams don't wait for platform engineers to edit files.
- **100% Governance**: Every ECR repo is tagged with an Owner and Risk Tier by default.
- **Safe Operations**: Targeted applies prevent "Blast Radius" accidents where unrelated changes are accidentally applied.
