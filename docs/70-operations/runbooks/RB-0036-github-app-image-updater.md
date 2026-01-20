---
id: RB-0036
title: GitHub App Setup for ArgoCD Image Updater
type: runbook
relates_to:
  - ADR-0170
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - EC-0005-kubernetes-operator-framework
  - GOV-0012-build-pipeline-standards
  - GOV-0015-build-pipeline-testing-matrix
  - RB-0037
  - argocd_image_updater
  - session-2026-01-19-build-pipeline-architecture
tags:
  - github-app
  - image-updater
  - gitops
  - authentication
  - breakglass
category: runbooks
---
# RB-0036: GitHub App Setup for ArgoCD Image Updater

## Purpose

Configure a GitHub App for ArgoCD Image Updater to write back image tag changes
to Git repositories. This replaces deploy keys with a more secure, org-wide
authentication method with automatic token rotation.

**This runbook is the breakglass procedure for platform team members.**

## Quick Reference

| Item | Value |
|------|-------|
| App Name | `goldenpath-image-updater` |
| App ID | `2690765` |
| Installation ID | `105100693` |
| AWS Secret Path | `goldenpath/{env}/github-app/image-updater` |
| K8s Secret Name | `github-app-image-updater` |
| K8s Namespace | `argocd` |

## Prerequisites

- GitHub organization admin access (or personal account for mikeybeezy)
- AWS CLI configured with Secrets Manager access
- kubectl access to target cluster (for K8s secret creation)
- jq installed locally

## Why GitHub App over Deploy Keys?

| Aspect | Deploy Key | GitHub App |
|--------|------------|------------|
| Scope | Single repo only | Org-wide or multi-repo |
| Token rotation | Manual | Automatic (1-hour expiry) |
| Audit trail | Limited | Rich (app name, installation ID) |
| Setup effort | Low per repo | Medium once, then zero |
| Multi-repo | One key per repo | One app covers all |

---

## Part A: One-Time GitHub App Setup

> **Note:** This only needs to be done once. If the GitHub App already exists,
> skip to Part B.

### Step A1: Create GitHub App

1. Navigate to GitHub:
   - **For personal account:** Settings → Developer settings → GitHub Apps
   - **For organization:** Organization Settings → Developer settings → GitHub Apps

2. Click **New GitHub App**

3. Fill in the form:

   | Field | Value |
   |-------|-------|
   | App name | `goldenpath-image-updater` |
   | Homepage URL | `https://github.com/mikeybeezy/goldenpath-idp-infra` |
   | Webhook | **Uncheck** "Active" |

4. Set **Permissions**:

   | Permission | Access |
   |------------|--------|
   | Repository: Contents | **Read and write** |
   | Repository: Metadata | **Read-only** |
   | Organization permissions | None required |

5. Under "Where can this GitHub App be installed?":
   - Select **"Only on this account"**

6. Click **Create GitHub App**

7. **Record the App ID** displayed on the page (e.g., `2690765`)

### Step A2: Generate Private Key

1. On the GitHub App page, scroll down to **Private keys** section

2. Click **Generate a private key**

3. A `.pem` file will automatically download (e.g., `goldenpath-image-updater.2026-01-19.private-key.pem`)

4. **Save this file securely** - GitHub does not store it and cannot recover it

> **Security:** Never commit `.pem` files to git. Add `*.pem` to `.gitignore`.

### Step A3: Install the App on Repositories

1. On the GitHub App page, click **Install App** (left sidebar)

2. Select your account/organization

3. Choose **Selected repositories** (recommended)

4. Add repositories that need image updates:
   - `hello-goldenpath-idp`
   - (Add more app repos as needed)

5. Click **Install**

6. **Record the Installation ID** from the URL:
   ```
   https://github.com/settings/installations/105100693
                                             ^^^^^^^^^
                                             Installation ID
   ```

> **Tip:** You can add more repositories later by going to:
> Settings → Applications → Installed GitHub Apps → Configure

---

## Part B: Store Credentials in AWS Secrets Manager

This stores the GitHub App credentials for use by the pipeline and cluster.

### Step B1: Prepare the Private Key

```bash
# Set variables
APP_ID="2690765"
INSTALLATION_ID="105100693"
PEM_FILE="/path/to/goldenpath-image-updater.YYYY-MM-DD.private-key.pem"
ENV="dev"  # Change for each environment: dev, test, staging, prod
REGION="eu-west-2"

# Read private key
PRIVATE_KEY=$(cat "$PEM_FILE")
```

