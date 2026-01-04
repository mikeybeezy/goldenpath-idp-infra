---
id: 09_PLATFORM_DASHBOARD_CATALOG
title: Platform Dashboard Catalog
type: documentation
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Platform Dashboard Catalog

**Status:** Living
**Owner:** platform
**Refresh:** As new dashboards are added

This catalog documents the standard observability dashboards provided "out of the box" by the Golden Path IDP.

---

## 1. Cluster Overview

**File:** `gitops/helm/kube-prometheus-stack/dashboards/cluster-overview.yaml`
**Audience:** Platform Engineers, SREs.

### Purpose

The "Bird's Eye View" of the cluster. Use this to determine if a problem is **Systemic** (Infrastructure/Capacity) or **Localized** (specific workload).

### Key Panels

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

### Purpose

Monitors the "Plumbing" of the IDP itself. Use this when deployments are failing or external access is broken.

### Key Panels

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

### Purpose

The standard View automatically provisioned for every new service created via the Backstage template.

### Key Panels

* **RED Method (User Experience):**
  * **Request Rate:** Traffic volume.
  * **Error Rate:** % of 5xx errors.
  * **Latency (P95):** How slow is the "tail" experience?
* **Saturation (Cause Analysis):**
  * **CPU/Memory:** Is the pod hitting its resource limits?
* **Logs (Investigation):**
  * **Recent Errors:** Real-time log stream of error lines correlated to the selected time range.

---

## How to edit these dashboards

These dashboards are managed as **Code**.

1. **Do not save changes in Grafana UI.** They will be lost.
2. Edit the JSON in the corresponding file path.
3. Commit and Push.
4. ArgoCD will sync the change.
