---
id: RB-0002-grafana-access
title: Grafana Access (Runbook)
type: runbook
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
relates_to:
  - 31_EKS_ACCESS_MODEL
  - DOCS_RUNBOOKS_README
category: runbooks
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# Grafana Access (Runbook)

This runbook explains how to access Grafana locally without exposing a public
endpoint.

Use this when:

- Grafana is running but you cannot reach it externally.
- You need temporary local access for setup or validation.
- You want to avoid creating a public load balancer.

## Prerequisites

- Cluster access (`kubectl` works).
- Grafana namespace and service name.

## Step 1: Port-forward the Grafana service

Why: Creates a local tunnel to the Grafana service port.

```sh
kubectl -n <GRAFANA_NAMESPACE> port-forward svc/<GRAFANA_SERVICE> 8080:80
```

Then open `http://localhost:8080`.

## Step 2: Get the admin password (if needed)

Why: Grafana often stores the admin password in a Kubernetes Secret.

```sh
kubectl get secret -n <GRAFANA_NAMESPACE> <GRAFANA_SECRET> \
  -o jsonpath='{.data.admin-password}' | base64 --decode; echo
```

## Troubleshooting

- If the port-forward command hangs with no response, check pod status:
  `kubectl get pods -n <GRAFANA_NAMESPACE>`
- If the page loads but login fails, confirm the secret name and contents.
- If the service has no endpoints, verify that Grafana pods are `Running`.

## Related docs

- `docs/60-security/31_EKS_ACCESS_MODEL.md`
