<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
# Platform Architecture

## Stack
*   **Cloud**: AWS (eu-west-2)
*   **Container**: EKS (Kubernetes)
*   **IaC**: Terraform (`envs/`, `modules/`)
*   **GitOps**: ArgoCD (`gitops/argocd/`)
*   **Portal**: Backstage (`backstage-helm/`)
*   **Auth**: Keycloak
*   **Secrets**: ExternalSecrets -> AWS Secrets Manager

## Key Locations
*   `bootstrap/`: Scripts to bring up the world.
*   `gitops/argocd/apps/`: Where apps are defined.
*   `gitops/helm/`: Local Helm charts.
*   `docs/adrs/`: Architectural Decision Records (Read these!).

## "Zero-Touch" Philosophy
*   **DNS**: ExternalDNS + Kong Automatically creates `*.dev.goldenpathidp.io`.
*   **Dashboards**: ConfigMaps with label `grafana_dashboard=1` are auto-discovered.
*   **Teardown**: `bootstrap/60_tear_down_clean_up/` must achieve 0 orphans.
