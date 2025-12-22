# Datree Policies

Datree enforces Kubernetes best practices in two places:

1. **CI checks** – the Datree CLI runs during pull requests to catch manifest violations (e.g., missing resource limits, `:latest` tags) before code merges.
2. **Admission webhook** – the Helm chart in `gitops/helm/datree/` deploys Datree’s validating webhook so that any manifest applied to the cluster is evaluated again. If CI missed something, the webhook blocks it at runtime.

This directory stores the Datree policy definitions (YAML) and documentation on how to run the CLI locally/inside CI. Keeping policies here ensures they’re version-controlled and evolve with the platform.
