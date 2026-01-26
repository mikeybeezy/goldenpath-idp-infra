---
id: RB-0031-idp-stack-deployment
title: IDP Stack Deployment (Keycloak + Backstage)
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: argocd-sync
  observability_tier: silver
  maturity: 2
schema_version: 1
relates_to:
  - 30_PLATFORM_RDS_ARCHITECTURE
  - ADR-0160
  - CL-0133-idp-stack-deployment-runbook
  - DOCS_RUNBOOKS_README
  - EC-0004-backstage-copilot-plugin
  - RB-0001-eks-access-recovery
  - RB-0012-argocd-app-readiness
  - RB-0032
  - RB-0033-persistent-cluster-teardown
  - RB-0034-persistent-cluster-deployment
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_USER_DB_PROVISIONING
  - SESSION_CAPTURE_2026_01_17_01
  - agent_session_summary
  - session_summary_template
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
supported_until: 2028-01-15
version: '1.0'
breaking_change: false
---

## IDP Stack Deployment Runbook (Keycloak + Backstage)

This runbook provides the complete sequence to deploy and verify the IDP core stack (Keycloak and Backstage) on a new or existing EKS cluster.

## When to Use

- After a new cluster is provisioned via Terraform
- After cluster rebuild/recovery
- When Keycloak or Backstage pods are failing to start
- When troubleshooting RDS connectivity issues

## Important Note: Pre-baked vs Custom Images

