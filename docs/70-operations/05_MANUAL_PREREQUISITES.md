---
id: 05_MANUAL_PREREQUISITES
title: Manual Prerequisites & One-Time Setup
---

# Manual Prerequisites & One-Time Setup

This document captures the **only two manual steps** required to bring the "Dev" (AWS) environment to a fully healthy, accessible state after the initial infrastructure provisioning.

Since we do not commit secrets to Git or manage public DNS zones via Terraform (yet), these are "One-Time Actions".

## 1. Secrets (Manual Value Population)

We use **External Secrets Operator (ESO)** to sync secrets from AWS Secrets Manager into the cluster.
Terraform automatically creates the *containers* (the Secret ARNs) with dummy/empty values, but **you must populate the actual sensitive values** via the AWS Console.

### The Secrets to Set

Navigate to **AWS Secrets Manager** and find the following secrets. Update their **Secret Key/Value** pairs:

#### `goldenpath/dev/keycloak/admin`
| Key | Value Type | Description |
| :--- | :--- | :--- |
| `admin-password` | String | A strong password for the initial `user` account (username is `user` by default). |

#### `goldenpath/dev/backstage/secrets`
| Key | Value Type | Description |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | String | A Personal Access Token (Classic) with `repo` and `workflow` scopes. |
| `OIDC_CLIENT_SECRET` | String | The Client Secret from Keycloak (Realm `goldenpath` -> Client `backstage` -> Credentials). *Note: You can get this after Keycloak is accessible.* |

---

## 2. Ingress & DNS (Route53)

Our Helm charts use **Kong** as the Ingress Controller and **Cert-Manager** for SSL.
However, for Cert-Manager to complete the Let's Encrypt challenge (HTTP-01), the traffic must actually reach the cluster.

### The Check
Get the external hostname of the Kong Load Balancer (NLB):

```bash
kubectl get svc -n kong kong-proxy
# Look for EXTERNAL-IP (e.g., ad48...elb.eu-west-2.amazonaws.com)
```

### The Action
Go to your DNS Provider (e.g., Route53, GoDaddy) and create **CNAME Records** pointing to that Load Balancer hostname:

| Type | Name | Value |
| :--- | :--- | :--- |
| CNAME | `keycloak.dev.goldenpath.io` | `[Load-Balancer-Hostname]` |
| CNAME | `backstage.dev.goldenpath.io` | `[Load-Balancer-Hostname]` |
| CNAME | `argocd.dev.goldenpath.io` | `[Load-Balancer-Hostname]` |

### Why?
1.  **Connectivity**: Allows you to access the tools.
2.  **SSL**: Cert-Manager will see the DNS resolves to the cluster -> LetsEncrypt will verify ownership -> Valid HTTPS certificates will be issued.

---

### Verification
Once these two steps are done:
1.  Restart External Secrets to fetch new values immediately:
    ```bash
    kubectl rollout restart deploy -n external-secrets external-secrets
    ```
2.  Check Ingress status:
    ```bash
    kubectl get ingress -A
    # ADDRESS should match the NLB, and HOSTS should map to your URLs.
    ```
