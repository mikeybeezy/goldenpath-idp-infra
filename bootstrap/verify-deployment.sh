#!/usr/bin/env bash
# Single-Build Deployment Verification Script
# Verifies that EKS cluster and ArgoCD applications are healthy after Terraform deployment
#
# Usage:
#   ./bootstrap/verify-deployment.sh <cluster-name> <region>
#
# Example:
#   ./bootstrap/verify-deployment.sh goldenpath-dev-eks eu-west-2

set -euo pipefail

cluster_name="${1:?Missing cluster name. Usage: $0 <cluster-name> <region>}"
region="${2:?Missing region. Usage: $0 <cluster-name> <region>}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
  echo ""
  echo -e "${BLUE}=========================================${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}=========================================${NC}"
  echo ""
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
clear
echo -e "${BLUE}"
cat << "EOF"
 ╔═══════════════════════════════════════════════════════════╗
 ║                                                           ║
 ║   Golden Path IDP - Deployment Verification               ║
 ║                                                           ║
 ╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "Cluster: $cluster_name"
print_info "Region: $region"
echo ""

# Step 1: Configure kubectl
print_header "Step 1: Configure kubectl"
if aws eks update-kubeconfig --name "$cluster_name" --region "$region" &>/dev/null; then
  print_success "kubectl configured for cluster $cluster_name"
else
  print_error "Failed to configure kubectl. Is the cluster accessible?"
  exit 1
fi

# Step 2: Verify cluster connectivity
print_header "Step 2: Verify Cluster Connectivity"
if kubectl cluster-info &>/dev/null; then
  print_success "Cluster is accessible"
  kubectl version --short 2>/dev/null || kubectl version
else
  print_error "Cannot connect to cluster"
  exit 1
fi

# Step 3: Check node status
print_header "Step 3: Check Node Status"
node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d ' ')
ready_count=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready " || echo "0")

if [ "$ready_count" -ge 3 ]; then
  print_success "$ready_count/$node_count nodes are Ready"
  kubectl get nodes
else
  print_warning "Only $ready_count/$node_count nodes are Ready (expected at least 3)"
  kubectl get nodes
fi
echo ""

# Step 4: Check ArgoCD installation
print_header "Step 4: Check ArgoCD Installation"
if kubectl get namespace argocd &>/dev/null; then
  print_success "ArgoCD namespace exists"

  # Check ArgoCD pods
  argocd_pods=$(kubectl get pods -n argocd --no-headers 2>/dev/null | wc -l | tr -d ' ')
  argocd_ready=$(kubectl get pods -n argocd --no-headers 2>/dev/null | grep -c "Running" || echo "0")

  if [ "$argocd_ready" -ge 5 ]; then
    print_success "ArgoCD is running ($argocd_ready/$argocd_pods pods Running)"
  else
    print_warning "ArgoCD may not be fully ready ($argocd_ready/$argocd_pods pods Running)"
  fi

  kubectl get pods -n argocd
else
  print_error "ArgoCD namespace not found"
  exit 1
fi
echo ""

# Step 5: Check ArgoCD Applications
print_header "Step 5: Check ArgoCD Applications"
if kubectl get applications -n argocd &>/dev/null; then
  app_count=$(kubectl get applications -n argocd --no-headers 2>/dev/null | wc -l | tr -d ' ')

  if [ "$app_count" -gt 0 ]; then
    print_success "Found $app_count ArgoCD Applications"
    echo ""

    # Show application status
    kubectl get applications -n argocd -o custom-columns=\
NAME:.metadata.name,\
SYNC:.status.sync.status,\
HEALTH:.status.health.status,\
MESSAGE:.status.conditions[0].message 2>/dev/null || \
    kubectl get applications -n argocd

    echo ""

    # Count healthy apps
    synced_count=$(kubectl get applications -n argocd -o json 2>/dev/null | \
      jq '[.items[] | select(.status.sync.status == "Synced")] | length' 2>/dev/null || echo "0")
    healthy_count=$(kubectl get applications -n argocd -o json 2>/dev/null | \
      jq '[.items[] | select(.status.health.status == "Healthy")] | length' 2>/dev/null || echo "0")

    if [ "$synced_count" == "$app_count" ] && [ "$healthy_count" == "$app_count" ]; then
      print_success "All $app_count applications are Synced and Healthy"
    else
      print_warning "$synced_count/$app_count Synced, $healthy_count/$app_count Healthy"
      print_info "Applications may still be syncing in the background"
    fi
  else
    print_warning "No ArgoCD Applications found"
    print_info "Applications may still be deploying"
  fi