> **Current State**: This runbook uses **pre-baked community images** for both Keycloak and Backstage:
>
> |Application|Image Source|Notes|
> |---|---|---|
> |Keycloak|`public.ecr.aws/bitnami/keycloak:latest`|Bitnami-maintained, required for Helm chart compatibility|
> |Backstage|`ghcr.io/guymenahem/backstage-platformers:0.0.1`|Platformers community pre-built image|
>
> **When building custom images**, the following will change:
>
> - **Backstage Dockerfile**: You'll need to maintain your own Dockerfile with custom plugins
> - **Build pipeline**: CI/CD will build and push images to ECR on each release
> - **Image tags**: Use semantic versioning instead of fixed tags
> - **appConfig**: May need additional configuration for custom plugins
>
> See [Phase 1, Step 1.6 Option B](#step-16-pull-and-push-backstage-image-if-missing) for custom build instructions.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         EKS Cluster                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Keycloak   │  │  Backstage   │  │  External Secrets        │  │
│  │   (StatefulSet)│  │  (Deployment)│  │  Operator                │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬──────────────┘  │
│         │                 │                       │                  │
│         │                 │                       ▼                  │
│         │                 │          ┌──────────────────────────┐   │
│         │                 │          │  ClusterSecretStore      │   │
│         │                 │          │  (aws-secretsmanager)    │   │
│         │                 │          └───────────┬──────────────┘   │
└─────────┼─────────────────┼───────────────────────┼──────────────────┘
          │                 │                       │
          ▼                 ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS Services                                 │
│  ┌──────────────────────┐        ┌──────────────────────────────┐  │
│  │     RDS PostgreSQL   │        │   AWS Secrets Manager        │  │
│  │  (goldenpath-*-db)   │        │   goldenpath/dev/*/postgres  │  │
│  │                      │        │   goldenpath/dev/*/secrets   │  │
│  │  Databases:          │        │                              │  │
│  │  - keycloak          │◄───────┤   Secrets:                   │  │
│  │  - backstage_*       │        │   - rds/master               │  │
│  └──────────────────────┘        │   - keycloak/postgres        │  │
│                                  │   - backstage/postgres       │  │
│  ┌──────────────────────┐        │   - backstage/secrets        │  │
│  │        ECR           │        └──────────────────────────────┘  │
│  │  - keycloak:latest   │                                          │
│  │  - backstage:0.0.1   │                                          │
│  └──────────────────────┘                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. AWS Infrastructure (Terraform)

Verify the following resources exist:

```bash
# Check RDS instance
aws rds describe-db-instances \
  --db-instance-identifier goldenpath-${ENV}-goldenpath-platform-db \
  --region eu-west-2 \
  --query 'DBInstances[0].DBInstanceStatus'

# Check Secrets Manager secrets exist
aws secretsmanager list-secrets \
  --region eu-west-2 \
  --query "SecretList[?contains(Name, 'goldenpath/${ENV}')].Name"

# Check ECR repositories
aws ecr describe-repositories \
  --region eu-west-2 \
  --query 'repositories[*].repositoryName'
```

### Expected secrets

- `goldenpath/${ENV}/rds/master` - RDS master credentials
- `goldenpath/${ENV}/keycloak/postgres` - Keycloak DB credentials
- `goldenpath/${ENV}/backstage/postgres` - Backstage DB credentials
- `goldenpath/${ENV}/backstage/secrets` - Backstage GitHub token

### 2. EKS Cluster Access

```bash
# Update kubeconfig
aws eks update-kubeconfig --name goldenpath-${ENV}-eks --region eu-west-2

# Verify access
kubectl get nodes
```

### 3. ArgoCD Running

```bash
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-server
```

### 4. External Secrets Operator Running

```bash
kubectl get pods -n external-secrets
kubectl get clustersecretstore aws-secretsmanager
```

### 5. CoreDNS Running (Cluster DNS)

CoreDNS provides internal DNS resolution for service discovery within the cluster. Without it, pods cannot resolve service names like `keycloak.keycloak.svc.cluster.local`.

```bash
# Check CoreDNS pods are running (should show 2/2 Running)
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS service exists
kubectl get svc -n kube-system kube-dns
```

### Expected output

- CoreDNS pods: 2 replicas running
- Service: ClusterIP on port 53 (UDP/TCP)

### Verification tests

```bash
# Test 1: Internal Kubernetes API resolution
kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup kubernetes.default.svc.cluster.local
# Expected: Address pointing to Kubernetes API ClusterIP

# Test 2: Cross-namespace service discovery (after services deployed)
kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup keycloak.keycloak.svc.cluster.local
# Expected: Address of Keycloak service

# Test 3: External DNS forwarding
kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup github.com
# Expected: External IP for github.com
```

**Note:** CoreDNS is an EKS-managed addon installed automatically during cluster creation. If CoreDNS is missing or unhealthy, check the EKS addon status:

```bash
aws eks describe-addon \
  --cluster-name goldenpath-${ENV}-eks \
  --addon-name coredns \
  --region eu-west-2 \
  --query 'addon.status'
```

---

## Phase 1: ECR Repository and Image Preparation

### Why This Matters (RDS User Provisioning)

- **ECR is required**: All IDP images must be stored in private ECR to avoid Docker Hub rate limits and ensure availability
- **Architecture matters**: EKS nodes are AMD64 (x86_64). Images pulled on Apple Silicon (ARM64) Macs will fail with `exec format error`
- **Bitnami compatibility**: Keycloak must use Bitnami images (not official Keycloak images) due to Helm chart init script requirements

### Step 1.1: Check Existing ECR Repositories

```bash
# List all ECR repositories
aws ecr describe-repositories \
  --region eu-west-2 \
  --query 'repositories[*].[repositoryName,repositoryUri]' \
  --output table
```

### Required repositories

|Repository|Purpose|Source Image|
|------------|---------|--------------|
|`keycloak`|Identity provider|`public.ecr.aws/bitnami/keycloak:latest`|
|`backstage`|Developer portal|`ghcr.io/guymenahem/backstage-platformers:0.0.1`|

### Step 1.2: Create ECR Repositories (if missing)

```bash
# Check if keycloak repo exists
aws ecr describe-repositories --repository-names keycloak --region eu-west-2 2>/dev/null || \
  aws ecr create-repository \
    --repository-name keycloak \
    --region eu-west-2 \
    --image-scanning-configuration scanOnPush=true \
    --tags Key=Environment,Value=${ENV} Key=Application,Value=keycloak

# Check if backstage repo exists
aws ecr describe-repositories --repository-names backstage --region eu-west-2 2>/dev/null || \
  aws ecr create-repository \
    --repository-name backstage \
    --region eu-west-2 \
    --image-scanning-configuration scanOnPush=true \
    --tags Key=Environment,Value=${ENV} Key=Application,Value=backstage
```

### Step 1.3: Authenticate to ECR

```bash
# Get ECR login token and authenticate Docker
aws ecr get-login-password --region eu-west-2 | \
  docker login --username AWS --password-stdin 593517239005.dkr.ecr.eu-west-2.amazonaws.com

# Verify authentication
docker pull 593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest 2>/dev/null && \
  echo "ECR auth successful" || echo "ECR auth failed or image missing"
```

### Step 1.4: Check if Images Exist in ECR

```bash
# Check Keycloak image
aws ecr describe-images \
  --repository-name keycloak \
  --region eu-west-2 \
  --query 'imageDetails[*].[imageTags,imagePushedAt]' \
  --output table 2>/dev/null || echo "No keycloak images found"

# Check Backstage image
aws ecr describe-images \
  --repository-name backstage \
  --region eu-west-2 \
  --query 'imageDetails[*].[imageTags,imagePushedAt]' \
  --output table 2>/dev/null || echo "No backstage images found"
```

### Step 1.5: Build/Pull and Push Keycloak Image (if missing)

**CRITICAL**: Use `--platform linux/amd64` to force AMD64 architecture.

```bash
# Pull Bitnami Keycloak (required for Bitnami Helm chart compatibility)
docker pull --platform linux/amd64 public.ecr.aws/bitnami/keycloak:latest

# Tag for private ECR
docker tag public.ecr.aws/bitnami/keycloak:latest \
  593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest

# Push to ECR
docker push 593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest
```

**WARNING**: Do NOT use `quay.io/keycloak/keycloak` - it lacks Bitnami init scripts.

### Step 1.6: Pull and Push Backstage Image (if missing)

### Option A: Use pre-built Platformers image

```bash
# Pull Backstage image (pre-built by Platformers community)
docker pull --platform linux/amd64 ghcr.io/guymenahem/backstage-platformers:0.0.1

# Tag for private ECR
docker tag ghcr.io/guymenahem/backstage-platformers:0.0.1 \
  593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage:0.0.1

# Push to ECR
docker push 593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage:0.0.1
```

### Option B: Build custom Backstage image from source

If you need to build a custom Backstage image with additional plugins:

```bash
# Clone backstage repo (contains Dockerfile)
cd /tmp
git clone https://github.com/mikeybeezy/goldenpath-idp-backstage.git
cd goldenpath-idp-backstage

# Build for AMD64 (even on Apple Silicon)
docker buildx build \
  --platform linux/amd64 \
  -t 593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage:custom \
  --push \
  .

# Or use standard docker build + push
docker build --platform linux/amd64 -t backstage:custom .
docker tag backstage:custom 593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage:custom
docker push 593517239005.dkr.ecr.eu-west-2.amazonaws.com/backstage:custom
```

**Note**: Update `gitops/helm/backstage/values/${ENV}.yaml` with the new tag if using a custom build.

### Step 1.7: Verify Image Architecture

```bash
docker inspect 593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest \
  --format '{{.Architecture}}'
# Expected: amd64
```

---

## Phase 2: RDS User Provisioning

### Automation Note

On merge to `development`, the `rds-database-apply.yml` workflow can run the
Terraform apply and provisioning job automatically. Use the manual steps below
for recovery, break-glass, or when automation is disabled.

### Toggles and Options

- `ALLOW_DB_PROVISION=true`: Required for non-dev environments (staging/prod).
- `RDS_MODE=coupled|standalone`: Force provisioning mode if auto-detection is ambiguous.
- `BUILD_ID` / `RUN_ID`: Include for traceability in audit logs.

### Why This Matters (GitHub Token)

Terraform creates AWS Secrets Manager secrets with credentials, but does NOT create the actual PostgreSQL users. This is a known gap that requires manual intervention.

### Step 2.1: Retrieve RDS Master Credentials

```bash
# Get master username and password
export RDS_HOST=$(aws rds describe-db-instances \
  --db-instance-identifier goldenpath-${ENV}-goldenpath-platform-db \
  --region eu-west-2 \
  --query 'DBInstances[0].Endpoint.Address' --output text)

export RDS_MASTER_USER=$(aws secretsmanager get-secret-value \
  --secret-id goldenpath/${ENV}/rds/master \
  --region eu-west-2 \
  --query 'SecretString' --output text | jq -r '.username')

export RDS_MASTER_PASS=$(aws secretsmanager get-secret-value \
  --secret-id goldenpath/${ENV}/rds/master \
  --region eu-west-2 \
  --query 'SecretString' --output text | jq -r '.password')

echo "RDS Host: $RDS_HOST"
echo "Master User: $RDS_MASTER_USER"
```

### Step 2.2: Get Application User Passwords

```bash
# Keycloak password
export KEYCLOAK_DB_PASS=$(aws secretsmanager get-secret-value \
  --secret-id goldenpath/${ENV}/keycloak/postgres \
  --region eu-west-2 \
  --query 'SecretString' --output text | jq -r '.password')

# Backstage password
export BACKSTAGE_DB_PASS=$(aws secretsmanager get-secret-value \
  --secret-id goldenpath/${ENV}/backstage/postgres \
  --region eu-west-2 \
  --query 'SecretString' --output text | jq -r '.password')
```

### Step 2.3: Create PostgreSQL Users via psql Pod

```bash
# Create a temporary psql pod
kubectl run psql-provisioner -n default --rm -i --restart=Never \
  --image=postgres:15-alpine -- psql \
  "host=$RDS_HOST port=5432 user=$RDS_MASTER_USER password=$RDS_MASTER_PASS dbname=postgres sslmode=require" \
  -c "
-- Keycloak user and database
CREATE USER keycloak_app WITH PASSWORD '$KEYCLOAK_DB_PASS';
CREATE DATABASE keycloak OWNER keycloak_app;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak_app;

-- Backstage user and database
CREATE USER backstage_app WITH PASSWORD '$BACKSTAGE_DB_PASS';
CREATE DATABASE backstage_plugin_catalog OWNER backstage_app;
GRANT ALL PRIVILEGES ON DATABASE backstage_plugin_catalog TO backstage_app;

-- Backstage needs CREATEDB privilege (creates plugin databases dynamically)
ALTER USER backstage_app CREATEDB;
"
```

### Step 2.4: Verify User Creation

```bash
kubectl run psql-verify -n default --rm -i --restart=Never \
  --image=postgres:15-alpine -- psql \
  "host=$RDS_HOST port=5432 user=$RDS_MASTER_USER password=$RDS_MASTER_PASS dbname=postgres sslmode=require" \
  -c "\du"
```

Expected output should show `keycloak_app` and `backstage_app` users.

---

## Phase 3: External Secrets Verification

### Step 3.1: Verify ClusterSecretStore

```bash
kubectl get clustersecretstore aws-secretsmanager -o yaml
```

Ensure `status.conditions` shows `Ready: True`.

### Step 3.2: Check ExternalSecret Status

```bash
# Keycloak
kubectl get externalsecret -n keycloak

# Backstage
kubectl get externalsecret -n backstage
```

All should show `SecretSynced` status.

### Step 3.3: Verify Secret Contents

```bash
# Verify keycloak secrets have correct keys
kubectl get secret -n keycloak -o name

# Verify backstage secrets
kubectl get secret backstage-secrets -n backstage -o jsonpath='{.data}' | jq 'keys'
```

---

## Phase 3.5: GitHub Token Configuration (Bootstrap Prerequisite)

### Why This Matters

Backstage requires a GitHub Personal Access Token (PAT) for:

- **Catalog Integration**: Reading catalog files from private repositories
- **Scaffolder Templates**: Creating repositories and pull requests
- **GitHub Actions**: Triggering workflow dispatches
- **Software Templates**: Publishing repos and PRs via Backstage templates

Without a valid token, Backstage will start but PR-based features and private catalog access will fail.

### Step 3.5.1: Create GitHub Personal Access Token

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta) (recommended) or [Classic tokens](https://github.com/settings/tokens)

2. Create a new token with these scopes:

### For Classic Tokens

|Scope|Purpose|
|-----------|-------------------------------------------------------------|
|`repo`|Full control of private repositories (scaffolder PR creation)|
|`workflow`|Update GitHub Action workflows|
|`read:org`|Read organization membership|
|`read:user`|Read user profile data|

### For Fine-grained Tokens

|Permission|Access Level|
|---------------------------------------|--------------|
|Repository permissions → Contents|Read and write|
|Repository permissions → Pull requests|Read and write|
|Repository permissions → Workflows|Read and write|
|Organization permissions → Members|Read-only|

### Step 3.5.2: Store Token in AWS Secrets Manager

```bash
# Set your environment
export ENV=dev

# Option 1: Interactive (more secure - token not in shell history)
read -sp "Enter GitHub PAT: " GITHUB_PAT && echo

# Update the secret (preserves existing keys)
CURRENT_SECRET=$(aws secretsmanager get-secret-value \
  --secret-id goldenpath/${ENV}/backstage/secrets \
  --region eu-west-2 \
  --query 'SecretString' --output text)

# Merge with new token
NEW_SECRET=$(echo "$CURRENT_SECRET" | jq --arg token "$GITHUB_PAT" '.token = $token')

aws secretsmanager put-secret-value \
  --secret-id goldenpath/${ENV}/backstage/secrets \
  --region eu-west-2 \
  --secret-string "$NEW_SECRET"

# Clear sensitive variables
unset GITHUB_PAT CURRENT_SECRET NEW_SECRET
```

```bash
# Option 2: Direct update (simpler but token visible in history)
aws secretsmanager put-secret-value \
  --secret-id goldenpath/${ENV}/backstage/secrets \
  --region eu-west-2 \
  --secret-string '{"token":"ghp_YOUR_TOKEN_HERE","client-secret":"placeholder"}'
```

### Step 3.5.3: Verify Secret Update

```bash
# Check token was stored (shows first 10 chars only)
aws secretsmanager get-secret-value \
  --secret-id goldenpath/${ENV}/backstage/secrets \
  --region eu-west-2 \
  --query 'SecretString' --output text | jq -r '.token' | head -c 10
echo "...(truncated)"
```

### Step 3.5.4: Trigger ExternalSecret Sync

```bash
# Force ExternalSecret to resync from AWS
kubectl annotate externalsecret backstage-secrets -n backstage \
  force-sync=$(date +%s) --overwrite

# Verify sync status
kubectl get externalsecret backstage-secrets -n backstage \
  -o jsonpath='{.status.conditions[0].type}{" "}{.status.conditions[0].status}'
# Expected: Ready True
```

### Step 3.5.5: Verify Token in Kubernetes Secret

```bash
# Confirm token synced to K8s (shows first 10 chars)
kubectl get secret backstage-secrets -n backstage \
  -o jsonpath='{.data.GITHUB_TOKEN}' | base64 -d | head -c 10
echo "...(truncated)"
```

### Step 3.5.6: Restart Backstage to Load New Token

```bash
kubectl rollout restart deployment/dev-backstage -n backstage
kubectl rollout status deployment/dev-backstage -n backstage
```

---

## Phase 4: Deploy Keycloak

### Step 4.1: Verify ArgoCD Application

```bash
kubectl get application dev-keycloak -n argocd -o jsonpath='{.status.sync.status}'
```

### Step 4.2: Force Sync if Needed

```bash
kubectl patch application dev-keycloak -n argocd \
  --type merge -p '{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'
```

### Step 4.3: Watch Pod Status

```bash
kubectl get pods -n keycloak -w
```

### Step 4.4: Check Logs for Errors

```bash
# Check init container logs
kubectl logs -n keycloak dev-keycloak-0 -c prepare

# Check main container logs
kubectl logs -n keycloak dev-keycloak-0 --tail=100
```

### Common Keycloak Issues

|Symptom|Cause|Fix|
|---------|-------|-----|
|`exec format error`|ARM64 image on AMD64 nodes|Re-push with `--platform linux/amd64`|
|`Init:Error`|Missing Bitnami scripts|Use `public.ecr.aws/bitnami/keycloak`|
|`password authentication failed`|PostgreSQL user doesn't exist|Run Phase 2 user provisioning|
|`ImagePullBackOff`|ECR auth or image missing|Check ECR login and image exists|

---

## Phase 5: Deploy Backstage

### Step 5.1: Verify ArgoCD Application

```bash
kubectl get application dev-backstage -n argocd -o jsonpath='{.status.sync.status}'
```

### Step 5.2: Force Sync if Needed

```bash
kubectl patch application dev-backstage -n argocd \
  --type merge -p '{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'
```

### Step 5.3: Watch Pod Status

```bash
kubectl get pods -n backstage -w
```

### Step 5.4: Check Logs for Errors

```bash
kubectl logs -n backstage -l app.kubernetes.io/name=backstage --tail=100
```

### Common Backstage Issues

|Symptom|Cause|Fix|
|---------|-------|-----|
|`no pg_hba.conf entry ... no encryption`|SSL not configured|Add `ssl.require: true` to appConfig|
|`permission denied to create database`|Missing CREATEDB privilege|Run `ALTER USER backstage_app CREATEDB`|
|`Kubernetes configuration is missing`|Missing k8s config in appConfig|Add kubernetes block to values|
|`Failed to connect to database`|Wrong host/port/credentials|Verify ExternalSecret syncing|

---

## Phase 6: Verification Checklist

### 6.1: Pod Health

```bash
echo "=== Keycloak ==="
kubectl get pods -n keycloak
kubectl get pods -n keycloak -o jsonpath='{.items[0].status.containerStatuses[0].ready}'

echo "=== Backstage ==="
kubectl get pods -n backstage
kubectl get pods -n backstage -o jsonpath='{.items[0].status.containerStatuses[0].ready}'
```

### 6.2: Service Endpoints

```bash
# Keycloak
kubectl get svc -n keycloak

# Backstage
kubectl get svc -n backstage
```

### 6.3: Logs Health Check

```bash
# Keycloak - look for "Listening on"
kubectl logs -n keycloak dev-keycloak-0 --tail=20 | grep -i "listening"

# Backstage - look for "Listening on :7007"
kubectl logs -n backstage -l app.kubernetes.io/name=backstage --tail=20 | grep -i "listening"
```

### 6.4: Database Connectivity

```bash
# Verify Keycloak can query its database
kubectl exec -n keycloak dev-keycloak-0 -- \
  /opt/bitnami/keycloak/bin/kc.sh show-config 2>/dev/null | grep -i database

# Backstage logs should show successful migration
kubectl logs -n backstage -l app.kubernetes.io/name=backstage | grep -i "migration"
```

---

## Troubleshooting Decision Tree

```text
Pod not starting?
├── ImagePullBackOff
│   ├── Check ECR authentication
│   ├── Verify image exists: aws ecr describe-images --repository-name <name>
│   └── Check image architecture matches cluster (amd64)
│
├── Init:Error / CrashLoopBackOff
│   ├── Check init container logs: kubectl logs <pod> -c <init-container>
│   ├── For Keycloak: Verify using Bitnami image (not official)
│   └── Check ExternalSecrets synced
│
├── Running but 0/1 Ready
│   ├── Check liveness/readiness probes
│   ├── Check container logs for startup errors
│   └── Verify database connectivity
│
└── Database connection errors
    ├── "password authentication failed"
    │   └── Run Phase 2: Create PostgreSQL users
    ├── "no pg_hba.conf entry ... no encryption"
    │   └── Add SSL config to database connection
    ├── "permission denied to create database"
    │   └── Grant CREATEDB: ALTER USER <user> CREATEDB;
    └── Connection timeout
        └── Check security groups allow RDS access from EKS
```

---

## Quick Reference Commands

```bash
# Full stack status
kubectl get pods -n keycloak && kubectl get pods -n backstage

# ArgoCD app status
kubectl get applications -n argocd -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status

# Restart deployments after config changes
kubectl rollout restart deployment -n backstage
kubectl rollout restart statefulset -n keycloak

# Force ArgoCD hard refresh
kubectl patch application <app-name> -n argocd --type merge -p '{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'

# Delete and recreate ArgoCD app (clears cache)
kubectl delete application <app-name> -n argocd && kubectl apply -f gitops/argocd/apps/${ENV}/<app-name>.yaml
```

---

## Related Documentation

- [RB-0001-eks-access-recovery](RB-0001-eks-access-recovery.md) - EKS cluster access
- [RB-0012-argocd-app-readiness](RB-0012-argocd-app-readiness.md) - ArgoCD verification
- [ADR-0160](../../adrs/ADR-0160-rds-optional-toggle-integration.md) - RDS toggle design
- [Session Summary](../../../claude_status/2026-01-15_session_summary.md) - Original debugging session

---

## Appendix A: Helm Values Reference

### Keycloak (`gitops/helm/keycloak/values/dev.yaml`)

```yaml
image:
  registry: 593517239005.dkr.ecr.eu-west-2.amazonaws.com
  repository: keycloak
  tag: latest
  pullPolicy: Always

global:
  security:
    allowInsecureImages: true  # Required for private ECR
```

### Backstage (`gitops/helm/backstage/values/dev.yaml`)

```yaml
image:
  repository: 593517239005.dkr.ecr.eu-west-2.amazonaws.com/
  name: backstage
  tag: 0.0.1
  pullPolicy: Always

externalSecret:
  enabled: true
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore

postgres:
  host: goldenpath-dev-goldenpath-platform-db.cxmcacaams2q.eu-west-2.rds.amazonaws.com
  port: "5432"
  user: backstage_app

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

---

## Appendix B: ArgoCD Multi-Source Pattern

When values files are outside the chart directory, use multi-source:

```yaml
spec:
  sources:
    # Source 1: Reference for values files
    - repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
      targetRevision: feature/tooling-apps-config
      ref: values
    # Source 2: Helm chart with $values reference
    - repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
      path: gitops/helm/backstage/chart
      targetRevision: feature/tooling-apps-config
      helm:
        valueFiles:
          - $values/gitops/helm/backstage/values/dev.yaml
```
