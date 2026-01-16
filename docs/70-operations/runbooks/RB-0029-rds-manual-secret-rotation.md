---
id: RB-0029-rds-manual-secret-rotation
title: RDS Manual Secret Rotation (Runbook)
type: runbook
risk_profile:
  production_impact: high
  security_risk: data
  coupling_risk: medium
reliability:
  rollback_strategy: rollback-procedure
  observability_tier: gold
  maturity: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - 30_PLATFORM_RDS_ARCHITECTURE
  - 35_TOOLING_SECRETS_LIFECYCLE
category: runbooks
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:aws-secrets-manager
  - module:rds
  - module:postgresql
breaking_change: false
---

## RDS Manual Secret Rotation (Runbook)

This runbook documents the manual process for rotating platform RDS database credentials.

### Rotation Policy

- Dev: 30 days
- Staging/Prod: 14 days

### CI Enforcement

- Daily scheduled workflow alerts when secrets approach deadline
- PR soft gate warns (non-blocking) for infrastructure changes

## Prerequisites

- AWS CLI configured with appropriate permissions
- PostgreSQL client (`psql`) installed
- Access to AWS Secrets Manager

## Step 1: Identify Secrets Requiring Rotation

Check secret ages using AWS CLI:

```bash
# List platform RDS secrets
ENVIRONMENT=dev  # Change as needed

for SECRET in \
  "goldenpath/${ENVIRONMENT}/rds/master" \
  "goldenpath/${ENVIRONMENT}/keycloak/postgres" \
  "goldenpath/${ENVIRONMENT}/backstage/postgres"; do

  echo "=== ${SECRET} ==="
  aws secretsmanager describe-secret --secret-id "${SECRET}" \
    --query '{Name:Name, LastChanged:LastChangedDate, Created:CreatedDate}' \
    --output table 2>/dev/null || echo "Not found"
done
```

## Step 2: Generate New Password

```bash
# Generate a secure password (32 chars, no special chars for DB compatibility)
NEW_PASSWORD=$(aws secretsmanager get-random-password \
  --password-length 32 \
  --exclude-characters '/@"'"'"'\\' \
  --exclude-punctuation \
  --query 'RandomPassword' \
  --output text)

echo "New password generated (keep secure, do not log in production)"
```

## Step 3: Update Database Password

Connect to RDS and change the user's password:

```bash
# Get current credentials
ENVIRONMENT=dev
SECRET_PATH="goldenpath/${ENVIRONMENT}/rds/master"

# Extract connection details
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "${SECRET_PATH}" \
  --query 'SecretString' \
  --output text)

DB_HOST=$(echo "${SECRET_JSON}" | jq -r '.host')
DB_PORT=$(echo "${SECRET_JSON}" | jq -r '.port')
DB_USER=$(echo "${SECRET_JSON}" | jq -r '.username')
DB_NAME=$(echo "${SECRET_JSON}" | jq -r '.dbname')
CURRENT_PASSWORD=$(echo "${SECRET_JSON}" | jq -r '.password')

# Connect and change password
PGPASSWORD="${CURRENT_PASSWORD}" psql \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  -c "ALTER USER ${DB_USER} WITH PASSWORD '${NEW_PASSWORD}';"
```

## Step 4: Update Secrets Manager

```bash
# Update the secret with new password
ENVIRONMENT=dev
SECRET_PATH="goldenpath/${ENVIRONMENT}/rds/master"

# Get current secret and update password fields
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "${SECRET_PATH}" \
  --query 'SecretString' \
  --output text)

NEW_SECRET_JSON=$(echo "${SECRET_JSON}" | jq \
  --arg pw "${NEW_PASSWORD}" \
  '.password = $pw | .["postgres-password"] = $pw | .["admin-password"] = $pw')

# Put new secret version
aws secretsmanager put-secret-value \
  --secret-id "${SECRET_PATH}" \
  --secret-string "${NEW_SECRET_JSON}"

echo "Secret updated: ${SECRET_PATH}"
```

## Step 5: Verify New Credentials

```bash
# Test connection with new password
PGPASSWORD="${NEW_PASSWORD}" psql \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  -c "SELECT 1 AS connection_test;"
```

## Step 6: Refresh Application Pods (if needed)

If applications cache database connections, restart pods to pick up new credentials:

```bash
# Keycloak
kubectl rollout restart deployment/keycloak -n keycloak

# Backstage
kubectl rollout restart deployment/backstage -n backstage
```

## Rotating Application-Specific Secrets

For application secrets (keycloak, backstage), follow the same process but:

1. Use the application-specific secret path
2. Update the application database user (not master)
3. Only restart that specific application

```bash
# Example for Keycloak
ENVIRONMENT=dev
SECRET_PATH="goldenpath/${ENVIRONMENT}/keycloak/postgres"
APP_USER="keycloak"

# ... follow steps 2-5 with APP_USER instead of master
```

## Rollback Procedure

If rotation fails and application cannot connect:

1. Retrieve previous secret version:

```bash
aws secretsmanager list-secret-version-ids --secret-id "${SECRET_PATH}"

# Get previous version
aws secretsmanager get-secret-value \
  --secret-id "${SECRET_PATH}" \
  --version-id "PREVIOUS_VERSION_ID"
```

1. Restore previous password in database
2. Revert secret to previous version

## Automation (V1.1)

Automated Lambda-based rotation is planned for V1.1. See ADR-0158 for roadmap.

## Related Resources

- [ADR-0158: Platform RDS Bounded Context](../../../docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md)
- [Platform RDS Architecture](../30_PLATFORM_RDS_ARCHITECTURE.md)
- [Secrets Lifecycle](../35_TOOLING_SECRETS_LIFECYCLE.md)
- [RB-0030: RDS Break-Glass Deletion](RB-0030-rds-break-glass-deletion.md)
