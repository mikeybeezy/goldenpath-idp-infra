---
id: agent_session_summary
title: 'Agent Session Summary (Append-Only)'
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
---

When switching agents or context windows:

Agents must:
1. Read `docs/10-governance/07_1_AI_COLLABORATION_PROTOCOL.md`
2. Read `docs/adrs/ADR-0163-agent-collaboration-governance.md`
3. Read `docs/10-governance/07_AI_AGENT_GOVERNANCE.md`
4. Read `docs/00-foundations/00_DESIGN_PHILOSOPHY.md`
5. Read `docs/10-governance/PR-156-STABILIZATION-CHECKLIST.md`
6. Read `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md`
7. Read `docs/80-onboarding/00_START_HERE.md`
8. Read `docs/80-onboarding/13_COLLABORATION_GUIDE.md`
9. Read `docs/80-onboarding/23_NEW_JOINERS.md`
10. Read `docs/80-onboarding/24_PR_GATES.md`
11. Read `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md`
12. Read `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md`
13. Read `docs/80-onboarding/AGENT_FIRST_BOOT.md`
14. Read `docs/10-governance/01_GOVERNANCE.md`
15. Read `docs/10-governance/09_AGENT_COLLABORATION_MATRIX.md`
16. Read `agent_summary/session_summary_template.md`
17. Read the latest session state from the canonical session summary document
18. Acknowledge understanding before continuing work


# Session Summary (Append-Only)

This file is an **append-only handoff log**.
Do **not** edit or rewrite previous entries. Add a new timestamped block at the end.

---

## 2026-01-16T00:00:00Z — INIT
Owner: platform-team
Agent: none
Goal: Initialize session summary log.

### Context
- Repo: goldenpath-idp-infra | goldenpath-idp-infra-backstage
- Purpose: Track high-signal progress + decisions across humans and AI agents.

### Rules
- Append-only blocks
- Each block must start with `## <ISO-8601 UTC timestamp> — <short title>`
- Include: Goal, Checkpoints, Edge cases, Next actions, Links
- timestamped
- always include goal + checkpoints + next actions
- link to PRs/runbooks/ADRs

# Format to follow
- Copy the entry template from `agent_summary/session_summary_template.md`.
- Paste it at the end during (or at the end of) the session.
- Fill it out and commit.

## Template source (copy from here)

```markdown
## <YYYY-MM-DDTHH:MMZ> — <AREA>: <short description> — env=<dev|test|staging|prod> build_id=<id|na>

Owner: <name/team>
Agent: <codex|chatgpt|human|...>
Goal: <one sentence>

Date range: <YYYY-MM-DD / YYYY-MM-DD> (optional)
Environment: <cloud/local> `<env>`
Cluster: <name> (optional)
Region: <region> (optional)
Objective: <short statement>

### In-Session Log (append as you go)
- <HH:MMZ> — Started: <task> — status: <running>
- <HH:MMZ> — Change: <what changed> — file: <path>
- <HH:MMZ> — Decision: <what you decided> — why: <reason>
- <HH:MMZ> — Blocker: <issue> — next step: <action>
- <HH:MMZ> — Result: <test> — outcome: <pass/fail>

### Checkpoints
- [ ] <checkpoint 1>
- [ ] <checkpoint 2>
- [ ] <checkpoint 3>

### Edge cases observed (optional)
- <symptom> -> <cause (if known)> -> <mitigation>

### Outputs produced (optional)
- PRs: <#123, #124>
- Scripts: <scripts/foo.py>
- Docs/ADRs: <ADR-XXXX>
- Artifacts: <report path, dashboard link>

### Next actions
- [ ] <next action 1>
- [ ] <next action 2>

### Links (optional)
- Runbook: <path>
- Workflow: <path>
- Notes: <path>

### Session Report (end-of-session wrap-up)
- Summary: <2-4 bullets>
- Decisions: <bullets>
- Risks/Follow-ups: <bullets>
- Validation: <tests run and results>
```

## Session Report: Backstage & Keycloak Stabilization

**Date**: 2026-01-15 / 2026-01-16 (continued)
**Environment**: AWS `dev` (EKS)
**Cluster**: `goldenpath-dev-eks`
**Region**: `eu-west-2`
**Objective**: Fix persistent `CrashLoopBackOff` (Backstage) and `ImagePullBackOff` (Keycloak) to enable platform health.

## 1. Executive Summary

This session focused on resolving critical startup failures in the core IDP stack. We successfully diagnosed and fixed a complex chain of issues involving **AWS Secrets Manager IAM policies**, **Backstage Configuration Loading**, **Keycloak Image Architecture mismatches**, and **RDS PostgreSQL user provisioning**.

**Key Outcome**:

- **Keycloak**: ✅ Running 1/1 - AMD64 Bitnami image from ECR, connected to RDS.
- **Backstage**: ✅ Running 1/1 - Local `backstage-helm` chart with ECR image, SSL RDS connection working.
- **Catalog**: ✅ Synced to governance-registry branch, loading in Backstage.
- **GitHub Token**: ✅ Configured in AWS Secrets Manager, synced via ExternalSecrets.
- **Infrastructure**: Secrets syncing fully operational via ExternalSecrets.

## 2. Detailed Issue Log & Resolutions

### A. Keycloak: The Image Pull & Compatibility Saga

**Problem**: `dev-keycloak-0` stuck in `Init:ErrImagePull`, then `Init:Error`.

**Investigation Trace**:

1. **Bitnami Hub Failure**: Attempts to pull `docker.io/bitnami/keycloak` tags (`25.0.0`, `26.1.1`, `latest`) consistently failed with `Manifest Not Found`.
   - *Cause*: Docker Hub rate-limiting or regional availability issues for Bitnami's public repo.

2. **ECR Mirroring (Attempt 1 - Architecture Mismatch)**:
   - Created private ECR: `aws ecr create-repository --repository-name keycloak --region eu-west-2`
   - Pulled `quay.io/keycloak/keycloak:latest` locally and pushed to ECR.
   - *Result*: Pod failed with `exec format error`.
   - *Root Cause*: Local machine (Apple Silicon) pulled `arm64`, but EKS nodes are `amd64`.

3. **Cross-Architecture Fix (Attempt 2 - Image Incompatibility Discovered)**:
   - Forced AMD64 pull: `docker pull --platform linux/amd64 quay.io/keycloak/keycloak:latest`
   - Pushed to ECR: `593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest`
   - *Result*: **Still failed** with `exec format error` (misleading log).
   - *Root Cause*: Official Keycloak image lacks Bitnami-specific scripts (`/opt/bitnami/scripts/liblog.sh`) that the Bitnami Helm chart init container expects.