else
  print_error "Cannot list ArgoCD Applications"
fi
echo ""

# Step 6: Check critical platform components
print_header "Step 6: Check Critical Platform Components"

check_component() {
  local name=$1
  local namespace=$2
  local selector=$3

  if kubectl get pods -n "$namespace" -l "$selector" --no-headers 2>/dev/null | grep -q "Running"; then
    print_success "$name is running"
    return 0
  else
    print_warning "$name may not be ready"
    return 1
  fi
}

check_component "Metrics Server" "kube-system" "k8s-app=metrics-server"
check_component "AWS Load Balancer Controller" "kube-system" "app.kubernetes.io/name=aws-load-balancer-controller"
check_component "Cluster Autoscaler" "kube-system" "app.kubernetes.io/name=aws-cluster-autoscaler"

if kubectl get pods -n argocd -l "app.kubernetes.io/name=argocd-image-updater" --no-headers 2>/dev/null | grep -q "Running"; then
  print_success "ArgoCD Image Updater is running"
else
  print_warning "ArgoCD Image Updater not found (may not be enabled)"
fi

echo ""

# Step 7: Check storage add-ons
print_header "Step 7: Check Storage Add-ons"
if kubectl get pods -n kube-system -l "app=ebs-csi-controller" --no-headers 2>/dev/null | grep -q "Running"; then
  print_success "EBS CSI Driver is running"
else
  print_warning "EBS CSI Driver not found"
fi

if kubectl get pods -n kube-system -l "app=efs-csi-controller" --no-headers 2>/dev/null | grep -q "Running"; then
  print_success "EFS CSI Driver is running"
else
  print_warning "EFS CSI Driver not found"
fi
echo ""

# Step 8: Get ArgoCD admin credentials
print_header "Step 8: ArgoCD Access Information"
if kubectl get secret argocd-initial-admin-secret -n argocd &>/dev/null; then
  admin_password=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' 2>/dev/null | base64 -d 2>/dev/null || echo "Unable to retrieve")

  print_info "ArgoCD Admin Credentials:"
  echo "  Username: admin"
  echo "  Password: $admin_password"
  echo ""
  print_info "Access ArgoCD UI:"
  echo "  kubectl port-forward svc/argocd-server -n argocd 8080:443"
  echo "  Then visit: https://localhost:8080"
else
  print_warning "ArgoCD admin secret not found"
fi
echo ""

# Step 9: Summary
print_header "Deployment Verification Summary"

# Calculate overall health score
total_checks=10
passed_checks=0

[ "$ready_count" -ge 3 ] && ((passed_checks++))
[ "$argocd_ready" -ge 5 ] && ((passed_checks++))
[ "$app_count" -gt 0 ] && ((passed_checks++))
[ "$synced_count" == "$app_count" ] && ((passed_checks++))
[ "$healthy_count" == "$app_count" ] && ((passed_checks++))
kubectl get pods -n kube-system -l "k8s-app=metrics-server" --no-headers 2>/dev/null | grep -q "Running" && ((passed_checks++))
kubectl get pods -n kube-system -l "app.kubernetes.io/name=aws-load-balancer-controller" --no-headers 2>/dev/null | grep -q "Running" && ((passed_checks++))
kubectl get pods -n kube-system -l "app.kubernetes.io/name=aws-cluster-autoscaler" --no-headers 2>/dev/null | grep -q "Running" && ((passed_checks++))
kubectl get pods -n kube-system -l "app=ebs-csi-controller" --no-headers 2>/dev/null | grep -q "Running" && ((passed_checks++))
kubectl get secret argocd-initial-admin-secret -n argocd &>/dev/null && ((passed_checks++))

health_percentage=$((passed_checks * 100 / total_checks))

if [ "$health_percentage" -ge 90 ]; then
  print_success "Platform Health: $health_percentage% ($passed_checks/$total_checks checks passed)"
  print_success "Deployment verification PASSED"
elif [ "$health_percentage" -ge 70 ]; then
  print_warning "Platform Health: $health_percentage% ($passed_checks/$total_checks checks passed)"
  print_info "Some components may still be initializing"
else
  print_error "Platform Health: $health_percentage% ($passed_checks/$total_checks checks passed)"
  print_error "Deployment may have issues - review logs above"
fi

echo ""
print_info "For detailed application status:"
echo "  kubectl get applications -n argocd"
echo ""
print_info "To watch application sync progress:"
echo "  watch kubectl get applications -n argocd"
echo ""

exit 0