### Step B2: Create AWS Secret

```bash
# Create the secret with proper JSON escaping
aws secretsmanager create-secret \
  --name "goldenpath/${ENV}/github-app/image-updater" \
  --secret-string "{\"appID\":\"${APP_ID}\",\"installationID\":\"${INSTALLATION_ID}\",\"privateKey\":$(echo "$PRIVATE_KEY" | jq -Rs .)}" \
  --region "$REGION"
```

**Expected output:**
```json
{
    "ARN": "arn:aws:secretsmanager:eu-west-2:593517239005:secret:goldenpath/dev/github-app/image-updater-XXXXXX",
    "Name": "goldenpath/dev/github-app/image-updater",
    "VersionId": "..."
}
```

### Step B3: Verify the Secret

```bash
# Verify secret was created correctly
aws secretsmanager get-secret-value \
  --secret-id "goldenpath/${ENV}/github-app/image-updater" \
  --query SecretString --output text \
  --region "$REGION" | jq .
```

### Step B4: Repeat for Other Environments

```bash
# For test
ENV="test" && aws secretsmanager create-secret \
  --name "goldenpath/${ENV}/github-app/image-updater" \
  --secret-string "{\"appID\":\"${APP_ID}\",\"installationID\":\"${INSTALLATION_ID}\",\"privateKey\":$(echo "$PRIVATE_KEY" | jq -Rs .)}" \
  --region "$REGION"

# For staging
ENV="staging" && aws secretsmanager create-secret \
  --name "goldenpath/${ENV}/github-app/image-updater" \
  --secret-string "{\"appID\":\"${APP_ID}\",\"installationID\":\"${INSTALLATION_ID}\",\"privateKey\":$(echo "$PRIVATE_KEY" | jq -Rs .)}" \
  --region "$REGION"

# For prod
ENV="prod" && aws secretsmanager create-secret \
  --name "goldenpath/${ENV}/github-app/image-updater" \
  --secret-string "{\"appID\":\"${APP_ID}\",\"installationID\":\"${INSTALLATION_ID}\",\"privateKey\":$(echo "$PRIVATE_KEY" | jq -Rs .)}" \
  --region "$REGION"
```

### Step B5: Clean Up Local Private Key

```bash
# Delete the .pem file - it's now safely in AWS Secrets Manager
rm "$PEM_FILE"

# Ensure .pem files are in .gitignore
echo "*.pem" >> .gitignore
```

---

## Part C: Create Kubernetes Secret (Per Cluster)

> **Preferred method:** Use `make pipeline-enable ENV=<env>` from RB-0037.
> This section is the manual breakglass procedure.

### Step C1: Fetch Credentials from AWS

```bash
ENV="dev"  # Change per environment
REGION="eu-west-2"

# Fetch the secret
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "goldenpath/${ENV}/github-app/image-updater" \
  --query SecretString --output text \
  --region "$REGION")

# Extract values
APP_ID=$(echo "$SECRET_JSON" | jq -r '.appID')
INSTALLATION_ID=$(echo "$SECRET_JSON" | jq -r '.installationID')
PRIVATE_KEY=$(echo "$SECRET_JSON" | jq -r '.privateKey')

# Verify extraction
echo "App ID: $APP_ID"
echo "Installation ID: $INSTALLATION_ID"
echo "Private Key length: $(echo "$PRIVATE_KEY" | wc -c) bytes"
```

### Step C2: Create Kubernetes Secret

```bash
# Ensure correct kubectl context
kubectl config current-context

# Create the secret
kubectl create secret generic github-app-image-updater \
  --namespace argocd \
  --from-literal=app-id="$APP_ID" \
  --from-literal=installation-id="$INSTALLATION_ID" \
  --from-literal=private-key="$PRIVATE_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Step C3: Restart Image Updater

```bash
# Restart to pick up the new secret
kubectl rollout restart deployment/argocd-image-updater -n argocd

# Watch the rollout
kubectl rollout status deployment/argocd-image-updater -n argocd
```

### Step C4: Verify Secret Mounted

```bash
# Check the pod has the secret mounted
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-image-updater -o yaml | grep -A5 "volumeMounts"