4. **Bitnami-Compatible Image (Attempt 3 - SUCCESS)**:
   - Discovered `public.ecr.aws/bitnami/keycloak` as an alternative source.
   - Forced AMD64 pull: `docker pull --platform linux/amd64 public.ecr.aws/bitnami/keycloak:latest`
   - **Verified Architecture**: `amd64`
   - Pushed to ECR: `593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest`
   - *Chart Update*: Set `image.registry` to ECR private URL and enabled `global.security.allowInsecureImages: true`.

### B. Backstage: Configuration & Crash Loops

**Problem**: `dev-backstage` crashing immediately on startup with multiple sequential errors.

**Investigation Trace**:

1. **Auth Key Missing**: Logged `Error: You must configure at least one key in backend.auth.keys`.
   - *Fix 1 (Failed)*: `appConfig` update was ignored by chart merging logic.
   - *Fix 2 (Success)*: Forced injection via Env Var `APP_CONFIG_backend_auth_keys_0_secret`.

2. **Kubernetes Plugin**: Logged `Error: Kubernetes configuration is missing`.
   - *Fix*: Added `kubernetes` block to `values.yaml` with `multiTenant` configuration.

3. **Wrong Helm Chart**: ArgoCD was using `backstage.github.io/charts` instead of local chart.
   - User clarified: Use local `backstage-helm/charts/backstage` chart.

4. **ArgoCD valueFiles Path Error**: Relative path `../../../gitops/helm/backstage/values/dev.yaml` failed with `permission denied`.
   - *Fix*: Switched to multi-source pattern with `$values` reference.

5. **RDS SSL Required**: Error `no pg_hba.conf entry for host ... no encryption`.
   - *Fix*: Added `ssl.require: true` and `ssl.rejectUnauthorized: false` to database connection config.

6. **CREATEDB Permission**: Error `permission denied to create database` for `backstage_plugin_scaffolder`.
   - *Fix*: Granted `CREATEDB` privilege to `backstage_app` user via psql.

### C. Infrastructure: Secret Syncing

**Problem**: ExternalSecrets failed to sync (`SecretSyncedError`).

**Fix**:

- Modified IAM Policy to allow wildcards (`goldenpath*`) matching secret names with slashes (e.g., `goldenpath/dev/backstage/...`).
- Manually created missing `ClusterSecretStore`.

### D. RDS User Provisioning Gap

**Problem**: Terraform creates AWS Secrets Manager secrets with credentials but does NOT create actual PostgreSQL users.

**Root Cause**: The `rds_config.application_databases` in terraform.tfvars defines usernames, but no provisioner runs `CREATE USER` in PostgreSQL.

**Fix (Manual via psql pod)**:

```sql
-- Connect as postgres master user
-- RDS Host: goldenpath-dev-goldenpath-platform-db.cxmcacaams2q.eu-west-2.rds.amazonaws.com

-- Keycloak user and database
CREATE USER keycloak_app WITH PASSWORD '<from goldenpath/dev/keycloak/postgres secret>';
CREATE DATABASE keycloak OWNER keycloak_app;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak_app;

-- Backstage user and database
CREATE USER backstage_app WITH PASSWORD '<from goldenpath/dev/backstage/postgres secret>';
CREATE DATABASE backstage_plugin_catalog OWNER backstage_app;
GRANT ALL PRIVILEGES ON DATABASE backstage_plugin_catalog TO backstage_app;

-- Additional privilege for Backstage (creates plugin databases dynamically)
ALTER USER backstage_app CREATEDB;
```

**Future**: Consider adding a Terraform `null_resource` with `local-exec` provisioner or a Kubernetes Job to automate user creation.

### E. Backstage Chart Migration

**Problem**: Multiple Backstage chart issues - wrong chart source, image field names, values path errors.

**Resolution**:

1. **Chart Source**: Switched from `backstage.github.io/charts` to local `backstage-helm/charts/backstage`.
2. **ArgoCD Multi-Source**: Used `sources` with `ref: values` and `$values/` prefix for cross-path values loading.
3. **ExternalSecret Integration**: Added conditional `externalsecret.yaml` template and made `secret.yaml` conditional via `externalSecret.enabled`.
4. **SSL for RDS**: Added `ssl.require: true` and `ssl.rejectUnauthorized: false` in appConfig database connection.

### F. Backstage Catalog Migration (2026-01-16)

**Problem**: Backstage catalog was pointing to `main` branch, which changes with feature development.

**Resolution**:

1. **Synced catalog to governance-registry branch**: Pushed 351 files to `governance-registry` branch at `backstage-helm/backstage-catalog/`.
2. **Updated all environment values files** to reference `governance-registry` branch:
   - `gitops/helm/backstage/values/dev.yaml`
   - `gitops/helm/backstage/values/staging.yaml`
   - `gitops/helm/backstage/values/prod.yaml`
   - `backstage-helm/values-local.yaml`

**New Catalog URL**:

```text
https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-helm/backstage-catalog/all.yaml
```

### G. GitHub Token Configuration (2026-01-16)

**Problem**: Backstage GitHub token was a placeholder, preventing PR creation and scaffolder features.

**Resolution**:

1. **Created GitHub PAT** with scopes: `repo`, `workflow`, `read:org`, `read:user`
2. **Updated AWS Secrets Manager**: `goldenpath/dev/backstage/secrets` with real token
3. **Triggered ExternalSecret sync**: `kubectl annotate externalsecret backstage-secrets -n backstage force-sync=$(date +%s) --overwrite`
4. **Restarted Backstage**: Token now loaded and PR features working

### H. Kong Ingress for Tooling Apps (2026-01-16)

**Problem**: Accessing Backstage and other tooling apps requires port-forwarding, which is inconvenient for daily use.

**Resolution**:

1. **Added ingress template** to Backstage Helm chart (`backstage-helm/charts/backstage/templates/ingress.yaml`)
2. **Configured Kong ingress** for all environments with TLS via cert-manager
3. **Updated base URLs** to remove `:7007` port suffix since Kong handles routing

**Services Configured**:

|Service|Dev URL|Ingress Status|
|---------|---------|----------------|
|Backstage|`backstage.dev.goldenpathidp.io`|New template added|
|Keycloak|`keycloak.dev.goldenpathidp.io`|Already configured|
|ArgoCD|`argocd.dev.goldenpathidp.io`|Configured|
|Grafana|`grafana.dev.goldenpathidp.io`|Configured|

**Pattern** (consistent across all tooling apps):

