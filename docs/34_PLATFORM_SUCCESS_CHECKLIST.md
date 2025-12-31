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

## Reliability Metrics (Minimal)

- ✅ Timed build/teardown runs write rows to `docs/build-timings.csv`.
- ✅ `make reliability-metrics` summarizes build/teardown counts and durations.
- ✅ Metrics are focused on reliability signals (success rate + duration), not full CI observability.

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

## Teardown + Rebuild Done Criteria (V1 Gate)

- [ ] Fresh Build ID uses an isolated state key for ephemeral runs (no refresh of prior BuildId resources in PR plan).
- [ ] Teardown completes without manual intervention; a second run is safe (no destructive retries or stuck resources).
- [ ] Orphan cleanup only deletes BuildId-tagged resources; state bucket + lock table are always skipped.
- [ ] Load balancer cleanup does not block teardown (automatic cleanup or runbook path works).
- [ ] CI logs clearly show what was deleted, skipped, and why.

## V1 Readiness Tracker (Current State)

| Area | Item | Status | Evidence / Next step |
| --- | --- | --- | --- |
| CI + Infrastructure | CI plan/apply/bootstrap/teardown succeed without manual fixes | Not met | Fix teardown hangs + orphan cleanup permissions; validate in `ci-teardown.yml` run |
| CI + Infrastructure | State in S3 + locks in DynamoDB | Met | `docs/32_TERRAFORM_STATE_AND_LOCKING.md` |
| CI + Infrastructure | Backend init + state checks automatic | Met | `infra-terraform.yml`, `ci-bootstrap.yml` |
| CI + Infrastructure | Orphan cleanup default + tag-scoped deletes | Partial | Policy exists; apply to CI role and validate delete perms |
| CI + Infrastructure | Failures clear + recoverable | Partial | Reduce manual fixes; runbook coverage + max-wait guards |
| Platform Workloads | Argo CD reachable after bootstrap | Unknown | Run a fresh bootstrap + health check |
| Platform Workloads | Grafana reachable after autoscaling | Unknown | Validate post-apply health checks |
| Platform Workloads | Backstage deploys via GitOps | Unknown | Run reference workload deploy |
| Platform Workloads | Basic smoke checks pass | Unknown | Add/execute smoke check step |
| Access + Security | OIDC roles separated for plan/apply | Met | `docs/33_IAM_ROLES_AND_POLICIES.md` |
| Access + Security | IAM policies logged/auditable | Met | IAM index + ADRs |
| Access + Security | EKS access documented/repeatable | Met | `docs/31_EKS_ACCESS_MODEL.md` |
| Access + Security | Secrets never live in Git | Partial | Enforce in CI/pre-commit |
| Documentation + Governance | Living docs indexed + reviewed | Met | `docs/00_DOC_INDEX.md`, `docs/30_DOCUMENTATION_FRESHNESS.md` |
| Documentation + Governance | ADR immutability + superseded marking | Met | ADR index + superseded entries |
| Documentation + Governance | Runbooks cover top operational flows | Partial | Expand + validate runbooks |
| Documentation + Governance | New joiners can run end-to-end | Partial | Run onboarding walkthrough |
| Confidence Checks | Clean build with new Build ID | Partial | Lifecycle-aware state keys in `ci-bootstrap.yml` + `ci-teardown.yml`; validate in CI |
| Confidence Checks | Failed run retried without manual cleanup | Not met | Address teardown/orphan cleanup gaps |
| Confidence Checks | Scaling predictable and documented | Partial | Validate node group sizing docs |

## V1 Readiness Backlog (Hohpe-Inspired)

- [ ] Fitness functions for tag coverage, teardown completeness, and plan/apply gates.
- [ ] Architect Elevator summary in ADRs/PRs (why + impact, not just mechanics).
- [ ] Contract stability rules for CI inputs and Terraform module interfaces.
- [ ] Idempotent ops: explicitly documented re-run behavior for build/teardown.
- [ ] Golden-path dogfooding: platform deploys via the same templates/pipelines as tenants.
- [ ] Runbook quality bar: symptom → diagnosis → fix format enforced.

---

## Notes

This checklist is intentionally short and practical. If a line item is
unclear, add a runbook or ADR before marking it complete.
