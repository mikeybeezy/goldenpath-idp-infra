---
id: RB-0037
title: Pipeline Enablement for ArgoCD Image Updater
type: runbook
relates_to:
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - ADR-0170-build-pipeline-architecture
  - GOV-0012-build-pipeline-standards
  - RB-0036-github-app-image-updater
tags:
  - pipeline
  - image-updater
  - gitops
  - post-bootstrap
category: runbooks
---

# RB-0037: Pipeline Enablement for ArgoCD Image Updater

## Purpose

Enable CI/CD pipeline write-back capabilities on a GoldenPath IDP cluster after
bootstrap. This runbook is executed as a **separate event** from cluster creation,
per ADR-0174.

## When to Use This Runbook

Execute this runbook when:
- A new cluster has been bootstrapped and you want to enable automated image updates
- Adding pipeline capabilities to an existing cluster
- Restoring pipeline functionality after secret rotation

## Prerequisites

- [ ] Cluster bootstrap completed successfully
- [ ] ArgoCD Image Updater deployed (via Helm)
- [ ] AWS Secrets Manager access
- [ ] kubectl access to target cluster
- [ ] GitHub App exists (see RB-0036 for creation)

## Architecture Context

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  GitHub Actions │───>│   ECR Registry   │<───│ Image Updater   │
│  (Build & Push) │    │                  │    │ (Poll for tags) │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  App Repo Git   │<───│   GitHub App     │<───│ Write-back      │
│  (values.yaml)  │    │ (Authentication) │    │ (Tag update)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Environment Matrix

| Environment | Secret Requirement | Behavior |
|-------------|-------------------|----------|
| local | Not required | Uses digest strategy, no write-back |
| dev | Optional | Graceful degradation if missing |
| test | Required | Deployment fails without secret |
| staging | Required | Deployment fails without secret |
| prod | Required | Deployment fails without secret |

## Local Infra-Like Toggle (Optional)

By default, **local stays fast**: digest updates only, no git write-back.
If you want a more infra-like experience locally, you can enable write-back
explicitly using a sandbox repo or branch.

### Option A: Minimal (fast default)

- Keep `gitops/helm/argocd-image-updater/values/local.yaml` as-is.
- No git credentials required.
- Best for quick iteration.

### Option B: Infra-Like (opt-in)

**Goal:** simulate AWS dev behavior (git write-back) on kind/local.

Steps:

1. Create a GitHub token (or GitHub App) scoped to a **sandbox repo/branch**.
2. Create a Kubernetes secret in `argocd` with the credentials.
3. Update the local ArgoCD Application to use git write-back and credentials.

Example (token-based for local only):

```bash
kubectl create secret generic github-app-image-updater \
  --namespace argocd \
  --from-literal=username="git" \
  --from-literal=password="$GITHUB_TOKEN"
```

Then update `gitops/argocd/apps/local/hello-goldenpath-idp.yaml`:

```yaml
metadata:
  annotations:
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
    argocd-image-updater.argoproj.io/git-credentials: secret:argocd/github-app-image-updater
```

**Note:** Prefer using a sandbox repo/branch to avoid noisy commits in primary repos.

## Step-by-Step Instructions

### Step 1: Verify GitHub App Exists

Confirm the GitHub App is created and installed per RB-0036:

```bash
# Check if Secrets Manager entry exists
aws secretsmanager describe-secret \
  --secret-id "goldenpath/${ENV}/github-app/image-updater" \
  --region eu-west-2

# Expected: Secret exists with appID, installationID, privateKey
```

If the secret doesn't exist, complete RB-0036 first.

### Step 2: Create Kubernetes Secret

**Option A: Manual Creation (Recommended for initial setup)**

```bash
# Set environment
ENV=dev  # or test, staging, prod

# Fetch credentials from Secrets Manager
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "goldenpath/${ENV}/github-app/image-updater" \
  --query SecretString --output text \
  --region eu-west-2)

# Extract values
APP_ID=$(echo "$SECRET_JSON" | jq -r '.appID')
INSTALLATION_ID=$(echo "$SECRET_JSON" | jq -r '.installationID')
PRIVATE_KEY=$(echo "$SECRET_JSON" | jq -r '.privateKey')

# Create Kubernetes secret
kubectl create secret generic github-app-image-updater \
  --namespace argocd \
  --from-literal=app-id="$APP_ID" \
  --from-literal=installation-id="$INSTALLATION_ID" \
  --from-literal=private-key="$PRIVATE_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secret created
kubectl get secret github-app-image-updater -n argocd
```

**Option B: ExternalSecret (Recommended for automated sync)**

