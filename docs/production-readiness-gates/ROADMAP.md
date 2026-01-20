---
id: ROADMAP
title: Platform TODO (Living)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 26_AI_AGENT_PROTOCOLS
  - 37_V1_SCOPE_AND_TIMELINE
  - ADR-0022-platform-post-apply-health-checks
  - ADR-0028-platform-dev-branch-gate
  - ADR-0034-platform-ci-environment-contract
  - ADR-0035-platform-iam-audit-cadence
  - ADR-0037-platform-resource-tagging-policy
  - ADR-0063-platform-terraform-helm-bootstrap
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - ADR-0136
  - ADR-0146
  - AGENT_FIRST_BOOT
  - CL-0097
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

## 🏥 Platform Health Command Center

**Generated**: `2026-01-07 08:29:32` | **V1 Readiness**: `95.5%` | **Mean Confidence**: `⭐ (1.1/5.0)`
Add items here before starting work.

## Priority legend

- P0: blocking / urgent
- P1: high impact, near-term
- P2: important, can wait
- P3: nice-to-have

---

## Value Quantification (VQ) Strategy

This roadmap is driven by **Value-Led Prioritization**. Every item is classified by its **VQ Bucket** to ensure we protect the core while moving fast on user-facing capabilities.

### VQ Buckets

|Bucket|Focus|Philosophy|
|:---|:---|:---|
|**🔴 HV/HQ**|**Platform Core**|"Slow is smooth." Protect trust, safety, and auditability at all costs.|
|**🟡 HV/LQ**|**Product Surface**|"Good enough beats elegant later." Ship rough, reversible user features.|
|**🔵 MV/HQ**|**Quiet Multipliers**|"Bound and freeze." Build once, lock it, and stop touching.|
|**⚫ LV/LQ**|**Actively Resist**|Every "No" buys clarity. resist over-customization and premature logic.|

---

## 90-Day Evolution Plan

### Phase 1: Stabilize the Core (🔴 HV/HQ)

- **Phase 2 (Make Power Legible)**: Focus on **🟡 HV/LQ**. Build scaffolds and visibility.
- **Phase 3 (Multipliers)**: Focus on **🔵 MV/HQ**. Build quiet scaling levers.
- **Maintenance**: Focus on **⚫ LV/LQ**. Pruning and hygiene.
- **Focus**: Metadata inheritance, approval routing, deterministic teardown, immutable audit trails.

### Phase 2: Make Power Legible (🟡 HV/LQ)

**Goal**: Show what’s possible without over-engineering.
**Outcome**: *"Users can see and use the platform's value immediately."*

- **Focus**: Scaffolder templates, automation health dashboards, service catalog UX.

### Phase 3: Optionality & Leverage (🔵 MV/HQ)

**Goal**: Prepare for scale without committing to it.
**Outcome**: *"Quiet multipliers that prepare us for V2/Enterprise growth."*

- **Focus**: Schema versioning, knowledge graph exports, policy-to-CI routing.

---

## Items

