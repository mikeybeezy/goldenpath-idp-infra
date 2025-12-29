# Platform v1 Baseline Success Checklist (Living)

This checklist defines what “success without a key operator” looks like.
It is a practical acceptance bar for repeatable, low‑drama operation.

Use this before marking the platform stable for broader use.

---

## CI + Infrastructure

- ✅ Plan, apply, bootstrap, teardown all succeed via CI without manual fixes.
- ✅ State is in S3 and locks in DynamoDB for all environments.
- ✅ Backend init and state checks are automatic in CI.
- ✅ Orphan cleanup runs by default and only touches tagged resources.
- ✅ Failures are clear and recoverable (no stuck pipelines).

## Platform Workloads

- ✅ Argo CD is reachable after bootstrap.
- ✅ Grafana is reachable after autoscaling or size adjustment.
- ✅ Backstage (or reference workload) deploys via GitOps.
- ✅ Basic smoke checks pass (cluster reachable, pods running).

## Access + Security

- ✅ OIDC roles are separated for plan vs apply.
- ✅ IAM policies are logged and auditable.
- ✅ Access to EKS is documented and repeatable.
- ✅ Secrets never live in Git.

## Documentation + Governance

- ✅ Core living docs are indexed and reviewed on schedule.
- ✅ ADRs are immutable; superseded ADRs are marked.
- ✅ Runbooks cover the top operational flows.
- ✅ New joiners can follow docs to run end‑to‑end.

## Confidence Checks

- ✅ A clean build can be performed with a new Build ID.
- ✅ A failed run can be retried without manual cleanup.
- ✅ Scaling is predictable (node group sizing documented).

---

## Notes

This checklist is intentionally short and practical. If a line item is
unclear, add a runbook or ADR before marking it complete.