Apply the ExternalSecret CRD to auto-sync from Secrets Manager:

```yaml
# gitops/base/argocd/external-secret-github-app.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: github-app-image-updater
  namespace: argocd
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: github-app-image-updater
    creationPolicy: Owner
  data:
    - secretKey: app-id
      remoteRef:
        key: goldenpath/{{ .Environment }}/github-app/image-updater
        property: appID
    - secretKey: installation-id
      remoteRef:
        key: goldenpath/{{ .Environment }}/github-app/image-updater
        property: installationID
    - secretKey: private-key
      remoteRef:
        key: goldenpath/{{ .Environment }}/github-app/image-updater
        property: privateKey
```

### Step 3: Restart Image Updater

After secret creation, restart Image Updater to pick up credentials:

```bash
kubectl rollout restart deployment argocd-image-updater -n argocd

# Wait for rollout
kubectl rollout status deployment argocd-image-updater -n argocd
```

### Step 4: Verify Configuration

Check Image Updater logs for successful authentication:

```bash
# Watch logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f

# Look for:
# - "using git write-back method"
# - "using github-app authentication"
# - No authentication errors
```

### Step 5: Test Write-Back

Trigger a test image update:

```bash
# Option A: Push a new image tag
docker tag myimage:v1 593517239005.dkr.ecr.eu-west-2.amazonaws.com/hello-goldenpath-idp:test-$(git rev-parse --short HEAD)
docker push 593517239005.dkr.ecr.eu-west-2.amazonaws.com/hello-goldenpath-idp:test-$(git rev-parse --short HEAD)

# Option B: Force annotation update (ArgoCD will trigger Image Updater)
kubectl annotate application hello-goldenpath-idp -n argocd \
  argocd-image-updater.argoproj.io/force-update="$(date +%s)" --overwrite
```

Check for git commit in the app repository:

```bash
# Check recent commits
cd /path/to/hello-goldenpath-idp
git pull
git log --oneline -5

# Expected: commit from argocd-image-updater
# "build: update image hello-goldenpath-idp to test-a1b2c3d"
```

## Verification Checklist

- [ ] Secret `github-app-image-updater` exists in `argocd` namespace
- [ ] Secret contains `app-id`, `installation-id`, `private-key` keys
- [ ] Image Updater pod is running without CrashLoopBackOff
- [ ] Logs show "using github-app authentication"
- [ ] Test image push results in git commit to app repo

## Troubleshooting

### Secret Not Found

**Symptom:**
```
MountVolume.SetUp failed for volume "github-app-creds": secret "github-app-image-updater" not found
```

**Resolution:**
1. Verify secret exists: `kubectl get secret github-app-image-updater -n argocd`
2. If missing, run Step 2 above
3. For dev environments, ensure `optional: true` is set in values

### Authentication Failed

**Symptom:**
```
error authenticating to git repository: authentication required
```

**Resolution:**
1. Verify App ID matches GitHub App
2. Verify Installation ID matches the org installation
3. Verify private key format includes header/footer:
   ```
   -----BEGIN RSA PRIVATE KEY-----
   ...
   -----END RSA PRIVATE KEY-----
   ```
4. Re-download private key from GitHub and update secret

### Permission Denied

**Symptom:**
```
error pushing to git repository: permission denied (publickey)
```

**Resolution:**
1. Verify GitHub App has "Contents: Read and write" permission
2. Verify app is installed on target repository
3. Re-install app on the repository if permissions changed

### Image Updater Not Detecting New Images

**Symptom:** New ECR images not triggering updates

**Resolution:**
1. Check registry configuration in values:
   ```yaml
   config:
     registries:
       - name: ECR
         api_url: https://593517239005.dkr.ecr.eu-west-2.amazonaws.com
   ```
2. Verify ECR credentials secret exists
3. Check Application annotations for correct image spec

## Rollback

To disable pipeline (revert to digest-only):

```bash
# Delete the secret
kubectl delete secret github-app-image-updater -n argocd

# For non-dev environments, update values to optional: true temporarily
# Or revert Application annotations to use digest strategy
```

## Related Documentation

- [ADR-0174: Pipeline Decoupling](../../adrs/ADR-0174-pipeline-decoupling-from-cluster-bootstrap.md)
- [ADR-0170: Build Pipeline Architecture](../../adrs/ADR-0170-build-pipeline-architecture.md)
- [RB-0036: GitHub App Setup](./RB-0036-github-app-image-updater.md)
- [GOV-0012: Build Pipeline Standards](../../10-governance/policies/GOV-0012-build-pipeline-standards.md)