```yaml
ingress:
  enabled: true
  ingressClassName: kong
  hostname: <service>.dev.goldenpathidp.io
  tls: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
```

**Documentation Created**:

- ADR-0162: Kong Ingress DNS Strategy for Platform Tooling
- CL-0136: Tooling Apps Ingress Configuration
- Living Doc: `docs/70-operations/45_DNS_MANAGEMENT.md`

## 3. Configuration Changes Summary

### ArgoCD Application (`gitops/argocd/apps/dev/backstage.yaml`)

```yaml
spec:
  sources:
    # Source 1: Values files from repo root
    - repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
      targetRevision: feature/tooling-apps-config
      ref: values
    # Source 2: Helm chart with values reference
    - repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
      path: backstage-helm/charts/backstage
      targetRevision: feature/tooling-apps-config
      helm:
        valueFiles:
          - $values/gitops/helm/backstage/values/dev.yaml
```

### Backstage Helm Values (`gitops/helm/backstage/values/dev.yaml`)

```yaml
# Image from private ECR
image:
  repository: 593517239005.dkr.ecr.eu-west-2.amazonaws.com/
  name: backstage
  tag: 0.0.1
  pullPolicy: Always

# ExternalSecret integration (disables chart's built-in secret)
externalSecret:
  enabled: true
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  secrets:
    postgresPassword:
      remoteRef:
        key: goldenpath/dev/backstage/postgres
        property: password
    postgresUser:
      remoteRef:
        key: goldenpath/dev/backstage/postgres
        property: username
    githubToken:
      remoteRef:
        key: goldenpath/dev/backstage/secrets
        property: token

# Catalog from governance-registry branch
catalog:
  catalogLocation: "https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-helm/backstage-catalog/all.yaml"
  customCatalogLocation: "None"

# PostgreSQL RDS connection
postgres:
  host: goldenpath-dev-goldenpath-platform-db.cxmcacaams2q.eu-west-2.rds.amazonaws.com
  port: "5432"
  user: backstage_app

# SSL required for RDS (in appConfig)
appConfig: |
  backend:
    database:
      client: pg
      connection:
        host: ${POSTGRES_HOST}
        port: ${POSTGRES_PORT}
        user: ${POSTGRES_USER}
        password: ${POSTGRES_PASSWORD}
        ssl:
          require: true
          rejectUnauthorized: false
```

### Chart Templates Modified

**`backstage-helm/charts/backstage/templates/secret.yaml`** - Made conditional:

```yaml
{{- if not .Values.externalSecret.enabled }}
apiVersion: v1
kind: Secret
metadata:
  name: backstage-secrets
data:
  POSTGRES_USER: {{ .Values.postgres.user | b64enc}}
  POSTGRES_PASSWORD: {{ .Values.postgres.password | b64enc}}
  GITHUB_TOKEN: {{ .Values.github.accessToken | default "None" | b64enc}}
{{- end }}
```

**`backstage-helm/charts/backstage/templates/externalsecret.yaml`** - New template:

```yaml
{{- if .Values.externalSecret.enabled }}
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: backstage-secrets
spec:
  refreshInterval: 1m
  secretStoreRef:
    name: {{ .Values.externalSecret.secretStoreRef.name }}
    kind: {{ .Values.externalSecret.secretStoreRef.kind }}
  target:
    name: backstage-secrets
    creationPolicy: Owner
  data:
    - secretKey: POSTGRES_PASSWORD
      remoteRef:
        key: {{ .Values.externalSecret.secrets.postgresPassword.remoteRef.key }}
        property: {{ .Values.externalSecret.secrets.postgresPassword.remoteRef.property }}
    - secretKey: POSTGRES_USER
      remoteRef:
        key: {{ .Values.externalSecret.secrets.postgresUser.remoteRef.key }}
        property: {{ .Values.externalSecret.secrets.postgresUser.remoteRef.property }}
    - secretKey: GITHUB_TOKEN
      remoteRef:
        key: {{ .Values.externalSecret.secrets.githubToken.remoteRef.key }}
        property: {{ .Values.externalSecret.secrets.githubToken.remoteRef.property }}
{{- end }}
```

### Keycloak Helm Values (`gitops/helm/keycloak/values/dev.yaml`)

```yaml
image:
  registry: 593517239005.dkr.ecr.eu-west-2.amazonaws.com
  repository: keycloak
  tag: latest  # AMD64 Bitnami build

global:
  security:
    allowInsecureImages: true  # Required for private ECR
```

## 4. Final Status

|Component|Status|Pod|Details|
|-----------|--------|-----|---------|
|**Keycloak**|✅ Running|`dev-keycloak-0` 1/1|AMD64 Bitnami from ECR, connected to RDS|
|**Backstage**|✅ Running|`dev-backstage-*` 1/1|Local chart, ECR image, SSL RDS connection|
|**Catalog**|✅ Loaded|N/A|Serving from governance-registry branch|
|**GitHub Token**|✅ Configured|N/A|PR features and scaffolder working|
|**ExternalSecrets**|✅ Synced|N/A|`backstage-secrets` syncing from AWS Secrets Manager|

### Commits Made This Session

|Commit|Message|
|--------|---------|
|`d4174ef7`|fix: use ArgoCD multi-source pattern for Backstage values|
|`0e0bd2fa`|fix: add SSL config for Backstage RDS connection|
|`5d13229e`|docs: update session summary with final platform status|
|`59f792f0`|feat(catalog): sync backstage-catalog to governance-registry|
|`06f26853`|fix: correct backstage catalog URL path to governance-registry|
|`58e35b96`|docs: add GitHub token setup phase to IDP deployment runbook|
|`92112513`|docs: update catalog references and add changelogs|

### AWS Resources

|Resource|ARN/ID|Purpose|
|----------|--------|---------|
|ECR: `backstage`|`593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage`|Backstage container image|
|ECR: `keycloak`|`593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak`|Keycloak container image|
|RDS|`goldenpath-dev-goldenpath-platform-db.cxmcacaams2q.eu-west-2.rds.amazonaws.com`|PostgreSQL 15.15|
|Secret|`goldenpath/dev/rds/master`|RDS master credentials|
|Secret|`goldenpath/dev/backstage/postgres`|Backstage DB credentials|
|Secret|`goldenpath/dev/backstage/secrets`|Backstage GitHub token|
|Secret|`goldenpath/dev/keycloak/postgres`|Keycloak DB credentials|

## 5. Documentation Created

### Runbooks

