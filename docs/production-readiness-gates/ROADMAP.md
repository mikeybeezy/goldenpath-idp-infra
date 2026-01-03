# Platform TODO (Living)

This is the single rolling backlog. Add items here before starting work.

## Priority legend

- P0: blocking / urgent
- P1: high impact, near-term
- P2: important, can wait
- P3: nice-to-have

## Items

| ID | Priority | Area | Summary | Owner | Status | Effort | Target | Next step | References | Why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 001 | P1 | CI | Defer health-check wiring until multi-env bring-up/teardown is stable | platform | Open | M | Q1 | Stabilize multi-env CI lifecycle | docs/40-delivery/26_POST_APPLY_HEALTH_CHECKS.md, docs/adrs/ADR-0022-platform-post-apply-health-checks.md | Avoid false failures before CI lifecycle is proven |
| 002 | P3 | Security | Introduce SBOM generation for production releases | platform | Open | M |  | Define approach (e.g., Syft/CycloneDX) | docs/60-security/28_SECURITY_FLOOR_V1.md | Future supply-chain hardening |
| 003 | P2 | CI | Add CI environment contract validator (hard-fail) | platform | Open | S |  | Define required vars and gating point | docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/adrs/ADR-0034-platform-ci-environment-contract.md | Enforce required inputs before apply |
| 004 | P2 | GitOps | Configure Argo Rollouts in bootstrap (install + health checks) | platform | Open | M |  | Decide install path and add Argo health checks | docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md | Optional rollout safety for V1+ |
| 005 | P2 | Docs | Test doc freshness validator with overdue and missing metadata cases | platform | Open | S |  | Run validator with `--today` and confirm warnings | docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md | Validate mechanism before enforcement |
| 006 | P3 | Docs | Decide if doc freshness check should become a hard gate | platform | Open | S |  | Evaluate after tests and initial adoption | docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md | Avoid over-enforcement in V1 |
| 007 | P1 | Governance | Switch on dev-branch gate in GitHub rulesets | platform | Open | S |  | Configure `dev` and `main` rulesets | docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/adrs/ADR-0028-platform-dev-branch-gate.md | Enforce value-preserving promotion path |
| 008 | P2 | Security | Tighten dev apply IAM policy after successful apply | platform | Open | M |  | Reduce broad permissions to least privilege | docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md | Start broad, then restrict once stable |
| 009 | P2 | CI | Add PR build_id validation (fail fast before merge) | platform | Open | S |  | Add PR workflow check for build_id format | .github/workflows/infra-terraform-apply-dev.yml | Catch missing/invalid build IDs earlier |
| 010 | P3 | Repo | Remove duplicate CLUSTER/REGION defaults in Makefile | platform | Open | S |  | Keep a single source of truth for defaults | Makefile | Reduce confusion about which defaults are used |
| 011 | P3 | Infra | Clarify cluster_lifecycle default in dev tfvars | platform | Open | S |  | Replace TODO comment with explicit guidance | envs/dev/terraform.tfvars | Avoid accidental lifecycle mismatch |
| 012 | P2 | Infra | Make compute_config.enabled opt-in in dev | platform | Open | S |  | Set default to false in dev tfvars | envs/dev/terraform.tfvars | Prevent accidental EC2 spend |
| 013 | P3 | Tooling | Standardize cluster name resolution via script | platform | Open | S |  | Use scripts/resolve-cluster-name.sh consistently | Makefile, scripts/resolve-cluster-name.sh | Align local and CI naming |
| 014 | P3 | CI | Upload plan output as an artifact | platform | Open | S |  | Add artifact upload step | .github/workflows/infra-terraform.yml | Improve traceability |
| 015 | P2 | CI | Harden plan gate env matching | platform | Open | S |  | Check workflow input env in gate | .github/workflows/infra-terraform-apply-dev.yml | Prevent mismatched plan/apply |
| 016 | P1 | CI | Allow both BUILD_ID formats (dd-mm-yy-NN and YYYYMMDD-NN) | platform | Open | S |  | Update regex and/or docs to match | Makefile, .github/workflows/ci-bootstrap.yml | Avoid regressions vs documented examples |
| 017 | P2 | CI | Re-enable Super Linter when CI stabilizes | platform | Open | S |  | Restore workflow to reduce doc regressions | .github/workflows/super-linter.yml | Disabled temporarily because it slowed the workflow |
| 018 | P2 | CI | Add stricter linting gate for merges to dev | platform | Open | M |  | Define required lint checks for dev gate | .github/workflows/yamllint.yml | Catch workflow YAML issues before merge |
| 019 | P2 | Security | Tighten teardown permissions after higher envs stabilize | platform | Open | M |  | Scope teardown IAM actions by tags | IAM apply role policy | Start broad to unblock CI, restrict once stable |
| 036 | P1 | Governance | Clear technical debt and tag all existing IAM policies | platform | Open | M |  | Audit IAM policies and backfill required tags | docs/10-governance/35_RESOURCE_TAGGING.md, docs/adrs/ADR-0037-platform-resource-tagging-policy.md | Enable tag-scoped cleanup and reliable audits |
| 020 | P2 | Docs | Create infrastructure architecture diagram | platform | Open | M |  | Define scope and system boundaries | docs/30-architecture/09_ARCHITECTURE.md | Consolidate platform topology for onboarding and reviews |
| 021 | P2 | Docs | Create infra networking diagram | platform | Open | M |  | Capture VPC, subnets, routes, NAT/IGW | docs/30-architecture/11_NETWORKING.md | Make network flows and boundaries explicit |
| 022 | P2 | Docs | Create bootstrap process flow diagram | platform | Open | M |  | Map bootstrap stages + dependencies | docs/40-delivery/17_BUILD_RUN_FLAGS.md | Visualize bootstrap sequence and gates |
| 023 | P2 | Docs | Create CI/CD stages diagram | platform | Open | M |  | Show PR → plan → apply → bootstrap → teardown | docs/40-delivery/12_GITOPS_AND_CICD.md | Clarify pipeline stages and handoffs |
| 024 | P2 | Docs | Create CD steps diagram | platform | Open | M |  | Show GitOps sync + rollout steps | docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md | Make CD path explicit for operators |
| 025 | P2 | Docs | Create teardown process diagram | platform | Open | M |  | Show cleanup and destroy steps | docs/40-delivery/17_BUILD_RUN_FLAGS.md | Reduce teardown ambiguity and failure modes |
| 026 | P2 | Docs | Create CI workflow relationship diagram | platform | Open | M |  | Show workflows and triggers | docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md | Map CI flow across workflows |
| 027 | P2 | Docs | Create environment promotion flow diagram | platform | Open | M |  | Show dev → test → staging → prod flow | docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md | Make promotion path and gates explicit |
| 028 | P2 | Docs | Create IAM role assumption diagram | platform | Open | M |  | Show CI and IRSA role assumptions | docs/60-security/33_IAM_ROLES_AND_POLICIES.md | Clarify access boundaries and trust chains |
| 029 | P2 | Docs | Create Terraform state + lock flow diagram | platform | Open | M |  | Show S3 state + DynamoDB lock usage | docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md | Prevent state confusion and lock errors |
| 030 | P2 | Docs | Create rollback/incident flow diagram | platform | Open | M |  | Show GitOps revert + recovery steps | docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md | Standardize rollback expectations |
| 031 | P2 | Docs | Create cost + lifecycle overview diagram | platform | Open | M |  | Compare ephemeral vs persistent lifecycles | docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md | Set expectations for cost and uptime |
| 032 | P2 | Security | Establish periodic IAM audit cadence for CI roles | platform | Open | S |  | Define CloudTrail + Access Analyzer review process | docs/adrs/ADR-0035-platform-iam-audit-cadence.md | Reduce permissions over time based on actual usage |
| 033 | P2 | Security | Create IAM audit runbook (CloudTrail + Access Analyzer) | platform | Open | S |  | Document exact CLI/Athena queries and steps | docs/runbooks/03_IAM_AUDIT.md | Make IAM reviews repeatable |
| 034 | P2 | Security | Run first IAM audit after stability milestone | platform | Open | M |  | Execute runbook and tighten policies | docs/runbooks/03_IAM_AUDIT.md | Validate audit cadence in practice |
| 035 | P2 | Security | Define multi-account IAM boundaries per environment (V2) | platform | Open | M |  | Map env → account and scope roles per account | docs/60-security/33_IAM_ROLES_AND_POLICIES.md | Prepare for teams using separate AWS accounts |
| 037 | P1 | Teardown | Define teardown reliability SLO (p95 < 20m, p99 < 45m; break-glass <5%) | platform | Open | S | Q1 | Capture in V1 scope and validation checklist | docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md, docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md | Sets acceptance bar for deterministic teardown |
| 038 | P1 | Teardown | Run 5–10 teardown cycles and record durations + break-glass usage | platform | Open | M | Q1 | Track runs and summarize results | docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md | Confirms SLO in practice |
| 039 | P1 | Teardown | If SLO missed, record known limitation and create V1.1 follow-up | platform | Open | S | Q1 | Add known limitation + V1.1 entry | docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md | Time-boxed hardening without blocking V1 |
| 040 | P2 | Ops | Add AWS Support escalation criteria for ENI >48h | platform | Open | S | Q1 | Add runbook section | docs/runbooks/06_LB_ENI_ORPHANS.md | Clear path when cleanup stalls |
| 041 | P2 | Observability | Track teardown duration + break-glass usage in pipeline metrics | platform | Open | M | Q1 | Extend pipeline metrics | docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md | Measure reliability over time |
| 042 | P1 | Observability | Define RED label contract (service/env/version/team/build_id) | platform | Done | S | Q1 | Implement in dashboards + alerts | docs/50-observability/05_OBSERVABILITY_DECISIONS.md | Consistent metrics for dashboards and alerts |
| 043 | P1 | Observability | Build RED + Golden Signals dashboards with minimal alerts | platform | Open | M | Q1 | Create dashboards and alert rules | docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md | V1 visibility baseline for operators |
| 044 | P2 | Observability | Capture V1.1 trace plan (OTel + Tempo) | platform | Open | S | Q2 | Define data path and sampling | docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md | Make trace adoption explicit and time-boxed |
| 045 | P2 | Cost | Implement Infracost + Backstage Integration | platform | Open | M | Q2 | Add `infracost` step to CI | docs/production-readiness-gates/ROADMAP.md | Surface cost impact in PRs and Backstage (Leading Indicator) |
| 046 | P2 | Teardown | Targeted cleanup for orphans (Kong TGs + Balancers) | platform | Open | S | Q1 | Scan by cluster/build_id/kong tags | docs/runbooks/06_LB_ENI_ORPHANS.md | Prevent quota exhaustion from ghost ingress resources |
| 047 | P3 | Teardown | Implement async Node Group deletion | platform | Open | M | Q2 | Trigger delete via CLI before Terraform | docs/40-delivery/17_BUILD_RUN_FLAGS.md | Reduce teardown duration by parallelizing slow steps |
| 048 | P2 | Cost | Validate orphaned EBS volumes in teardown | platform | Open | S | Q1 | Add volume scan to `teardown.sh` | docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md | Prevent hidden costs from persistent PVCs |

## Rules

- Keep items short and specific.
- Update Status + Next step whenever you touch an item.
- Use P0 sparingly.

****
