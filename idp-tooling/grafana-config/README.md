# Grafana Configuration Module

Helm deploys Grafana the application (`gitops/helm/grafana`). This module uses the Grafana Terraform provider to manage what lives inside Grafana:

- Datasources (Loki, Prometheus, CloudWatch, Datadog, …)
- Dashboards and folders
- Alert rules and contact points

Keeping these in Terraform ensures observability contracts are versioned, reviewed, and synced across environments. Helm handles pods/services; this module handles dashboards and signal wiring.