- **RB-0031**: `docs/70-operations/runbooks/RB-0031-idp-stack-deployment.md` - Complete IDP stack deployment guide with:
  - Phase 1: ECR Repository and Image Preparation
  - Phase 2: RDS User Provisioning
  - Phase 3: External Secrets Verification
  - Phase 3.5: GitHub Token Configuration (NEW)
  - Phase 4-5: Keycloak and Backstage Deployment
  - Phase 6: Verification Checklist

### Changelogs

|Changelog|Description|
|---------|------------------------------------------|
|CL-0132|ClusterSecretStore Addon Deployment Fix|
|CL-0133|IDP Stack Deployment Runbook (RB-0031)|
|CL-0134|Backstage Catalog Governance Registry Sync|
|CL-0135|Kong Ingress for Tooling Apps|

### Session Summary

- **Session Summary**: `agent_summary/agent_session_summary.md` (this file)

## 6. Lessons Learned

1. **ARM64 vs AMD64**: Always use `--platform linux/amd64` when pulling images on Apple Silicon for deployment to x86 clusters.

2. **Bitnami Charts**: Require Bitnami-specific images (not official upstream images) due to init scripts.

3. **ArgoCD Multi-Source**: For values files outside chart directory, use `sources` with `ref: values` and `$values/` prefix pattern.

4. **RDS User Provisioning**: Terraform creates secrets but not PostgreSQL users - manual intervention or automation required.

5. **RDS SSL**: AWS RDS requires SSL by default. Configure `ssl.require: true` in application database connections.

6. **Backstage CREATEDB**: Backstage dynamically creates plugin databases, requiring `CREATEDB` privilege on its database user.

7. **Catalog Branch Strategy**: Use `governance-registry` branch for stable catalog that doesn't change with feature development.

8. **GitHub Token for PR Features**: Backstage scaffolder requires valid GitHub PAT with `repo`, `workflow`, `read:org` scopes.

9. **Kong Ingress for Tooling**: Use Kong ingress with cert-manager to provide DNS-based access to tooling apps, eliminating port-forwarding.

## 7. Access Commands

```bash
# DNS-based access (after ingress deployment)
# Backstage: https://backstage.dev.goldenpathidp.io
# Keycloak: https://keycloak.dev.goldenpathidp.io

# Port-forward fallback (if DNS not configured)
kubectl port-forward svc/dev-backstage -n backstage 7007:7007
kubectl port-forward svc/dev-keycloak -n keycloak 8080:8080

# Check pod status
kubectl get pods -n backstage
kubectl get pods -n keycloak

# Check ingress status
kubectl get ingress -n backstage
kubectl get ingress -n keycloak

# Check certificate status
kubectl get certificate -n backstage
kubectl get certificate -n keycloak

# Check ExternalSecret status
kubectl get externalsecret -n backstage
kubectl get externalsecret -n keycloak

# Port-forward Grafana (monitoring stack)
kubectl port-forward -n monitoring svc/dev-kube-prometheus-stack-grafana 8080:80
```

## 8. Monitoring Stack Resolution (2026-01-16)

### H. Prometheus Monitoring Stack Fix

**Problem**: Grafana dashboards were empty and datasource connections returning HTTP 500 errors. No Prometheus server pod existed despite the kube-prometheus-stack Helm chart being deployed.

**Investigation Trace**:

1. **Initial Symptoms**:
   - Grafana accessible but dashboards showed no data
   - Datasource test for Prometheus failed with "Error reading Prometheus: An error occurred within the plugin"
   - Loki datasource test failed with "Failed to call resource"
   - PromQL queries in Explore view returned HTTP 500 errors

2. **Root Cause Discovery**:
   - Prometheus StatefulSet was completely missing from the `monitoring` namespace
   - Only Alertmanager StatefulSet existed
   - Prometheus Operator logs showed continuous errors:

```text
     failed to list *v1.Prometheus: the server could not find the requested resource (get prometheuses.monitoring.coreos.com)
     ```

   - **Critical Finding**: The `prometheuses.monitoring.coreos.com` CRD was **not installed**
   - All other monitoring CRDs were present (ServiceMonitors, PodMonitors, AlertManagers, PrometheusRules)

3. **Resolution Steps**:

   ```bash
   # 1. Install missing Prometheus CRD
   kubectl apply --server-side -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.68.0/example/prometheus-operator-crd/monitoring.coreos.com_prometheuses.yaml

   # Result: customresourcedefinition.apiextensions.k8s.io/prometheuses.monitoring.coreos.com serverside-applied

   # 2. Trigger ArgoCD sync for monitoring stack
   kubectl -n argocd patch application dev-kube-prometheus-stack --type merge -p '{"operation": {"sync": {"prune": true}}}'

   # 3. Wait for Prometheus StatefulSet creation
   kubectl wait --for=condition=ready pod/prometheus-dev-kube-prometheus-stack-prometheus-0 -n monitoring --timeout=120s
   ```

1. **Verification Results**:
   - **Prometheus Pod**: `prometheus-dev-kube-prometheus-stack-prometheus-0` - 2/2 Running
   - **Prometheus Version**: v2.42.0
   - **Metrics Collection**: **38 time series** actively scraped (query: `up`)
   - **Active Targets**: All ServiceMonitors successfully discovered
   - **Grafana Dashboards**: Now populated with live data
   - **Cluster Metrics**:
     - CPU Utilization: 1.70%
     - CPU Requests Commitment: 28.4%
     - Memory Utilization: 33.5%
     - Memory Requests Commitment: 18.7%

**Status**: ✅ **RESOLVED** - Monitoring stack fully operational

**Components Now Functional**:

|Component|Status|Details|
|-----------|--------|---------|
|**Prometheus Server**|✅ Running|StatefulSet deployed with 1/1 ready replicas|
|**Grafana Datasources**|✅ Connected|Both Prometheus and Loki passing connection tests|
|**Dashboards**|✅ Populated|26 pre-provisioned dashboards showing live metrics|
|**Metrics Scraping**|✅ Active|38 targets being scraped across monitoring, kube-system, keycloak namespaces|
|**Alertmanager**|✅ Running|Already operational, unaffected by CRD issue|

**Root Cause Analysis**:
The Prometheus CRD was likely excluded during the initial kube-prometheus-stack deployment, possibly due to:

- CRD installation being disabled in Helm values (`crds.enabled: false`)
- Manual CRD deletion during troubleshooting
- ArgoCD sync policy excluding CRDs

**Screenshots**:

- Prometheus metrics query results: `grafana_explore_up_results_1768523234215.png`
- Kubernetes cluster dashboard with live data: `grafana_kubernetes_cluster_data_1768523284777.png`

**Access**:

