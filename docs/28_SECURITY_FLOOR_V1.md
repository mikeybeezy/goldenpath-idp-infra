# Security Floor V1 (Living Document)

This checklist defines the minimum security baseline for V1. It is the floor, not the ceiling.

## V1 checklist (trimmed)

- OIDC only for CI; no long-lived cloud credentials.
- No secrets in Git; use AWS Secrets Manager/SSM + External Secrets.
- CI image scanning with Trivy; fail on HIGH/CRITICAL for prod, warn in dev/test.
- Pre-merge policy checks (Datree) for Kubernetes manifests.
- Environment boundaries enforced (separate namespaces, Argo Projects/RBAC).
- Source of truth is explicit:
  - Infra: Terraform state
  - In-cluster: GitOps
  - Secrets: AWS
  - Decisions: ADRs
- Least-privilege roles per environment (broader in dev, tighter higher up).
- Human access separated from workload access (humans via IAM/SSO, workloads via IRSA).
- GitOps is the default deployment path; no manual `kubectl apply` in steady state.

## Out of scope for V1

- SBOM signing/verification
- Runtime security agents
- Mandatory security gates for all pipelines

## Change process

- Update the ADR if the floor changes.
- Keep this doc aligned with governance and CI.
