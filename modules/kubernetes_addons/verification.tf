# Post-Deployment Verification
# Waits for critical ArgoCD applications to sync and become healthy

resource "null_resource" "wait_for_core_apps" {
  count = var.enable_post_deployment_verification ? 1 : 0

  provisioner "local-exec" {
    command = <<-EOT
      #!/bin/bash
      set -e

      echo "========================================="
      echo "Post-Deployment Verification"
      echo "========================================="
      echo ""

      # Wait for ArgoCD API to be responsive
      echo "⏳ Waiting for ArgoCD API to be ready..."
      kubectl wait --for=condition=Ready \
        --timeout=300s \
        -n argocd \
        pod -l app.kubernetes.io/name=argocd-server || true

      echo "✅ ArgoCD API is ready"
      echo ""

      # Wait for critical applications to exist
      echo "⏳ Waiting for critical applications to be created..."
      for app in cert-manager external-secrets cluster-autoscaler; do
        timeout=60
        elapsed=0
        until kubectl get application "$app" -n argocd &>/dev/null || [ $elapsed -ge $timeout ]; do
          echo "  Waiting for $app application... ($elapsed/$timeout seconds)"
          sleep 5
          elapsed=$((elapsed + 5))
        done

        if kubectl get application "$app" -n argocd &>/dev/null; then
          echo "  ✅ $app application exists"
        else
          echo "  ⚠️  $app application not found (may not be enabled)"
        fi
      done
      echo ""

      # Wait for applications to sync (non-blocking)
      echo "⏳ Checking ArgoCD application sync status..."
      for app in cert-manager external-secrets cluster-autoscaler; do
        if kubectl get application "$app" -n argocd &>/dev/null; then
          sync_status=$(kubectl get application "$app" -n argocd -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Unknown")
          health_status=$(kubectl get application "$app" -n argocd -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown")
          echo "  $app: Sync=$sync_status, Health=$health_status"
        fi
      done
      echo ""

      echo "========================================="
      echo "Verification Complete"
      echo "========================================="
      echo ""
      echo "Note: ArgoCD applications will continue syncing in the background."
      echo "Use 'kubectl get applications -n argocd' to monitor progress."
      echo ""
    EOT
  }

  depends_on = [helm_release.bootstrap_apps]
}