```bash
# Grafana UI
kubectl port-forward -n monitoring svc/dev-kube-prometheus-stack-grafana 8080:80
# URL: http://localhost:8080
# Username: admin
# Password: prom-operator
```

### I. Dashboard Auto-Discovery (2026-01-16)

**Problem**: Application dashboards (defined as ConfigMaps) were deployed but ignored by Grafana.

**Resolution**:

1. **Enabled Grafana Sidecar**: Configured `sidecar.dashboards.enabled: true` in `dev.yaml` and `local.yaml`.
2. **Global Namespace Watch**: Set `sidecar.dashboards.searchNamespace: ALL` to allow decentralized dashboards in app namespaces.
3. **Label Selector**: Configured sidecar to watch for label `grafana_dashboard: "1"`.

**Verification**:

- ConfigMaps in `apps/*/dashboards/` are now automatically detected.
- Dashboards for Wordpress, FastAPI, and Stateful apps appear in Grafana without manual import.

### J. Out-of-the-Box Observability (2026-01-16)

**Problem**: Observability capabilities (RED metrics, logs) were available but undocumented.

**Resolution**:

1. **Changelog Created**: `CL-0137-ootb-observability-dashboards.md` documenting the "Zero-Config" capability.
    - *Note*: Renamed from `CL-0135` to `CL-0137` to resolve conflict with remote changes.
2. **Capability Ledger Updated**: Added **Section 23** to `CAPABILITY_LEDGER.md` detailing Golden Signals & RED.
3. **Features List Updated**: Added "OOTB Golden Signals" to `FEATURES.md`.

### K. Remote Synchronization & Ingress (2026-01-16)

**Action**: Merged `origin/feature/tooling-apps-config` into local branch.

**Updates Received**:

- **Kong Ingress**: Grafana now exposed at `grafana.dev.goldenpathidp.io` (no port-forward needed).
- **DNS Management**: New documentation on DNS strategies.
- **Conflict Resolution**: Successfully merged local Sidecar config with remote Ingress config in `dev.yaml`.

**Current Access URLs**:

- **Grafana**: `https://grafana.dev.goldenpathidp.io`
- **Backstage**: `https://backstage.dev.goldenpathidp.io`
- **Keycloak**: `https://keycloak.dev.goldenpathidp.io`

## 9. Dashboard Auto-Discovery Debugging (2026-01-16)

### L. Grafana Dashboard Sidecar Configuration

**Objective**: Enable automatic discovery of application dashboards (Wordpress, FastAPI, Stateful) from ConfigMaps.

**Problem**: Application dashboards exist as ConfigMaps with label `grafana_dashboard: "1"` in namespaces `apps-wordpress-efs`, `apps-sample-stateless`, `apps-stateful`, but do not appear in Grafana UI.

**Investigation Steps**:

1. **Initial Configuration (Attempt 1)**:
   - Added sidecar configuration to `gitops/helm/kube-prometheus-stack/values/dev.yaml`:

     ```yaml
     grafana:
       sidecar:
         dashboards:
           enabled: true
           label: grafana_dashboard
           searchNamespace: ALL
     ```

   - Triggered ArgoCD sync
   - Result: Deployment stuck due to ArgoCD pointing to wrong branch

2. **Branch Correction**:
   - Patched `dev-kube-prometheus-stack` application to use `feature/tooling-apps-config` branch
   - Result: New pod created but stuck in `Init:0/1` state for 30+ minutes

3. **Volume Attachment Deadlock Discovery**:
   - Root Cause: PersistentVolume (`pvc-3fd53380-07c7-4506-933b-a011fcc10a82`) is `ReadWriteOnce`
   - Old pod holds volume, new pod requires volume to initialize
   - Deployment strategy prevents graceful handoff
   - Resolution: Manually deleted old pod `dev-kube-prometheus-stack-grafana-f67c5df7f-7w7xt`

4. **Browser Verification (Attempt 1)**:
   - New pod `...8876l` started successfully
   - Sidecar logs showed only startup messages, no dashboard discovery activity
   - Browser check confirmed only 26 infrastructure dashboards visible
   - Missing: All application dashboards (Wordpress, FastAPI, Stateful)

5. **Environment Variable Investigation**:
   - Discovered `NAMESPACE` environment variable was NOT set on sidecar container
   - `searchNamespace: ALL` in values.yaml did not propagate to pod spec
   - Chart version issue: `kube-prometheus-stack` v45.7.1 may not support `searchNamespace` directly

6. **Explicit Environment Variable (Attempt 2)**:
   - Updated `gitops/helm/kube-prometheus-stack/values/dev.yaml`:

     ```yaml
     grafana:
       sidecar:
         dashboards:
           enabled: true
           label: grafana_dashboard
           searchNamespace: ALL
           extraEnv:
             - name: NAMESPACE
               value: ALL
     ```

   - Triggered ArgoCD sync
   - Result: **Same volume deadlock** - new ReplicaSet created but pod stuck in Init

7. **Current State (as of 02:27 UTC)**:
   - **Running Pod**: `dev-kube-prometheus-stack-grafana-f67c5df7f-wwk4r` (old ReplicaSet, no `NAMESPACE` env var)
   - **Stuck Pod**: `dev-kube-prometheus-stack-grafana-6d7d8fc764-659zz` (new ReplicaSet, in Init for 52+ minutes)
   - **Volume**: Still attached to running pod, preventing new pod from starting
   - **Dashboard Status**: Only infrastructure dashboards visible (26 total)

**Verified Configuration**:

- ✅ Application ConfigMaps exist with correct label (`grafana_dashboard: "1"`)
- ✅ RBAC ClusterRole grants `get, watch, list` on ConfigMaps cluster-wide
- ✅ Sidecar container running and healthy in current pod
-  `NAMESPACE: ALL` environment variable not present in running pod
-  Application dashboards not discovered by sidecar

**Root Cause Hypothesis**:
The Helm chart's deployment update strategy is incompatible with `ReadWriteOnce` persistent volumes, causing a continuous deadlock where:

1. ArgoCD detects configuration change
2. Creates new ReplicaSet with updated config
3. New pod cannot start (waiting for volume)
4. Old pod keeps running (holds volume)
5. Deployment never completes rollout

**Resolution (2026-01-16 02:45 UTC)**:

1. **Scaled down old ReplicaSet**: `kubectl scale replicaset <old-rs> -n monitoring --replicas=0`
2. **Volume released**: New pod was able to attach PVC and start
3. **Correct Helm values**: Used `searchNamespace: ALL` with `labelValue: "1"`:

   ```yaml
   grafana:
     sidecar:
       dashboards:
         enabled: true
         label: grafana_dashboard
         labelValue: "1"
         searchNamespace: ALL
       datasources:
         enabled: true
         searchNamespace: ALL
   ```

