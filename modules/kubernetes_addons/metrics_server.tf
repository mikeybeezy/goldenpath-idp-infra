# Metrics Server
# Provides container resource metrics for HPA and kubectl top commands

resource "helm_release" "metrics_server" {
  count = var.enable_metrics_server ? 1 : 0

  name             = "metrics-server"
  repository       = "https://kubernetes-sigs.github.io/metrics-server/"
  chart            = "metrics-server"
  version          = var.metrics_server_version
  namespace        = "kube-system"
  create_namespace = false
  wait             = true
  timeout          = 300

  # Enable API priority and fairness
  set {
    name  = "apiService.create"
    value = "true"
  }

  # Additional args for EKS compatibility
  set {
    name  = "args[0]"
    value = "--kubelet-preferred-address-types=InternalIP"
  }
}
