# Session Report: Backstage & Keycloak Stabilization

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
   - **Verified Architecture**: `amd64` ✓
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

| Component | Status | Pod | Details |
|-----------|--------|-----|---------|
| **Keycloak** | ✅ Running | `dev-keycloak-0` 1/1 | AMD64 Bitnami from ECR, connected to RDS |
| **Backstage** | ✅ Running | `dev-backstage-*` 1/1 | Local chart, ECR image, SSL RDS connection |
| **Catalog** | ✅ Loaded | N/A | Serving from governance-registry branch |
| **GitHub Token** | ✅ Configured | N/A | PR features and scaffolder working |
| **ExternalSecrets** | ✅ Synced | N/A | `backstage-secrets` syncing from AWS Secrets Manager |

### Commits Made This Session

| Commit | Message |
|--------|---------|
| `d4174ef7` | fix: use ArgoCD multi-source pattern for Backstage values |
| `0e0bd2fa` | fix: add SSL config for Backstage RDS connection |
| `5d13229e` | docs: update session summary with final platform status |
| `59f792f0` | feat(catalog): sync backstage-catalog to governance-registry |
| `06f26853` | fix: correct backstage catalog URL path to governance-registry |
| `58e35b96` | docs: add GitHub token setup phase to IDP deployment runbook |
| `92112513` | docs: update catalog references and add changelogs |

### AWS Resources

| Resource | ARN/ID | Purpose |
|----------|--------|---------|
| ECR: `backstage` | `593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage` | Backstage container image |
| ECR: `keycloak` | `593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak` | Keycloak container image |
| RDS | `goldenpath-dev-goldenpath-platform-db.cxmcacaams2q.eu-west-2.rds.amazonaws.com` | PostgreSQL 15.15 |
| Secret | `goldenpath/dev/rds/master` | RDS master credentials |
| Secret | `goldenpath/dev/backstage/postgres` | Backstage DB credentials |
| Secret | `goldenpath/dev/backstage/secrets` | Backstage GitHub token |
| Secret | `goldenpath/dev/keycloak/postgres` | Keycloak DB credentials |

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

| Changelog | Description                                |
| --------- | ------------------------------------------ |
| CL-0132   | ClusterSecretStore Addon Deployment Fix    |
| CL-0133   | IDP Stack Deployment Runbook (RB-0031)     |
| CL-0134   | Backstage Catalog Governance Registry Sync |

### Session Summary

- **Session Summary**: `claude_status/2026-01-15_session_summary.md` (this file)

## 6. Lessons Learned

1. **ARM64 vs AMD64**: Always use `--platform linux/amd64` when pulling images on Apple Silicon for deployment to x86 clusters.

2. **Bitnami Charts**: Require Bitnami-specific images (not official upstream images) due to init scripts.

3. **ArgoCD Multi-Source**: For values files outside chart directory, use `sources` with `ref: values` and `$values/` prefix pattern.

4. **RDS User Provisioning**: Terraform creates secrets but not PostgreSQL users - manual intervention or automation required.

5. **RDS SSL**: AWS RDS requires SSL by default. Configure `ssl.require: true` in application database connections.

6. **Backstage CREATEDB**: Backstage dynamically creates plugin databases, requiring `CREATEDB` privilege on its database user.

7. **Catalog Branch Strategy**: Use `governance-registry` branch for stable catalog that doesn't change with feature development.

8. **GitHub Token for PR Features**: Backstage scaffolder requires valid GitHub PAT with `repo`, `workflow`, `read:org` scopes.

## 7. Access Commands

```bash
# Port-forward Backstage
kubectl port-forward svc/dev-backstage -n backstage 7007:7007

# Port-forward Keycloak
kubectl port-forward svc/dev-keycloak -n keycloak 8080:8080

# Check pod status
kubectl get pods -n backstage
kubectl get pods -n keycloak

# Check ExternalSecret status
kubectl get externalsecret -n backstage
kubectl get externalsecret -n keycloak
```
