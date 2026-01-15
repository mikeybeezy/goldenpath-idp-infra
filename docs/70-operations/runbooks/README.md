---
id: DOCS_RUNBOOKS_README
title: Runbooks Index
type: runbook
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
relates_to:
  - RB-0001
  - RB-0002
  - RB-0003
  - RB-0004
  - RB-0005
  - RB-0006
  - RB-0007
  - RB-0008
  - RB-0009
  - RB-0010
  - RB-0011
  - RB-0012
  - RB-0013
  - RB-0014
  - RB-0015
  - RB-0016
  - RB-0017
  - RB-0018
  - RB-0019
  - RB-0020
  - RB-0021
  - RB-0022
  - RB-0023
  - RB-0024
  - RB-0025
  - RB-0026
  - RB-0027
  - RB-0028
  - RB-0029
  - RB-0030
  - RB-0031
category: runbooks
supported_until: 2028-01-01
version: 1.0
breaking_change: false
---

# Runbooks

## Index

- [docs/70-operations/runbooks/RB-0001-eks-access-recovery.md](docs/70-operations/runbooks/RB-0001-eks-access-recovery.md) — Restore EKS access and refresh kubeconfig.
- [docs/70-operations/runbooks/RB-0002-grafana-access.md](docs/70-operations/runbooks/RB-0002-grafana-access.md) — Port-forward Grafana and retrieve admin credentials.
- [docs/70-operations/runbooks/RB-0003-iam-audit.md](docs/70-operations/runbooks/RB-0003-iam-audit.md) — Audit CI IAM role usage and tighten permissions.
- [docs/70-operations/runbooks/RB-0004-lb-finalizer-stuck.md](docs/70-operations/runbooks/RB-0004-lb-finalizer-stuck.md) — Remove stuck LoadBalancer Service finalizers during teardown.
- [docs/70-operations/runbooks/RB-0005-golden-path-validation.md](docs/70-operations/runbooks/RB-0005-golden-path-validation.md) — Validate PR → apply → bootstrap → teardown end-to-end.
- [docs/70-operations/runbooks/RB-0006-lb-eni-orphans.md](docs/70-operations/runbooks/RB-0006-lb-eni-orphans.md) — Recover subnet deletes blocked by LoadBalancer ENIs.
- [docs/70-operations/runbooks/RB-0007-tf-state-force-unlock.md](docs/70-operations/runbooks/RB-0007-tf-state-force-unlock.md) — Break-glass Terraform state unlock.
- [docs/70-operations/runbooks/RB-0008-managed-lb-cleanup.md](docs/70-operations/runbooks/RB-0008-managed-lb-cleanup.md) — Remove LBC-managed LBs, ENIs, and SGs by cluster tag.
- [docs/70-operations/runbooks/RB-0009-ci-teardown-recovery-v2.md](docs/70-operations/runbooks/RB-0009-ci-teardown-recovery-v2.md) — CI-only recovery sequence for v2 teardown hangs and state locks.
- [docs/70-operations/runbooks/RB-0010-dev-branch-apply.md](docs/70-operations/runbooks/RB-0010-dev-branch-apply.md) — Build an environment from the `development` branch apply workflow.
- [docs/70-operations/runbooks/RB-0011-repo-decommissioning.md](docs/70-operations/runbooks/RB-0011-repo-decommissioning.md) — Archive/delete repos with teardown evidence and audit trail.
- [docs/70-operations/runbooks/RB-0012-argocd-app-readiness.md](docs/70-operations/runbooks/RB-0012-argocd-app-readiness.md) — Argo CD app readiness checklist and dependency checks.
- [docs/70-operations/runbooks/RB-0013-leak-protection-management.md](docs/70-operations/runbooks/RB-0013-leak-protection-management.md) — Preventing ungoverned assets from leaking into Production.
- [docs/70-operations/runbooks/RB-0014-metadata-and-enum-alignment.md](docs/70-operations/runbooks/RB-0014-metadata-and-enum-alignment.md) — Commands and logic for resolving metadata drift.
- [docs/70-operations/runbooks/RB-0015-repo-health-and-hygiene.md](docs/70-operations/runbooks/RB-0015-repo-health-and-hygiene.md) — Platform Owner's guide to maintaining repo health.
- [docs/70-operations/runbooks/RB-0016-extending-governance-vocabulary.md](docs/70-operations/runbooks/RB-0016-extending-governance-vocabulary.md) — How to add new values to the system enums.
- [docs/70-operations/runbooks/RB-0017-orphan-cleanup.md](docs/70-operations/runbooks/RB-0017-orphan-cleanup.md) — Delete BuildId-tagged orphaned resources safely.
- [docs/70-operations/runbooks/RB-0018-metadata-backfill-script.md](docs/70-operations/runbooks/RB-0018-metadata-backfill-script.md) — Automated metadata injection for legacy directories.
- [docs/70-operations/runbooks/RB-0019-relationship-extraction-script.md](docs/70-operations/runbooks/RB-0019-relationship-extraction-script.md) — Building the Platform Knowledge Graph via metadata links.
- [docs/70-operations/runbooks/RB-0020-git-troubleshooting.md](docs/70-operations/runbooks/RB-0020-git-troubleshooting.md) — Resolving branch drift and merge conflicts in governed repos.
- [docs/70-operations/runbooks/RB-0025-ecr-catalog-sync.md](docs/70-operations/runbooks/RB-0025-ecr-catalog-sync.md) — Sync Backstage ECR registry to AWS physical state.
- [docs/70-operations/runbooks/RB-0026-local-secret-generation.md](docs/70-operations/runbooks/RB-0026-local-secret-generation.md) — Execute the Secret Request Parser locally for dry-runs and targeting.
- [docs/70-operations/runbooks/RB-0027-frictionless-pr-gates.md](docs/70-operations/runbooks/RB-0027-frictionless-pr-gates.md) — Managing PR gate policies and exemptions.
- [docs/70-operations/runbooks/RB-0028-governance-registry-operations.md](docs/70-operations/runbooks/RB-0028-governance-registry-operations.md) — Syncing governance registry branch operations.
- [docs/70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md](docs/70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md) — Manually rotate RDS credentials in Secrets Manager.
- [docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md](docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md) — Emergency RDS instance deletion procedures.
- [docs/70-operations/runbooks/RB-0031-idp-stack-deployment.md](docs/70-operations/runbooks/RB-0031-idp-stack-deployment.md) — Deploy Keycloak and Backstage IDP stack with ECR images and RDS.

### App Team Runbooks
- [docs/70-operations/runbooks/app-team/RB-0021-fix-cve-guide.md](docs/70-operations/runbooks/app-team/RB-0021-fix-cve-guide.md) — Step-by-step guide to resolving CVEs in container images.
- [docs/70-operations/runbooks/app-team/RB-0022-pull-image-guide.md](docs/70-operations/runbooks/app-team/RB-0022-pull-image-guide.md) — How to pull images from the ECR registry with correct credentials.
- [docs/70-operations/runbooks/app-team/RB-0023-push-image-guide.md](docs/70-operations/runbooks/app-team/RB-0023-push-image-guide.md) — Authenticating and pushing images to the platform registry.
- [docs/70-operations/runbooks/app-team/RB-0024-request-registry.md](docs/70-operations/runbooks/app-team/RB-0024-request-registry.md) — Requesting a new ECR repository via the governance model.

Operational runbooks for GoldenPath (incident response, recovery, and routine ops).
