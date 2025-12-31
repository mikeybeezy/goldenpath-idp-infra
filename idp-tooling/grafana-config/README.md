# Grafana Configuration Module

Helm deploys Grafana as part of `kube-prometheus-stack` (`gitops/helm/kube-prometheus-stack`). This module uses the Grafana Terraform provider to manage what lives inside Grafana:

- Datasources (Loki, Prometheus, CloudWatch, Datadog, …)
- Dashboards and folders
- Alert rules and contact points

Keeping these in Terraform ensures observability contracts are versioned, reviewed, and synced across environments. Helm handles pods/services; this module handles dashboards and signal wiring.
