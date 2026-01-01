# App Template Living Doc

This is a living reference for the team-owned app template and its structure.
It is updated whenever the template changes.

## Current Structure (ASCII)

```
apps/fast-api-app-template/
├─ README.md
├─ deployment.yaml
├─ service.yaml
├─ servicemonitor.yaml
├─ ingress.yaml
├─ serviceaccount.yaml
├─ rbac.yaml
├─ networkpolicy.yaml
├─ dashboards/
│  └─ configmap-dashboard.yaml
└─ kong/
   ├─ kong-auth-plugin.yaml
   ├─ kong-rate-limiting.yaml
   ├─ kong-consumer.yaml
   └─ kong-secret.yaml
```

## Ownership Boundaries

App-owned:
- deployment.yaml
- service.yaml
- servicemonitor.yaml
- dashboards/configmap-dashboard.yaml
- ingress.yaml values (host/path/service/ports)

Platform-owned:
- kong/*
- networkpolicy.yaml
- rbac.yaml (only when needed)

## Change Log (Living)

- 2025-12-31: Initial reference template added with placeholders and Kong +
  observability defaults.
