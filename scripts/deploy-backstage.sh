#!/bin/bash
# Purpose: Deploy Backstage with VQ Telemetry and Born Governed status.
# Value: Reclaims 15 minutes of dev time per deployment attempt through automation.

set -e

# Load VQ Logger if exists
VQ_LOGGER="./scripts/lib/vq_logger.py"
PROJECT_ROOT=$(pwd)

echo "🚀 Initializing Backstage Deployment..."

# 1. Dependency Check: CloudNativePG
if ! kubectl get customresourcedefinition clusters.postgresql.cnpg.io > /dev/null 2>&1; then
    echo "📦 Installing CloudNativePG Operator..."
    helm repo add cnpg https://cloudnative-pg.github.io/charts
    helm repo update
    helm upgrade --install cnpg cnpg/cloudnative-pg --namespace cnpg-system --create-namespace
fi

# 2. Namespace & Secret Setup
kubectl create namespace backstage --dry-run=client -o yaml | kubectl apply -f -

if [ -z "$GH_TOKEN" ]; then
    echo "⚠️  GH_TOKEN not set. Skipping GitHub integration secret."
else
    kubectl create secret generic backstage-github-token \
        --namespace backstage \
        --from-literal=token=$GH_TOKEN \
        --dry-run=client -o yaml | kubectl apply -f -
fi

# 3. Deploy DB Cluster
echo "🗄️  Provisioning PostgreSQL Cluster..."
kubectl apply -f - << EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: backstage
  namespace: backstage
spec:
  instances: 1
  primaryUpdateStrategy: unsupervised
  storage:
    size: 1Gi
  bootstrap:
    initdb:
      database: backstage
      owner: app
EOF

# 4. Deploy Backstage via Local Helm Chart
echo "🏗️  Deploying Backstage Helm Chart..."
helm upgrade --install backstage ./backstage-helm/charts/backstage \
    --namespace backstage \
    --set github.accessToken=${GH_TOKEN:-"none"}

# 5. Record Value Heartbeat
if [ -f "$VQ_LOGGER" ]; then
    echo "📈 Recording Value Heartbeat..."
    python3 "$VQ_LOGGER" --activity "backstage_deploy" --hours 0.25 --category "infrastructure"
fi

echo "✅ Backstage deployed successfully!"
echo "🔗 Access via: kubectl port-forward svc/backstage -n backstage 7007:7007"
