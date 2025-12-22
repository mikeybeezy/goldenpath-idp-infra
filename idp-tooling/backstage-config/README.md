# Backstage Configuration Module

Helm installs Backstage (`gitops/helm/backstage`). This Terraform module stores Backstage catalog entities, locations, groups, and plugin settings so the portal’s structure is managed as code.

Use it to:
- Register default catalog locations (Git repos, templates).
- Seed groups/users/service metadata.
- Configure integrations (GitHub, GitLab, Argo CD) via Backstage APIs.

Result: Backstage content stays version-controlled and consistent across environments; Helm only handles runtime deployment.
