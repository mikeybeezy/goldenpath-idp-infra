# Grafana Configuration Module

Note: For in-cluster Grafana managed by `kube-prometheus-stack`, the default
path is Helm + ConfigMaps. Use this module only when managing **external**
Grafana (Grafana Cloud) or when explicitly opting into Terraform-managed
Grafana configuration.

Helm deploys Grafana as part of `kube-prometheus-stack` (`gitops/helm/kube-prometheus-stack`). This module uses the Grafana Terraform provider to manage what lives inside Grafana:

- Datasources (Loki, Prometheus, CloudWatch, Datadog, …)
- Dashboards and folders
- Alert rules and contact points

Keeping these in Terraform ensures observability contracts are versioned, reviewed, and synced across environments. Helm handles pods/services; this module handles dashboards and signal wiring.
