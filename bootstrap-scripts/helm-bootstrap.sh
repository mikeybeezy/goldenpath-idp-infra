#!/usr/bin/env bash
set -euo pipefail

# bootstrap Helm-based GitOps tooling onto a new EKS cluster.
# Assumes kubectl context is already pointing at the target cluster.
# 1. installs Argo CD (default) and
# 2. configures Argo CD to sync the gitops/ directory in this repo.
# For Flux, swap out the installation block below.

REPO_URL="${REPO_URL:-git@github.com:your-org/goldenpath-idp-infra.git}"
GIT_PATH="${GIT_PATH:-gitops}"
ARGO_NAMESPACE="${ARGO_NAMESPACE:-argocd}"

if ! command -v kubectl >/dev/null; then
  echo "kubectl is required" >&2
  exit 1
fi
if ! command -v helm >/dev/null; then
  echo "helm is required" >&2
  exit 1
fi

kubectl create namespace "$ARGO_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

helm repo add argo https://argoproj.github.io/argo-helm >/dev/null
helm upgrade --install argocd argo/argo-cd \
  --namespace "$ARGO_NAMESPACE" \
  --set server.service.type=LoadBalancer \
  --set configs.params."server\.insecure"=true

cat <<APP | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: idp-gitops
  namespace: $ARGO_NAMESPACE
spec:
  destination:
    namespace: default
    server: https://kubernetes.default.svc
  project: default
  source:
    repoURL: $REPO_URL
    targetRevision: HEAD
    path: $GIT_PATH
    directory:
      recurse: true
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
APP

cat <<'NOTE'
Helm bootstrap finished. Grab the Argo CD admin password with:
  kubectl -n $ARGO_NAMESPACE get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
NOTE

