---
id: 09_PLATFORM_DASHBOARD_CATALOG
title: Platform Dashboard Catalog
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
category: observability
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
relates_to:
  - ADR-0066-platform-dashboards-as-code
  - CL-0020-golden-signals-dashboard
  - agent_session_summary
---
## Platform Dashboard Catalog

**Status:** Living
**Owner:** platform
**Refresh:** As new dashboards are added

This catalog documents the standard observability dashboards provided "out of the box" by the Golden Path IDP.

---

## 1. Cluster Overview

**File:** `gitops/helm/kube-prometheus-stack/dashboards/cluster-overview.yaml`
**Audience:** Platform Engineers, SREs.

### Purpose (Cluster Overview)

The "Bird's Eye View" of the cluster. Use this to determine if a problem is **Systemic** (Infrastructure/Capacity) or **Localized** (specific workload).

### Key Panels (Cluster Overview)

* **Cluster Capacity (Gauges):**
  * **CPU/Memory:** Aggregate saturation across all nodes.
  * *Green (<75%)*: Healthy.
  * *Orange (>75%)*: Warning. Review HPA/Cluster Autoscaler limits.
  * *Red (>90%)*: Critical. Risk of eviction/OOM.
* **Nodes Ready:** Count of healthy worker nodes.
* **Workload Health:**
  * **Pods Not Ready:** Namespace breakdown of pods in `Pending`, `CrashLoopBackOff`, or `Error` states.
  * **Container Restarts:** The top 5 "churning" pods. High restarts usually indicate crashing applications or OOMKilled events.

---

## 2. Platform Health

**File:** `gitops/helm/kube-prometheus-stack/dashboards/platform-health.yaml`
**Audience:** Platform Engineers.

### Purpose (Platform Health)

Monitors the "Plumbing" of the IDP itself. Use this when deployments are failing or external access is broken.

### Key Panels (Platform Health)

* **GitOps Health (ArgoCD):**
  * **Degraded Apps:** Applications where the deployment is failing (Health Checks failing).
  * **Out of Sync Apps:** Applications where the cluster state does not match Git.
* **Critical Addons:**
  * **Ingress Availability:** % of NGINX controller replicas online. (Drop < 100% means potential downtime).
  * **External Secrets:** Rate of synchronization errors (e.g., IAM permission failures fetching secrets).

---

## 3. Application Golden Signals (Default)

**File:** `apps/fast-api-app-template/dashboards/configmap-dashboard.yaml`
**Audience:** Application Developers.

### Purpose (Application Golden Signals)

The standard View automatically provisioned for every new service created via the Backstage template.

### Key Panels (Application Golden Signals)

* **RED Method (User Experience):**
  * **Request Rate:** Traffic volume.
  * **Error Rate:** % of 5xx errors.
  * **Latency (P95):** How slow is the "tail" experience?
* **Saturation (Cause Analysis):**
  * **CPU/Memory:** Is the pod hitting its resource limits?
* **Logs (Investigation):**
  * **Recent Errors:** Real-time log stream of error lines correlated to the selected time range.

---

## 4. Tooling Dashboards (Platform Services)

The platform provides dedicated Golden Signals dashboards for each core tooling application. These are deployed as ConfigMaps and auto-discovered by Grafana.

### 4.1 Backstage Dashboard

**File:** `gitops/helm/tooling-dashboards/backstage-dashboard.yaml`
**Namespace:** `backstage`
**Audience:** Platform Engineers, Developer Experience Team.

#### Backstage Panels

* **RED Metrics:** Request Rate, Error Rate (4xx/5xx), Latency (P50/P95/P99)
* **Saturation:** CPU/Memory usage, Pod Restarts
* **Logs:** Error logs and full application logs via Loki

### 4.2 Keycloak Dashboard

**File:** `gitops/helm/tooling-dashboards/keycloak-dashboard.yaml`
**Namespace:** `keycloak`
**Audience:** Platform Engineers, Security Team.

#### Keycloak Panels

* **Auth Metrics:** Login Attempts (success/failed), Active Sessions
* **RED Metrics:** HTTP Request Rate, Error Rate, Login Failure Rate
* **Duration:** HTTP Latency percentiles
* **Saturation:** CPU/Memory, JVM Heap Usage
* **Logs:** Authentication events and errors

### 4.3 ArgoCD Dashboard

**File:** `gitops/helm/tooling-dashboards/argocd-dashboard.yaml`
**Namespace:** `argocd`
**Audience:** Platform Engineers, SREs.

#### ArgoCD Panels

* **GitOps Health:** Total Apps, Healthy, Degraded, Out of Sync counts
* **RED Metrics:** API Request Rate (HTTP/gRPC), Error Rate, Duration
* **Operations:** Sync Operations Rate, Git Operations Rate
* **Saturation:** CPU/Memory by component (server, repo-server, controller)
* **Logs:** Sync events and reconciliation errors

### 4.4 Kong Dashboard

**File:** `gitops/helm/tooling-dashboards/kong-dashboard.yaml`
**Namespace:** `kong-system`
**Audience:** Platform Engineers, Network/SRE Team.

#### Kong Panels

* **Traffic:** Total Request Rate, Requests by Status Code
* **RED Metrics:** Error Rate (4xx/5xx), Request Latency, Upstream Latency
* **Connections:** Active Connections, Bandwidth In/Out
* **Health:** Upstream Health status
* **Logs:** Kong errors, warnings, and upstream issues

---

## How to edit these dashboards

These dashboards are managed as **Code**.

1. **Do not save changes in Grafana UI.** They will be lost.
2. Edit the JSON in the corresponding file path.
3. Commit and Push.
4. ArgoCD will sync the change.