|ID|Priority|VQ Class|Area|Summary|Owner|Status|Effort|Target|Next step|Why|
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
|001|P1|**🔴 HV/HQ**|CI|Defer health-check wiring until multi-envbring-up stable|platform|Open|M|Q1|Stabilize multi-env lifecycle|Avoid false failures|
|007|P1|**🔴 HV/HQ**|Governance|Switch on dev-branch gate in GitHub rulesets|platform|Open|S|Q1|Configure rulesets|Enforce promote path|
|036|P1|**🔴 HV/HQ**|Governance|Backfill and tag all existing IAM policies|platform|Open|M|Q1|Audit policies|Enable reliable audits|
|050|P1|**🔴 HV/HQ**|Environments|Enable EKS in test, staging, and prod envs|platform|Open|M|Q1|Validate `eks_config`|Multi-env parity|
|052|P1|**🔴 HV/HQ**|GitOps|Add GitOps manifests per environment|platform|Open|M|Q1|Create app manifests|Consistent deployment|
|043|P1|**🟡 HV/LQ**|Observability|Build RED + Golden Signals dashboards (v1)|platform|Open|M|Q1|Create dashboards|V1 visibility baseline|
|051|P1|**🟡 HV/LQ**|Apps|Add stateful app template (Scaffold)|platform|Open|M|Q1|Define template|Golden Path for stateful|
|045|P2|**🟡 HV/LQ**|Cost|Implement Infracost + Backstage Integration|platform|Open|M|Q2|Add CI step|Surface cost leading indicators|
|065|P2|**🔵 MV/HQ**|GitOps|Automate PR Merge Apply (VPC/IAM)|platform|Done|M|Q2|Expand pattern|Eliminate manual ClickOps|
|073|P1|**🔵 MV/HQ**|Governance|Field Test: Automated Governance & VQ Enforcement in Onboarding|platform|Open|S|Q1|Conduct live onboarding drill|Validate friction vs. value of hard-gates|
|002|P3|**⚫ LV/LQ**|Security|SBOM generation for production releases|platform|Open|M||Define approach|Future supply-chain hardening|
|003|P2|CI|Add CI environment contract validator (hard-fail)|platform|Open|S||Define required vars and gating point|docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/adrs/ADR-0034-platform-ci-environment-contract.md|Enforce required inputs before apply|
|004|P2|GitOps|Configure Argo Rollouts in bootstrap (install + health checks)|platform|Open|M||Decide install path and add Argo health checks|docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md|Optional rollout safety for V1+|
|005|P2|Docs|Test doc freshness validator with overdue and missing metadata cases|platform|Open|S||Run validator with `--today` and confirm warnings|docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md|Validate mechanism before enforcement|
|006|P3|Docs|Decide if doc freshness check should become a hard gate|platform|Open|S||Evaluate after tests and initial adoption|docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md|Avoid over-enforcement in V1|
|008|P2|Security|Tighten dev apply IAM policy after successful apply|platform|Open|M||Reduce broad permissions to least privilege|docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md|Start broad, then restrict once stable|
|009|P2|CI|Add PR build_id validation (fail fast before merge)|platform|Open|S||Add PR workflow check for build_id format|.github/workflows/infra-terraform-apply-dev.yml|Catch missing/invalid build IDs earlier|
|010|P3|Repo|Remove duplicate CLUSTER/REGION defaults in Makefile|platform|Open|S||Keep a single source of truth for defaults|Makefile|Reduce confusion about which defaults are used|
|011|P3|Infra|Clarify cluster_lifecycle default in dev tfvars|platform|Open|S||Replace TODO comment with explicit guidance|envs/dev/terraform.tfvars|Avoid accidental lifecycle mismatch|
|012|P2|Infra|Make compute_config.enabled opt-in in dev|platform|Open|S||Set default to false in dev tfvars|envs/dev/terraform.tfvars|Prevent accidental EC2 spend|
|013|P3|Tooling|Standardize cluster name resolution via script|platform|Open|S||Use scripts/resolve-cluster-name.sh consistently|Makefile, scripts/resolve-cluster-name.sh|Align local and CI naming|
|014|P3|CI|Upload plan output as an artifact|platform|Open|S||Add artifact upload step|.github/workflows/infra-terraform.yml|Improve traceability|
|015|P2|CI|Harden plan gate env matching|platform|Open|S||Check workflow input env in gate|.github/workflows/infra-terraform-apply-dev.yml|Prevent mismatched plan/apply|
|016|P1|CI|Allow both BUILD_ID formats (dd-mm-yy-NN and YYYYMMDD-NN)|platform|Open|S||Update regex and/or docs to match|Makefile, .github/workflows/ci-bootstrap.yml|Avoid regressions vs documented examples|
|017|P2|CI|Re-enable Super Linter when CI stabilizes|platform|Open|S||Restore workflow to reduce doc regressions|.github/workflows/super-linter.yml|Disabled temporarily because it slowed the workflow|
|018|P2|CI|Add stricter linting gate for merges to dev|platform|Open|M||Define required lint checks for dev gate|.github/workflows/yamllint.yml|Catch workflow YAML issues before merge|
|019|P2|Security|Tighten teardown permissions after higher envs stabilize|platform|Open|M||Scope teardown IAM actions by tags|IAM apply role policy|Start broad to unblock CI, restrict once stable|
|020|P2|Docs|Create infrastructure architecture diagram|platform|Open|M||Define scope and system boundaries|docs/30-architecture/09_ARCHITECTURE.md|Consolidate platform topology for onboarding and reviews|
|021|P2|Docs|Create infra networking diagram|platform|Open|M||Capture VPC, subnets, routes, NAT/IGW|docs/30-architecture/11_NETWORKING.md|Make network flows and boundaries explicit|
|022|P2|Docs|Create bootstrap process flow diagram|platform|Open|M||Map bootstrap stages + dependencies|docs/40-delivery/17_BUILD_RUN_FLAGS.md|Visualize bootstrap sequence and gates|
|023|P2|Docs|Create CI/CD stages diagram|platform|Open|M||Show PR → plan → apply → bootstrap → teardown|docs/40-delivery/12_GITOPS_AND_CICD.md|Clarify pipeline stages and handoffs|
|024|P2|Docs|Create CD steps diagram|platform|Open|M||Show GitOps sync + rollout steps|docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md|Make CD path explicit for operators|
|025|P2|Docs|Create teardown process diagram|platform|Open|M||Show cleanup and destroy steps|docs/40-delivery/17_BUILD_RUN_FLAGS.md|Reduce teardown ambiguity and failure modes|
|026|P2|Docs|Create CI workflow relationship diagram|platform|Open|M||Show workflows and triggers|docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md|Map CI flow across workflows|
|027|P2|Docs|Create environment promotion flow diagram|platform|Open|M||Show dev → test → staging → prod flow|docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md|Make promotion path and gates explicit|
|028|P2|Docs|Create IAM role assumption diagram|platform|Open|M||Show CI and IRSA role assumptions|docs/60-security/33_IAM_ROLES_AND_POLICIES.md|Clarify access boundaries and trust chains|
|029|P2|Docs|Create Terraform state + lock flow diagram|platform|Open|M||Show S3 state + DynamoDB lock usage|docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md|Prevent state confusion and lock errors|
|030|P2|Docs|Create rollback/incident flow diagram|platform|Open|M||Show GitOps revert + recovery steps|docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md|Standardize rollback expectations|
|031|P2|Docs|Create cost + lifecycle overview diagram|platform|Open|M||Compare ephemeral vs persistent lifecycles|docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md|Set expectations for cost and uptime|
|032|P2|Security|Establish periodic IAM audit cadence for CI roles|platform|Open|S||Define CloudTrail + Access Analyzer review process|docs/adrs/ADR-0035-platform-iam-audit-cadence.md|Reduce permissions over time based on actual usage|
|033|P2|Security|Create IAM audit runbook (CloudTrail + Access Analyzer)|platform|Open|S||Document exact CLI/Athena queries and steps|docs/70-operations/runbooks/03_IAM_AUDIT.md|Make IAM reviews repeatable|
|034|P2|Security|Run first IAM audit after stability milestone|platform|Open|M||Execute runbook and tighten policies|docs/70-operations/runbooks/03_IAM_AUDIT.md|Validate audit cadence in practice|
|035|P2|Security|Define multi-account IAM boundaries per environment (V2)|platform|Open|M||Map env → account and scope roles per account|docs/60-security/33_IAM_ROLES_AND_POLICIES.md|Prepare for teams using separate AWS accounts|
|037|P1|Teardown|Define teardown reliability SLO (p95 < 20m, p99 < 45m; break-glass <5%)|platform|Open|S|Q1|Capture in V1 scope and validation checklist|docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md, docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md|Sets acceptance bar for deterministic teardown|
|038|P1|Teardown|Run 5–10 teardown cycles and record durations + break-glass usage|platform|Open|M|Q1|Track runs and summarize results|docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md|Confirms SLO in practice|
|039|P1|Teardown|If SLO missed, record known limitation and create V1.1 follow-up|platform|Open|S|Q1|Add known limitation + V1.1 entry|docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md|Time-boxed hardening without blocking V1|
|040|P2|Ops|Add AWS Support escalation criteria for ENI >48h|platform|Open|S|Q1|Add runbook section|docs/70-operations/runbooks/06_LB_ENI_ORPHANS.md|Clear path when cleanup stalls|
|041|P2|Observability|Track teardown duration + break-glass usage in pipeline metrics|platform|Open|M|Q1|Extend pipeline metrics|docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md|Measure reliability over time|
|042|P1|Observability|Define RED label contract (service/env/version/team/build_id)|platform|Done|S|Q1|Implement in dashboards + alerts|docs/50-observability/05_OBSERVABILITY_DECISIONS.md|Consistent metrics for dashboards and alerts|
|043|P1|Observability|Build RED + Golden Signals dashboards with minimal alerts|platform|Open|M|Q1|Create dashboards and alert rules|docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md|V1 visibility baseline for operators|
|044|P2|Observability|Capture V1.1 trace plan (OTel + Tempo)|platform|Open|S|Q2|Define data path and sampling|docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md|Make trace adoption explicit and time-boxed|
|045|P2|Cost|Implement Infracost + Backstage Integration|platform|Open|M|Q2|Add `infracost` step to CI|docs/production-readiness-gates/ROADMAP.md|Surface cost impact in PRs and Backstage (Leading Indicator)|
|046|P2|Teardown|Targeted cleanup for orphans (Kong TGs + Balancers)|platform|Open|S|Q1|Scan by cluster/build_id/kong tags|docs/70-operations/runbooks/06_LB_ENI_ORPHANS.md|Prevent quota exhaustion from ghost ingress resources|
|047|P3|Teardown|Implement async Node Group deletion|platform|Open|M|Q2|Trigger delete via CLI before Terraform|docs/40-delivery/17_BUILD_RUN_FLAGS.md|Reduce teardown duration by parallelizing slow steps|
|048|P2|Cost|Validate orphaned EBS PVCs (tag scan)|platform|Open|S|Q1|Scan `tag:kubernetes.io/created-for/pvc/name` in `teardown.sh`|docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md|Prevent hidden costs from persistent PVCs|
|049|P2|Cost|Add Infracost baseline diff vs main for PRs|platform|Open|S|Q2|Compare `main` vs PR plan costs|.github/workflows/pr-terraform-plan.yml|Show cost deltas, not just totals|
|050|P1|Environments|Enable EKS in test, staging, and prod envs|platform|Open|M|Q1|Uncomment and validate `eks_config` per env|envs/test/terraform.tfvars, envs/staging/terraform.tfvars, envs/prod/terraform.tfvars|Multi-env parity for workloads (added 2026-01-03)|
|051|P1|Apps|Add stateful app template (StatefulSet + PVC + storage class)|platform|Open|M|Q1|Define template and ownership boundaries|apps/ (new) + docs/20-contracts/42_APP_TEMPLATE_LIVING.md|Required for stateful workload golden path (added 2026-01-03)|
|052|P1|GitOps|Add GitOps app manifests for stateless + stateful apps per env|platform|Open|M|Q1|Create `gitops/argocd/apps/<env>/<app>.yaml`|gitops/argocd/apps/<env>|Consistent deployment across envs (added 2026-01-03)|
|053|P1|Observability|Validate OOTB app + platform observability across all envs|platform|Open|M|Q1|Run env verification checklist + record results|docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/production-readiness-gates/READINESS_CHECKLIST.md|Confirm observability parity beyond dev (added 2026-01-03)|
|054|P2|Teardown|Unified Teardown Recovery Protocol|platform|Open|M|Q1|Create `force-cleanup` action + auto-retry in CI|docs/production-readiness-gates/ROADMAP.md|Consolidate orphan/LB cleanup into a single reliability hammer|
|055|P2|Governance|Repository lifecycle policy + runbook|platform|Open|S|Q1|Publish policy + runbook; align with scaffolder inputs|docs/10-governance/05_REPOSITORY_LIFECYCLE.md, docs/70-operations/runbooks/10_REPO_DECOMMISSIONING.md|Define deterministic repo lifecycle and decommissioning|
|056|P2|Governance|Validate repo lifecycle workflow (3+ drills)|platform|Open|M|Q1|Run 3 scaffold runs + 1 decommission drill; record evidence links|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Ensure solution goes beyond documentation|
|057|P3|Governance|Log repo creation + decommission duration|platform|Open|S|Q1|Capture duration metrics from scaffolder + decommission drills|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Track end-to-end lifecycle automation time|
|058|P3|Governance|Track scaffold/decommission success rate|platform|Open|S|Q1|Record pass/fail % for lifecycle runs|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Reliability signal for automation|
|059|P3|Governance|Track first-run success vs retries|platform|Open|S|Q1|Capture retry counts for lifecycle workflows|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Indicates determinism and stability|
|060|P3|Governance|Track time-to-ready for new repos|platform|Open|S|Q1|Measure repo creation → first CI green|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|End-to-end onboarding signal|
|061|P3|Governance|Track policy compliance coverage|platform|Open|S|Q1|% repos with metadata + branch protection|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Ensures governance-by-default|
|062|P3|Governance|Track stale repo count and archive rate|platform|Open|S|Q1|Count stale repos flagged vs archived|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Confirms controlled exit path|
|063|P2|Governance|Explore GitHub App agent roles|platform|Open|S|Q1|Define minimal permissions and installation flow|docs/10-governance/08_GITHUB_AGENT_ROLES.md|Avoid new human accounts while preserving auditability|
|064|P2|ECR|Test OIDC-based ecr-build-push.sh script|platform|Open|S|Q1|Run end-to-end test with sample app and verify dual-tagging|scripts/ecr-build-push.sh, docs/guides/standardized-image-delivery.md, ADR-0100|Validate OIDC authentication, multi-tagging (SHA + version), and push reliability before app team adoption|
|065|P2|GitOps|Automate "Terraform Apply" on Pull Request Merge|platform|Done|M|Q2|Expand pattern to other core modules (IAM, VPC)|.github/workflows/ecr-auto-apply.yml|Eliminate manual "ClickOps" step after merging config changes|
|066|P2|Docs|Test & Harden Doc Index Generators (Removal logic)|platform|Done|S|Q1|Monitor for drift in future additions|scripts/generate_workflow_index.py, scripts/generate_script_index.py|Ensure documentation self-heals when tools or workflows are deprecated/deleted|
|067|P2|ECR|Decommission ECR Registry Workflow|platform|Open|S|Q1|Create `decommission-ecr-registry.yml` with safety guardrails|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Enable safe, automated removal of registries|
|068|P1|ECR|Image Creation and Standardized Tagging|platform|Open|S|Q1|Implement hashing and semantic version tagging in `ecr-build-push.sh`|ADR-0100|Ensure images are traceable and immutable|
|069|P2|ECR|Automated Image Deletion (Stale/Untagged)|platform|Open|S|Q1|Configure lifecycle policies for automated cleanup|envs/dev/main.tf|Prevent ECR storage cost bloat|
|070|P1|ECR|Standardized Image Pull/Push (OIDC)|platform|Open|S|Q1|Roll out `ecr-build-push.sh` to all app templates|ADR-0100|Secure, passwordless image delivery as standard|
|071|P3|ECR|Image Version Decommissioning Process|platform|Open|S|Q2|Define archival strategy for sunsetting old images|docs/10-governance/05_REPOSITORY_LIFECYCLE.md|Manage long-term image supply chain technical debt|
|072|P2|Gov|Shared Responsibility Notifications (Lifecycle Events)|platform|Open|M|Q1|Build notification trigger for Slack/Email after Create/Delete|docs/10-governance/38_SHARED_RESPONSIBILITY.md|Clarify ownership boundaries immediately after resource changes|
|073|P2|Backstage|TechDocs: switch local build to S3 publisher|platform|Open|M|Q2|Configure TechDocs S3 bucket + IAM and enable publisher|docs/production-readiness-gates/ROADMAP.md|Faster, more reliable doc builds at scale|
|074|P1|**🔴 HV/HQ**|ECR|Extensive Verification of ECR Single Source of Truth|platform|Done|S|Q1|Monitor for future drift|Script verified against 10 ghost repos|
|075|P2|GitOps|Deprecate legacy ArgoCD bootstrap scripts after build is stable|platform|Open|S|Q1|Mark scripts as deprecated and add a guard to prevent double-install|docs/adrs/ADR-0063-platform-terraform-helm-bootstrap.md, bootstrap/10_gitops-controller/10_argocd_helm.sh, bootstrap/10_bootstrap/goldenpath-idp-bootstrap*.sh|Prevent drift and duplicate ArgoCD installs now that Terraform owns Helm bootstrap|
|076|P2|Governance|Tooling config identity sidecars|platform|Done|S|Q1|Extend to additional config files if needed|docs/adrs/ADR-0136-platform-tooling-config-identity.md, docs/changelog/entries/CL-0097-tooling-config-identity-sidecars.md|Ensure tooling configs have explicit identity and audit trail|
|077|P2|Governance|Enforce tooling sidecar presence in validation/reporting|platform|Open|S|Q1|Add validator/reporting coverage for root config sidecars|scripts/validate_metadata.py, PLATFORM_HEALTH.md|Turn identity sidecars into measurable governance coverage|
|078|P2|Observability|V2: full AWS inventory via Config Aggregator or Resource Explorer|platform|Open|M|Q2|Evaluate costs + scope, then add cross-region inventory|docs/50-observability/05_OBSERVABILITY_DECISIONS.md|Surface tagged + untagged resources across all regions|
|079|P1|**🔴 HV/HQ**|Governance|Infra Governance: Inherit "Born Governed" for Terraform Modules|platform|Open|M|Q1|Extend schema/validator to infra/modules/*|ADR-0146, CNT-001 - Prevent drift in infrastructure code quality|
|080|P1|**🔴 HV/HQ**|Governance|Script Cert: Achieve 100% Maturity 3 (Certified) on P0 scripts|platform|Open|M|Q1|Backfill tests for critical path scripts|SCRIPT_CERTIFICATION_AUDIT.md - Eliminate "trust me" testing via cryptographic proofs|
|081|P3|**🟡 HV/LQ**|Backstage|Kong Backstage Plugin: Build custom plugin for Kong API Gateway visibility|platform|Parked|L|Q3+|Create design spec when capacity available|Community contribution opportunity - no existing Kong plugin in Backstage marketplace. Pattern reusable for Traefik/Istio/NGINX. ~10-12 days effort for MVP.|
|082|P1|**🔴 HV/HQ**|Security|Enforce mandatory security scans at promotion boundary|platform|Open|M|Q1|Design ADR for enforcement strategy|ADR-0170, GOV-0012 - Prevent code reaching prod without security scans. Options: Branch Protection, ArgoCD Admission Controller, OPA/Gatekeeper, ECR Policy.|
|083|P1|**🔴 HV/HQ**|Governance|Require canonical build workflow for all app repos|platform|Open|M|Q1|Define org-wide workflow adoption policy|ADR-0174 - Ensure all repos use goldenpath-build.yml with security scans. Scaffolder enforces for new repos; existing repos require migration.|

## Rules

- Keep items short and specific.
- Update Status + Next step whenever you touch an item.
- Use P0 sparingly.

---
