# Runbooks

## Index

- `docs/runbooks/01_EKS_ACCESS_RECOVERY.md` — Restore EKS access and refresh kubeconfig.
- `docs/runbooks/02_GRAFANA_ACCESS.md` — Port-forward Grafana and retrieve admin credentials.
- `docs/runbooks/03_IAM_AUDIT.md` — Audit CI IAM role usage and tighten permissions.
- `docs/runbooks/04_LB_FINALIZER_STUCK.md` — Remove stuck LoadBalancer Service finalizers during teardown.
- `docs/runbooks/05_GOLDEN_PATH_VALIDATION.md` — Validate PR → apply → bootstrap → teardown end-to-end.
- `docs/runbooks/06_LB_ENI_ORPHANS.md` — Recover subnet deletes blocked by LoadBalancer ENIs.
- `docs/runbooks/07_TF_STATE_FORCE_UNLOCK.md` — Break-glass Terraform state unlock.
- `docs/runbooks/08_MANAGED_LB_CLEANUP.md` — Remove LBC-managed LBs, ENIs, and SGs by cluster tag.
- `docs/runbooks/09_CI_TEARDOWN_RECOVERY_V2.md` — CI-only recovery sequence for v2 teardown hangs and state locks.
- `docs/runbooks/10_REPO_DECOMMISSIONING.md` — Archive/delete repos with teardown evidence and audit trail.
- `docs/runbooks/ORPHAN_CLEANUP.md` — Delete BuildId-tagged orphaned resources safely.

Operational runbooks for GoldenPath (incident response, recovery, and routine ops).