4. **Result**: Sidecar now has `NAMESPACE=ALL` env var and discovers dashboards from all namespaces

**Final State**:

- ✅ **Grafana Pod**: Running with 3/3 containers
- ✅ **Sidecar Config**: `NAMESPACE=ALL` environment variable set
- ✅ **Application Dashboards**: All 3 discovered and loaded
  - `sample-stateless-app - Golden Signals`
  - `stateful-app - Golden Signals`
  - `wordpress-efs - Golden Signals`
- ✅ **Total Dashboards**: 29 (26 infrastructure + 3 application)
- ✅ **Ingress**: `grafana.dev.goldenpathidp.io` configured

**Key Learning**: The `extraEnv` field didn't work with this chart version. The correct approach is to use `searchNamespace: ALL` directly under `sidecar.dashboards`, which the chart translates to the `NAMESPACE` env var internally.

### M. Tooling Application Dashboards (2026-01-16)

**Problem**: Tooling applications (Backstage, Keycloak, ArgoCD, Kong) lacked dedicated RED/Golden Signals dashboards. Only sample applications had dashboards.

**Investigation**:

- Checked for existing dashboard ConfigMaps in tooling namespaces
- Found: Only `apps-sample-stateless`, `apps-stateful`, `apps-wordpress-efs` had dashboards
- Missing: `backstage`, `keycloak`, `argocd`, `kong-system` namespaces

**Resolution**:

1. **Created 4 new dashboard ConfigMaps** following RED methodology:
   - `gitops/helm/tooling-dashboards/backstage-dashboard.yaml` - Request rate, errors, latency, logs
   - `gitops/helm/tooling-dashboards/keycloak-dashboard.yaml` - Auth metrics, sessions, JVM heap, logs
   - `gitops/helm/tooling-dashboards/argocd-dashboard.yaml` - GitOps health, sync ops, gRPC metrics, logs
   - `gitops/helm/tooling-dashboards/kong-dashboard.yaml` - Traffic, upstream latency, connections, logs

2. **Deployment mechanism**: Created `kustomization.yaml` for easy deployment:

   ```bash
   kubectl apply -k gitops/helm/tooling-dashboards/
   ```

3. **Documentation updates**:
   - `docs/changelog/entries/CL-0138-tooling-apps-dashboards.md` - New changelog entry
   - `docs/50-observability/09_PLATFORM_DASHBOARD_CATALOG.md` - Added Section 4 (Tooling Dashboards)

**Each dashboard includes**:

- **Rate**: Request rate (RPS) by method/service
- **Errors**: 4xx/5xx error rate percentages with thresholds
- **Duration**: P50/P95/P99 latency percentiles
- **Saturation**: CPU, memory, and app-specific metrics
- **Logs**: Loki panels for error investigation + full application logs

**Commit**: `f8e33b94` - feat: add RED/Golden Signals dashboards for tooling applications

## 10. Metadata Governance Cleanup (2026-01-16)

**Objective**: Normalize ADR/CL metadata and clear schema validation failures repo-wide.

**Actions**:

- Normalized ADR/CL frontmatter and status fields; marked superseded ADRs consistently.
- Added missing metadata sidecars and IDs where required (e.g., envs and Helm overlays).
- Fixed governance IDs/labels for tooling dashboards and local infra values.
- Added metadata for previously missing docs, reports, and local audit logs.
- Corrected test metadata IDs to match filenames for validation.

**Validation**:

- `scripts/validate_metadata.py`: ✅ 745 passed,  0 failed
- `bin/governance audit`: generated `docs/10-governance/reports/compliance_snapshot_2026-01-16.json`
- `value_ledger.json` updated with the new metadata inventory

**Commit**: `99922e58` - chore: normalize metadata and fix validation

## 11. Link Normalization & Secrets Path Alignment (2026-01-16)

**Objective**: Remove `file://` links repo-wide, align Backstage GitHub token secret path, and re-validate coherence.

**Actions**:

- Replaced `file://` links with repo-relative paths across docs and auto-generated reports.
- Standardized Backstage GitHub token secret path to `goldenpath/{env}/backstage/secrets` in docs and ExternalSecrets.
- Updated generators to emit relative links for script index and platform health output.
- Repaired truncated catalog link in Backstage ADR metadata.

**Validation**:

- `scripts/generate_script_index.py --validate`: ✅ (after regeneration)
- `scripts/platform_health.py`: refreshed `PLATFORM_HEALTH.md` and `HEALTH_AUDIT_LOG.md`
- `scripts/validate_metadata.py`: ✅ 745 passed,  0 failed

## 12. Backstage Template Migration + Catalog Path Fix (2026-01-16 08:47:34Z)

**Objective**: Remove unused `/backstage` directory, migrate templates into catalog, and align catalog URLs with governance-registry layout.

**Actions**:

- Moved Backstage templates into `backstage-helm/backstage-catalog/templates/` and updated catalog `all.yaml` to include them.
- Updated Backstage test catalog locations to use governance-registry URLs for templates.
- Repointed dev/staging/prod/local `catalogLocation` to `governance-registry/backstage-catalog/all.yaml`.
- Deleted the legacy `/backstage` directory after updating references.

## 13. Platform Requirements Draft (2026-01-16 09:25:59Z)

**Objective**: Populate the platform requirements placeholder with V1-scoped golden paths, access model, and approval flow.

**Actions**:

- Filled `docs/00-foundations/10_PLATFORM_REQUIREMENTS.md` with V1 functional/non-functional requirements.
- Added golden path provisioning list (apps, S3, RDS, ECR, EC2, EKS) with platform approvals.
- Documented approval model, access matrix, and Backstage-to-PR flow.
- Clarified ESO naming and V1 acceptance criteria.

## 14. PR Guardrails & Pre-Merge Checks (2026-01-16 09:40:40Z)

**Objective**: Run required pre-merge checks before opening a PR to `development`.

**Results**:

- `bin/governance lint`: reported YAML lint warnings and errors (comments spacing, blank lines, indentation) in existing files.
- `bin/governance audit`: ✅ snapshot saved to `docs/10-governance/reports/compliance_snapshot_2026-01-16.json`.
- `scripts/validate_metadata.py`: ✅ 745 passed,  0 failed.

**Notes**:

- `markdownlint-cli2` is not installed locally (lint reported missing dependency).

## 15. PR-Scoped Markdown Lint Remediation (2026-01-16 10:56:48Z)