# Check logs for authentication success
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater --tail=50
```

---

## Part D: Verification

### Test the Full Flow

1. **Push a new image:**
   ```bash
   docker push 593517239005.dkr.ecr.eu-west-2.amazonaws.com/hello-goldenpath-idp:latest
   ```

2. **Watch Image Updater logs:**
   ```bash
   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f
   ```

3. **Verify git commit appears** in the app repo (e.g., `hello-goldenpath-idp`)

4. **Check the commit author** should be `goldenpath-image-updater[bot]`

---

## Troubleshooting

### Issue: Authentication Failed

**Symptom:**
```
error authenticating to git repository: authentication required
```

**Resolution:**
1. Verify App ID and Installation ID are correct
2. Check private key format (must include `-----BEGIN RSA PRIVATE KEY-----` header)
3. Verify app is installed on the target repository
4. Check the secret has all three keys: `app-id`, `installation-id`, `private-key`

```bash
# Debug: Check secret contents
kubectl get secret github-app-image-updater -n argocd -o jsonpath='{.data}' | jq -r 'to_entries[] | "\(.key): \(.value | @base64d | length) bytes"'
```

### Issue: Permission Denied

**Symptom:**
```
error pushing to git repository: permission denied
```

**Resolution:**
1. Verify GitHub App has "Contents: Read and write" permission
2. Re-install the app if permissions were changed after installation
3. Check the app is installed on the specific repository

### Issue: Rate Limited

**Symptom:**
```
error: API rate limit exceeded
```

**Resolution:**
- GitHub App has higher rate limits than personal tokens (5000/hour)
- If hitting limits, reduce image-updater check interval in values

### Issue: Secret Not Found in AWS

**Symptom:**
```
An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation
```

**Resolution:**
1. Verify the secret path matches: `goldenpath/{env}/github-app/image-updater`
2. Check AWS region is correct (`eu-west-2`)
3. Verify IAM permissions allow `secretsmanager:GetSecretValue`

---

## Secret Rotation

GitHub App private keys can be rotated without downtime:

1. **Generate new key** in GitHub App settings (Private keys section)
2. **Update AWS Secrets Manager:**
   ```bash
   aws secretsmanager update-secret \
     --secret-id "goldenpath/${ENV}/github-app/image-updater" \
     --secret-string "{\"appID\":\"${APP_ID}\",\"installationID\":\"${INSTALLATION_ID}\",\"privateKey\":$(cat new-key.pem | jq -Rs .)}" \
     --region eu-west-2
   ```
3. **Recreate K8s secret** (repeat Part C)
4. **Restart image-updater pod**
5. **Delete old key** from GitHub App settings (after verifying new key works)

---

## Architecture Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub                                       │
│  ┌─────────────────┐     ┌─────────────────┐                        │
│  │ GitHub App      │     │ App Repo        │                        │
│  │ (goldenpath-    │────▶│ (hello-         │                        │
│  │  image-updater) │     │  goldenpath-idp)│                        │
│  └─────────────────┘     └─────────────────┘                        │
│         │                        ▲                                   │
│         │ authenticates          │ git push                          │
│         ▼                        │                                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                              │
│  ┌─────────────────┐     ┌─────────────────┐                        │
│  │ Image Updater   │────▶│ K8s Secret      │                        │
│  │ Pod             │     │ (github-app-    │                        │
│  │                 │     │  image-updater) │                        │
│  └─────────────────┘     └─────────────────┘                        │
│                                  ▲                                   │
│                                  │ created from                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS Secrets Manager                               │
│  ┌─────────────────────────────────────────┐                        │
│  │ goldenpath/{env}/github-app/image-updater│                        │
│  │ {appID, installationID, privateKey}     │                        │
│  └─────────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [RB-0037: Pipeline Enablement](./RB-0037-pipeline-enablement.md) - Automated K8s secret creation
- [ADR-0170: Build Pipeline Architecture](../../adrs/ADR-0170-build-pipeline-architecture.md)
- [ADR-0174: Pipeline Decoupling](../../adrs/ADR-0174-pipeline-decoupling-from-cluster-bootstrap.md)
- [GOV-0012: Build Pipeline Standards](../../10-governance/policies/GOV-0012-build-pipeline-standards.md)
- [ArgoCD Image Updater Docs](https://argocd-image-updater.readthedocs.io/)
