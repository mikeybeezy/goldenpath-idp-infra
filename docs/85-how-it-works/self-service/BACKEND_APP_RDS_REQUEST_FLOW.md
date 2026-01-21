# How It Works: Backend App + RDS Request Flow

This document explains the "Golden Path" for provisioning a **Backend Application** that connects to a **Managed RDS Database**.

## The Composite Pattern
This is a "high-leverage" action. ONE request triggers TWO outcomes:
1.  **Infrastructure**: Triggers `create-rds-database.yml` to provision Postgres on the Platform RDS.
2.  **Application**: Scaffolds a new GitHub repo with code pre-wired to connect to that database.

## The Secret contract (Zero-Touch)
We use the **External Secrets Operator** (ESO) to bridge the gap between AWS and K8s.

```mermaid
sequenceDiagram
    participant IDP
    participant Actions
    participant AWS_Secrets
    participant K8s_ESO
    participant App_Pod

    IDP->>Actions: Trigger "create-rds-database"
    Actions->>AWS_Secrets: Create Secret "rds/production/mydb"
    IDP->>GitHub: Scaffold Repo with "externalsecret.yaml"
    GitHub->>ArgoCD: Sync App
    ArgoCD->>K8s_ESO: Apply ExternalSecret
    K8s_ESO->>AWS_Secrets: Fetch "rds/production/mydb"
    K8s_ESO->>K8s_Secret: Create "myapp-db-creds"
    App_Pod->>K8s_Secret: Mount envFrom
```

## Parameters

| Field | Description | Example |
| :--- | :--- | :--- |
| **App Name** | Unique identifier for your service. | `user-service` |
| **Database Name** | Postgres DB Name. | `users_db` |
| **Username** | Postgres User. | `users_app_user` |

## Output Repository Structure

```bash
user-service/
├── deploy/
│   ├── base/
│   │   ├── deployment.yaml       # Mounts secret as env
│   │   ├── externalsecret.yaml   # Syncs AWS -> K8s
│   │   └── kustomization.yaml
├── app.py                        # Connects using os.environ['DB_HOST']
└── catalog-info.yaml             # Metadata
```