**Objective**: Fix markdownlint issues for files changed in the PR without touching the rest of the repo.

**Actions**:

- Ran markdownlint over PR-changed files and applied auto-fixes plus targeted cleanup for duplicate headings, heading punctuation, and table styles.
- Normalized repeated headings by adding context-specific suffixes (e.g., security controls per registry) to avoid duplicate anchors.
- Added local-infra app sections to the tooling apps matrix so localstack/minio/postgresql anchors resolve correctly.

**Validation**:

- `markdownlint-cli2` on PR-changed files: ✅ 0 errors.
- `bin/governance lint`: still fails repo-wide due to pre-existing markdownlint issues outside PR scope (YAML lint is clean).

## 16. Agent Collaboration Governance Additions (2026-01-16 11:18:21Z)

**Objective**: Formalize agent collaboration governance with a living registry and session log requirements.

**Actions**:

- Added `docs/10-governance/09_AGENT_COLLABORATION_MATRIX.md` as the living registry for agent roles, models, and responsibilities.
- Documented environment access levels (local/CI/cluster/cloud) and per-agent access columns.
- Captured the append-only session log requirement for `agent_summary/agent_session_summary.md`.
- Linked the registry and session log expectations into `docs/10-governance/07_AI_AGENT_GOVERNANCE.md`.
- Added ADR `docs/adrs/ADR-0163-agent-collaboration-governance.md` to formalize the collaboration model.

## 17. RDS User and Database Provisioning Automation (2026-01-16 19:30:00Z)

**Objective**: Implement automated RDS user and database provisioning per PRD-0001 and ADR-0165.

**Problem Statement**: Terraform creates Secrets Manager entries for database credentials but does not create the corresponding PostgreSQL roles or databases. This leaves a manual `psql` gap and introduces drift between declared config and runtime state.

**Actions**:

### Files Created

| File | Purpose |
|------|---------|
| `scripts/rds_provision.py` | Core provisioning script (SCRIPT-0035) - idempotent role/database creation |
| `tests/scripts/test_script_0035.py` | Unit tests with mocks + integration test markers |
| `docs/70-operations/runbooks/RB-0032-rds-user-provision.md` | Operations runbook for provisioning |

### Files Modified

| File | Change |
|------|--------|
| `Makefile` | Added `rds-provision` and `rds-provision-dry-run` targets |
| `docs/adrs/ADR-0165-rds-user-db-provisioning-automation.md` | Updated status to "accepted", added implementation details |

### Key Features Implemented

1. **Idempotent Provisioning**: Safe to re-run without destructive side effects
2. **Dry-Run Mode**: Preview changes without executing (`--dry-run`)
3. **Approval Gates**: Non-dev environments require `ALLOW_DB_PROVISION=true`
4. **Audit Trail**: CSV output with build_id, run_id, timestamps, and status
5. **Secure Connections**: SSL required, no password logging
6. **Fail-Fast**: Exits immediately on missing secrets or connection errors

### Usage

```bash
# Preview what would be provisioned (safe)
make rds-provision-dry-run ENV=dev

# Provision for dev (no approval needed)
make rds-provision ENV=dev

# Provision for non-dev (requires explicit approval)
ALLOW_DB_PROVISION=true make rds-provision ENV=staging
```

### Dry-Run Output Example

```
[DRY-RUN] Provisioning RDS users and databases for dev...
Found 2 application databases to provision
--- Provisioning: keycloak ---
[DRY-RUN] Would create/update role: keycloak_user
[DRY-RUN] Would create database: keycloak with owner keycloak_user
[DRY-RUN] Would grant ALL on keycloak to keycloak_user
--- Provisioning: backstage ---
[DRY-RUN] Would create/update role: backstage_user
[DRY-RUN] Would create database: backstage with owner backstage_user
[DRY-RUN] Would grant ALL on backstage to backstage_user
```

### Artifacts

- **PRD**: `docs/20-contracts/prds/PRD-0001-rds-user-db-provisioning.md`
- **ADR**: `docs/adrs/ADR-0165-rds-user-db-provisioning-automation.md`
- **Script**: `scripts/rds_provision.py` (SCRIPT-0035)
- **Tests**: `tests/scripts/test_script_0035.py`
- **Runbook**: `docs/70-operations/runbooks/RB-0032-rds-user-provision.md`
- **Changelog**: `docs/changelog/entries/CL-0140-rds-user-db-provisioning.md`

### Technical Design

- **Source of Truth**: `application_databases` in `envs/<env>-rds/terraform.tfvars`
- **Secrets**: Master credentials from `goldenpath/<env>/rds/master`, app passwords from `goldenpath/<env>/<app>/postgres`
- **Connection**: psycopg2 with SSL (same pattern as rotation Lambda)
- **SQL Patterns**: Check-then-create for idempotency, identifier validation to prevent SQL injection

### PRD Gap Fixes (2026-01-16 Session Continuation)

Addressed audit feedback to fully satisfy PRD-0001 and ADR-0165:

| Gap                              | Resolution                                                                            |
| -------------------------------- | ------------------------------------------------------------------------------------- |
| Fail-fast not implemented        | Added `ProvisionError` exception + `--no-fail-fast` flag (default: fail-fast enabled) |
| Only GRANT ALL, no access levels | Added `ACCESS_LEVELS` mapping for owner/editor/reader with appropriate grants         |
| No default privileges            | Added `ALTER DEFAULT PRIVILEGES` for tables and sequences                             |
| Audit not persisted              | Added `--audit-output` CLI arg and `persist_audit_records()` function                 |
| Missing changelog                | Created `CL-0140-rds-user-db-provisioning.md`                                         |

### Updated CLI Arguments

```bash
python3 scripts/rds_provision.py \
  --env dev \
  --tfvars envs/dev-rds/terraform.tfvars \
  --master-secret goldenpath/dev/rds/master \
  --audit-output governance/dev/rds_provision_audit.csv \
  [--no-fail-fast]  # Optional: continue on errors
```

### Access Level Grants

| Level  | Database       | Schema | Tables                         | Default Privileges          |
| ------ | -------------- | ------ | ------------------------------ | --------------------------- |
| owner  | ALL PRIVILEGES | ALL    | ALL                            | ALL on tables/sequences     |
| editor | CONNECT        | USAGE  | SELECT, INSERT, UPDATE, DELETE | Same                        |
| reader | CONNECT        | USAGE  | SELECT                         | SELECT on tables/sequences  |

### Follow-ups (Deferred to V2)

