# Monitoring Configuration Modules

This directory holds Terraform modules for monitoring components that need API-level configuration beyond Helm:

- `grafana/` – dashboards, datasources, alert rules.
- `alertmanager/` – receivers, routing trees, notification policies.
- `fluent-bit/` – optional configmaps/templates for multi-destination log outputs.

Helm installs the workloads; these modules describe their internal configuration so alerts, dashboards, and log routing remain declarative across environments.