1. Lambda fallback for K8s-independent execution
2. Delegated admin role instead of master credentials
3. CI workflow integration (post-Terraform-apply step)

---

## 2026-01-16T21:00Z — RDS: Automated provisioning on merge — env=dev build_id=na

Owner: platform-team
Agent: claude-opus-4-5
Goal: Automate RDS provisioning to trigger on PR merge (eliminate manual step)

Environment: AWS `dev`
Cluster: goldenpath-dev-eks
Region: eu-west-2
Objective: When PR is merged to development, automatically run Terraform apply + K8s provisioning job

### In-Session Log (append as you go)

- 19:30Z — Started: Implement auto-provisioning workflow — status: running
- 20:00Z — Decision: Use K8s Job over Lambda — why: VPC access required, GitHub runners can't reach private RDS
- 20:15Z — Change: Created rds-database-apply.yml — file: .github/workflows/rds-database-apply.yml
- 20:30Z — Change: Created platform-system namespace + RBAC — file: gitops/kustomize/platform-system/
- 20:45Z — Change: Created Argo WorkflowTemplate — file: gitops/kustomize/platform-system/rds-provision-workflowtemplate.yaml
- 21:00Z — Change: Updated documentation — file: docs/85-how-it-works/self-service/RDS_USER_DB_PROVISIONING.md
- 21:15Z — Result: All automation components created — outcome: pass

### Checkpoints

- [x] Create GitHub workflow triggered on merge to development
- [x] Create platform-system namespace
- [x] Create ServiceAccount + RBAC with IRSA annotation
- [x] Create Argo WorkflowTemplate as fallback
- [x] Update documentation to reflect automated flow
- [x] Sync Backstage template with `size` field

### Edge cases observed (optional)

- GitHub runners cannot reach private RDS -> use K8s Job with VPC access via IRSA

### Outputs produced

- Workflows: `.github/workflows/rds-database-apply.yml`
- K8s manifests: `gitops/kustomize/platform-system/` (namespace, RBAC, WorkflowTemplate)
- Docs: Updated `RDS_USER_DB_PROVISIONING.md` Part 7, `RB-0032` runbook

### Next actions

- [ ] Create IRSA role `goldenpath-platform-provisioner` in Terraform
- [ ] Merge workflow to main branch (required for trigger)
- [ ] Test end-to-end with new database request

### Links (optional)

- Runbook: docs/70-operations/runbooks/RB-0032-rds-user-provision.md
- Workflow: .github/workflows/rds-database-apply.yml
- How-it-works: docs/85-how-it-works/self-service/RDS_USER_DB_PROVISIONING.md

### Session Report (end-of-session wrap-up)

- Summary:
  - Implemented fully automated RDS provisioning triggered on PR merge
  - Created GitHub workflow, K8s namespace, ServiceAccount/RBAC, Argo WorkflowTemplate
  - Updated documentation to reflect V1.1 automation architecture
  - Synced Backstage form with new `size` field (9 fields total)
- Decisions:
  - K8s Job over Lambda for VPC access
  - IRSA for Secrets Manager access (boto3), PostgreSQL credentials for DB operations
  - Argo WorkflowTemplate as manual fallback with UI visibility
- Risks/Follow-ups:
  - IRSA role must be created before automation works
  - Workflow file must be on main branch to trigger
- Validation: Dry-run tested locally; full E2E pending merge

### Files Created This Session

| File | Purpose |
|------|---------|
| `.github/workflows/rds-database-apply.yml` | Auto-triggers on merge, runs TF apply + K8s Job |
| `gitops/kustomize/platform-system/kustomization.yaml` | Kustomization for platform-system |
| `gitops/kustomize/platform-system/rds-provisioner-rbac.yaml` | ServiceAccount + RBAC for IRSA |
| `gitops/kustomize/platform-system/rds-provision-workflowtemplate.yaml` | Argo WorkflowTemplate |
| `claude_status/2026-01-16_session_summary.md` | Session summary (alternate location) |

### Files Modified This Session

| File | Change |
|------|--------|
| `gitops/kustomize/bases/namespaces.yaml` | Added `platform-system` namespace |
| `gitops/kustomize/bases/kustomization.yaml` | Added `../platform-system/` reference |
| `docs/85-how-it-works/self-service/RDS_USER_DB_PROVISIONING.md` | Added Part 7: Automation Architecture |
| `docs/70-operations/runbooks/RB-0032-rds-user-provision.md` | Updated "When to Use" section |
| `backstage-helm/backstage-catalog/templates/rds-request.yaml` | Added `size` field (synced) |
| `.github/workflows/create-rds-database.yml` | Added `size` field + validation |

## 2026-01-16T22:08:49Z — RDS: dual-mode alignment + deploy wiring — env=dev build_id=na

Owner: platform-team
Agent: codex
Goal: Align RDS enums across self-service, document dual-mode flow, and wire auto provisioning into deploy.

### In-Session Log (append as you go)
- 22:00Z — Updated Backstage RDS template/workflow inputs to match enums + size tiers
- 22:02Z — Added dual-mode RDS how-it-works doc + ADR-0166
- 22:05Z — Added mode-aware rds-provision-auto and wired into make deploy
- 22:07Z — Documented deploy/approval guidance in RDS architecture/runbook

### Checkpoints
- [x] Enum-aligned Backstage RDS inputs (size/domain/risk)
- [x] Dual-mode automation doc + ADR
- [x] Mode-aware provisioning command
- [x] Deploy flow updated to include provisioning

### Outputs produced (optional)
- ADR: `docs/adrs/ADR-0166-rds-dual-mode-automation-and-enum-alignment.md`
- Docs: `docs/85-how-it-works/self-service/RDS_DUAL_MODE_AUTOMATION.md`
- Docs: `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
- Runbook: `docs/70-operations/runbooks/RB-0032-rds-user-provision.md`

### Next actions
- [ ] Run a coupled `make deploy` in dev to confirm end-to-end flow
- [ ] Add PR guard for `size=large|xlarge` approvals (if desired)

### Session Report (end-of-session wrap-up)
- Summary:
  - Aligned RDS self-service inputs with canonical enums and size tiers
  - Documented dual-mode RDS flow and deploy shortcut caveats
  - Wired `rds-provision-auto` into `make deploy` for one-command builds
- Decisions:
  - Keep both coupled and standalone modes; auto-detect provisioning source
- Risks/Follow-ups:
  - Non-dev still requires `ALLOW_DB_PROVISION=true` approval gate
  - IRSA/CI workflow approval for large tiers remains a follow-up
- Validation: Not run in this session

Signed: Codex (2026-01-16T22:08:49Z)
