#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# ORPHAN CLEANUP - Clean up orphaned AWS resources by BuildId tag
# =============================================================================
#
# Version: 2.2.0
# Purpose: Clean up AWS resources left behind by failed builds
#
# Key changes in 2.2.0:
#   - Added name-pattern fallback search for NAT gateways, subnets, IGWs, VPCs
#     (searches for resources with BuildId in Name tag when tag search fails)
#   - Enhanced NAT gateway wait loop with proper polling (up to 90s timeout)
#   - Added VPC dependency diagnostics on deletion failure (shows remaining
#     NAT gateways, subnets, ENIs, security groups, IGWs)
#   - Fixed NAT gateway state filter to include 'deleting' state
#
# Key changes in 2.1.0:
#   - Moved NAT gateway cleanup BEFORE ENI cleanup (NAT gateways hold ENIs)
#   - Added wait after NAT gateway deletion to allow ENI release
#   - Skip wait if no NAT gateways found
#
# Usage:
#   bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
#
# Environment variables:
#   DRY_RUN=true|false (default true) - Set to false to perform actual deletions
#   STATE_BUCKET=<bucket> - State bucket (for logging only, never modified)
#   STATE_TABLE=<table> - State table (for logging only, never modified)
#   IAM_REGION=<region> - Region for IAM operations (default us-east-1)
#   NODEGROUP_WAIT_TIMEOUT=<seconds> - Max wait for nodegroup deletion (default 600)
#   RDS_SKIP_FINAL_SNAPSHOT=true|false (default true) - Skip RDS final snapshot
#   RDS_DELETE_AUTOMATED_BACKUPS=true|false (default true) - Delete RDS backups
#
# Resources cleaned up:
#   - EKS clusters and nodegroups (with proper wait)
#   - RDS instances, subnet groups, parameter groups
#   - Load balancers (ALB/NLB/CLB) and target groups
#   - EC2 instances
#   - ENIs (unattached only)
#   - IAM roles and instance profiles
#   - NAT gateways
#   - Elastic IPs
#   - Route tables
#   - Subnets
#   - Security groups
#   - Internet gateways
#   - VPCs
#
# =============================================================================

build_id="${1:-}"
region="${2:-}"
dry_run="${DRY_RUN:-true}"
state_bucket="${STATE_BUCKET:-}"
state_table="${STATE_TABLE:-}"
iam_region="${IAM_REGION:-us-east-1}"
nodegroup_wait_timeout="${NODEGROUP_WAIT_TIMEOUT:-600}"
rds_skip_final_snapshot="${RDS_SKIP_FINAL_SNAPSHOT:-true}"
rds_delete_automated_backups="${RDS_DELETE_AUTOMATED_BACKUPS:-true}"

if [[ -z "${build_id}" || -z "${region}" ]]; then
  echo "Usage: $0 <build-id> <region>" >&2
  echo "Set DRY_RUN=false to perform deletions." >&2
  exit 1
fi

# =============================================================================
# LOGGING HELPERS
# =============================================================================

log_step() {
  local step_name="$1"
  local message="$2"
  echo "[STEP: ${step_name}] ${message}"
}

log_info() {
  echo "[INFO] $*"
}

log_warn() {
  echo "[WARN] $*" >&2
}

log_error() {
  echo "[ERROR] $*" >&2
}

run() {
  if [[ "${dry_run}" == "true" ]]; then
    echo "[DRY-RUN] $*"
  else
    log_info "Executing: $*"
    eval "$@"
  fi
}

# =============================================================================
# MAIN CLEANUP
# =============================================================================

echo "============================================================================="
echo "ORPHAN CLEANUP STARTING"
echo "============================================================================="
echo "BuildId: ${build_id}"
echo "Region: ${region}"
echo "Dry Run: ${dry_run}"
echo "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
if [[ -n "${state_bucket}" || -n "${state_table}" ]]; then
  echo "State context (bucket=${state_bucket:-unset}, table=${state_table:-unset})"
fi
echo "Safety: state backend resources (S3 bucket, DynamoDB lock table) are never modified."
echo "============================================================================="

# =============================================================================
# EKS CLUSTERS AND NODEGROUPS
# =============================================================================

log_step "EKS_CLEANUP" "Finding EKS clusters with BuildId=${build_id}..."

eks_clusters=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "eks:cluster" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)

for arn in ${eks_clusters}; do
  cluster_name="${arn##*/}"
  log_step "EKS_CLUSTER" "Processing cluster: ${cluster_name}"

  # Delete nodegroups first
  nodegroups=$(aws eks list-nodegroups --cluster-name "${cluster_name}" --region "${region}" --query "nodegroups[]" --output text 2>/dev/null || true)

  if [[ -n "${nodegroups}" ]]; then
    for ng in ${nodegroups}; do
      log_step "DELETE_NODEGROUP" "Deleting nodegroup: ${ng}"
      run aws eks delete-nodegroup --cluster-name "${cluster_name}" --nodegroup-name "${ng}" --region "${region}"
    done

    # Wait for all nodegroups to be deleted before proceeding
    if [[ "${dry_run}" != "true" ]]; then
      log_step "WAIT_NODEGROUPS" "Waiting for nodegroups to be deleted (timeout: ${nodegroup_wait_timeout}s)..."
      start_epoch=$(date -u +%s)

      while true; do
        remaining_ngs=$(aws eks list-nodegroups --cluster-name "${cluster_name}" --region "${region}" --query "nodegroups[]" --output text 2>/dev/null || true)

        if [[ -z "${remaining_ngs}" ]]; then
          log_info "All nodegroups deleted for cluster ${cluster_name}."
          break
        fi

        now_epoch=$(date -u +%s)
        elapsed=$((now_epoch - start_epoch))

        if [[ "${elapsed}" -ge "${nodegroup_wait_timeout}" ]]; then
          log_error "Timed out waiting for nodegroups after ${elapsed}s. Remaining: ${remaining_ngs}"
          break
        fi

        log_info "  Nodegroups still deleting (${elapsed}s/${nodegroup_wait_timeout}s): ${remaining_ngs}"
        sleep 30
      done
    fi
  else
    log_info "No nodegroups found for cluster ${cluster_name}."
  fi

  # Now delete the cluster
  log_step "DELETE_CLUSTER" "Deleting EKS cluster: ${cluster_name}"
  run aws eks delete-cluster --name "${cluster_name}" --region "${region}"
done

# =============================================================================
# RDS INSTANCES
# =============================================================================

log_step "RDS_CLEANUP" "Finding RDS instances with BuildId=${build_id}..."

rds_arns=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "rds:db" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)

for arn in ${rds_arns}; do
  db_identifier="${arn##*:db:}"
  log_step "DELETE_RDS" "Deleting RDS instance: ${db_identifier}"

  delete_args="--db-instance-identifier ${db_identifier} --region ${region}"

  if [[ "${rds_skip_final_snapshot}" == "true" ]]; then
    delete_args="${delete_args} --skip-final-snapshot"
    log_info "  Skipping final snapshot"
  else
    snapshot_id="${db_identifier}-final-$(date +%Y%m%d%H%M%S)"
    delete_args="${delete_args} --final-db-snapshot-identifier ${snapshot_id}"
    log_info "  Creating final snapshot: ${snapshot_id}"
  fi

  if [[ "${rds_delete_automated_backups}" == "true" ]]; then
    delete_args="${delete_args} --delete-automated-backups"
    log_info "  Deleting automated backups"
  fi

  run "aws rds delete-db-instance ${delete_args}"
done

# RDS Subnet Groups
log_step "RDS_SUBNET_GROUPS" "Finding RDS subnet groups with BuildId pattern..."
rds_subnet_groups=$(aws rds describe-db-subnet-groups \
  --region "${region}" \
  --query "DBSubnetGroups[?contains(DBSubnetGroupName, '${build_id}')].DBSubnetGroupName" \
  --output text 2>/dev/null || true)

for sg in ${rds_subnet_groups}; do
  log_step "DELETE_RDS_SUBNET_GROUP" "Deleting RDS subnet group: ${sg}"
  run aws rds delete-db-subnet-group --db-subnet-group-name "${sg}" --region "${region}"
done

# RDS Parameter Groups
log_step "RDS_PARAM_GROUPS" "Finding RDS parameter groups with BuildId pattern..."
rds_param_groups=$(aws rds describe-db-parameter-groups \
  --region "${region}" \
  --query "DBParameterGroups[?contains(DBParameterGroupName, '${build_id}')].DBParameterGroupName" \
  --output text 2>/dev/null || true)

for pg in ${rds_param_groups}; do
  log_step "DELETE_RDS_PARAM_GROUP" "Deleting RDS parameter group: ${pg}"
  run aws rds delete-db-parameter-group --db-parameter-group-name "${pg}" --region "${region}"
done

# =============================================================================
# LOAD BALANCERS AND TARGET GROUPS
# =============================================================================

log_step "LB_CLEANUP" "Finding load balancers with BuildId=${build_id}..."

lb_arns=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "elasticloadbalancing:loadbalancer" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)

for arn in ${lb_arns}; do
  if [[ "${arn}" == *"/app/"* || "${arn}" == *"/net/"* || "${arn}" == *"/gateway/"* ]]; then
    lb_name=$(aws elbv2 describe-load-balancers \
      --load-balancer-arns "${arn}" \
      --region "${region}" \
      --query "LoadBalancers[0].LoadBalancerName" \
      --output text 2>/dev/null || echo "${arn}")
    log_step "DELETE_LB_V2" "Deleting load balancer: ${lb_name}"
    run aws elbv2 delete-load-balancer --load-balancer-arn "${arn}" --region "${region}"
  else
    lb_name="${arn##*/}"
    log_step "DELETE_LB_CLASSIC" "Deleting classic load balancer: ${lb_name}"
    run aws elb delete-load-balancer --load-balancer-name "${lb_name}" --region "${region}"
  fi
done

# Target Groups
log_step "TG_CLEANUP" "Finding target groups with BuildId=${build_id}..."

tg_arns=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "elasticloadbalancing:targetgroup" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)

for arn in ${tg_arns}; do
  tg_name=$(aws elbv2 describe-target-groups \
    --target-group-arns "${arn}" \
    --region "${region}" \
    --query "TargetGroups[0].TargetGroupName" \
    --output text 2>/dev/null || echo "${arn}")
  log_step "DELETE_TARGET_GROUP" "Deleting target group: ${tg_name}"
  run aws elbv2 delete-target-group --target-group-arn "${arn}" --region "${region}"
done

# =============================================================================
# EC2 INSTANCES
# =============================================================================

log_step "EC2_CLEANUP" "Finding EC2 instances with BuildId=${build_id}..."

instances=$(aws ec2 describe-instances \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Reservations[].Instances[].InstanceId" --output text 2>/dev/null || true)

if [[ -n "${instances}" ]]; then
  for instance in ${instances}; do
    log_step "TERMINATE_EC2" "Terminating EC2 instance: ${instance}"
  done
  run aws ec2 terminate-instances --instance-ids ${instances} --region "${region}"
else
  log_info "No EC2 instances found."
fi

# =============================================================================
# NAT GATEWAYS (must be deleted BEFORE ENIs - NAT gateways hold ENIs)
# =============================================================================

log_step "NAT_CLEANUP" "Finding NAT gateways with BuildId=${build_id}..."

# Strategy 1: Search by BuildId tag (include all non-deleted states)
nat_gws=$(aws ec2 describe-nat-gateways \
  --filter "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "NatGateways[?State!='deleted'].NatGatewayId" --output text 2>/dev/null || true)

# Strategy 2: Search by name pattern if no results from tag search
# This handles cases where resources have the BuildId in name but tag search fails
if [[ -z "${nat_gws}" ]]; then
  log_info "No NAT gateways found by tag, searching by name pattern *${build_id}*..."
  nat_gws=$(aws ec2 describe-nat-gateways \
    --region "${region}" \
    --query "NatGateways[?State!='deleted' && contains(Tags[?Key=='Name'].Value | [0], '${build_id}')].NatGatewayId" \
    --output text 2>/dev/null || true)
fi

nat_deleted=0
nat_waiting=0
for nat in ${nat_gws}; do
  # Check current state
  nat_state=$(aws ec2 describe-nat-gateways \
    --nat-gateway-ids "${nat}" \
    --region "${region}" \
    --query "NatGateways[0].State" --output text 2>/dev/null || echo "unknown")

  if [[ "${nat_state}" == "deleting" ]]; then
    log_info "NAT gateway ${nat} already deleting, will wait for it."
    nat_waiting=$((nat_waiting + 1))
  elif [[ "${nat_state}" == "available" || "${nat_state}" == "pending" || "${nat_state}" == "failed" ]]; then
    log_step "DELETE_NAT_GW" "Deleting NAT gateway: ${nat} (state: ${nat_state})"
    run aws ec2 delete-nat-gateway --nat-gateway-id "${nat}" --region "${region}"
    nat_deleted=$((nat_deleted + 1))
  else
    log_info "NAT gateway ${nat} in state ${nat_state}, skipping."
  fi
done

# Wait for NAT gateway deletion to complete (releases ENIs)
if [[ "${nat_deleted}" -gt 0 || "${nat_waiting}" -gt 0 ]]; then
  log_step "WAIT_NAT_GW" "Waiting for NAT gateway deletion to release ENIs..."

  # Wait up to 90 seconds for NAT gateways to be deleted
  nat_wait_timeout=90
  nat_wait_start=$(date +%s)

  while true; do
    all_deleted=true
    for nat in ${nat_gws}; do
      nat_state=$(aws ec2 describe-nat-gateways \
        --nat-gateway-ids "${nat}" \
        --region "${region}" \
        --query "NatGateways[0].State" --output text 2>/dev/null || echo "deleted")

      if [[ "${nat_state}" != "deleted" ]]; then
        all_deleted=false
        log_info "  NAT gateway ${nat}: ${nat_state}"
      fi
    done

    if [[ "${all_deleted}" == "true" ]]; then
      log_info "All NAT gateways deleted."
      break
    fi

    elapsed=$(($(date +%s) - nat_wait_start))
    if [[ "${elapsed}" -ge "${nat_wait_timeout}" ]]; then
      log_warn "Timed out waiting for NAT gateway deletion after ${elapsed}s. Continuing..."
      break
    fi

    log_info "[WAIT] NAT gateways still deleting (${elapsed}s/${nat_wait_timeout}s)..."
    sleep 15
  done
else
  log_info "No NAT gateways found, skipping wait."
fi

# =============================================================================
# ELASTIC NETWORK INTERFACES (unattached only)
# =============================================================================

log_step "ENI_CLEANUP" "Finding unattached ENIs with BuildId=${build_id}..."

enis=$(aws ec2 describe-network-interfaces \
  --filters "Name=tag:BuildId,Values=${build_id}" "Name=status,Values=available" \
  --region "${region}" \
  --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)

for eni in ${enis}; do
  log_step "DELETE_ENI" "Deleting ENI: ${eni}"
  run aws ec2 delete-network-interface --network-interface-id "${eni}" --region "${region}"
done

# =============================================================================
# IAM ROLES AND INSTANCE PROFILES
# =============================================================================

log_step "IAM_CLEANUP" "Finding IAM roles with BuildId=${build_id}..."

iam_roles=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "iam:role" \
  --region "${iam_region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)

for arn in ${iam_roles}; do
  role_name="${arn##*/}"
  log_step "DELETE_IAM_ROLE" "Processing IAM role: ${role_name}"

  # Detach managed policies
  attached_policies=$(aws iam list-attached-role-policies \
    --role-name "${role_name}" \
    --query "AttachedPolicies[].PolicyArn" --output text 2>/dev/null || true)
  for policy in ${attached_policies}; do
    log_info "  Detaching managed policy: ${policy##*/}"
    run aws iam detach-role-policy --role-name "${role_name}" --policy-arn "${policy}"
  done

  # Delete inline policies
  inline_policies=$(aws iam list-role-policies \
    --role-name "${role_name}" \
    --query "PolicyNames[]" --output text 2>/dev/null || true)
  for policy in ${inline_policies}; do
    log_info "  Deleting inline policy: ${policy}"
    run aws iam delete-role-policy --role-name "${role_name}" --policy-name "${policy}"
  done

  # Remove from instance profiles
  profiles=$(aws iam list-instance-profiles-for-role \
    --role-name "${role_name}" \
    --query "InstanceProfiles[].InstanceProfileName" --output text 2>/dev/null || true)
  for profile in ${profiles}; do
    log_info "  Removing from instance profile: ${profile}"
    run aws iam remove-role-from-instance-profile --instance-profile-name "${profile}" --role-name "${role_name}"

    tagged=$(aws iam list-instance-profile-tags \
      --instance-profile-name "${profile}" \
      --query "Tags[?Key=='BuildId' && Value=='${build_id}']" --output text 2>/dev/null || true)
    if [[ -n "${tagged}" ]]; then
      log_info "  Deleting instance profile: ${profile}"
      run aws iam delete-instance-profile --instance-profile-name "${profile}"
    fi
  done

  log_info "  Deleting IAM role: ${role_name}"
  run aws iam delete-role --role-name "${role_name}"
done

# =============================================================================
# ELASTIC IPS
# =============================================================================

log_step "EIP_CLEANUP" "Finding Elastic IPs with BuildId=${build_id}..."

eips=$(aws ec2 describe-addresses \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Addresses[].AllocationId" --output text 2>/dev/null || true)

for eip in ${eips}; do
  log_step "RELEASE_EIP" "Releasing Elastic IP: ${eip}"
  run aws ec2 release-address --allocation-id "${eip}" --region "${region}"
done

# =============================================================================
# ROUTE TABLES
# =============================================================================

log_step "RT_CLEANUP" "Finding route tables with BuildId=${build_id}..."

rt_ids=$(aws ec2 describe-route-tables \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "RouteTables[].{Id:RouteTableId,Main:Associations[?Main==\`true\`]|[0].Main}" \
  --output text 2>/dev/null || true)

if [[ -n "${rt_ids}" ]]; then
  while read -r rtb main; do
    [[ -z "${rtb}" ]] && continue
    if [[ "${main}" != "True" ]]; then
      log_step "DELETE_ROUTE_TABLE" "Deleting route table: ${rtb}"

      assoc_ids=$(aws ec2 describe-route-tables \
        --route-table-ids "${rtb}" \
        --region "${region}" \
        --query "RouteTables[].Associations[?Main!=\`true\`].RouteTableAssociationId" --output text 2>/dev/null || true)

      for assoc_id in ${assoc_ids}; do
        log_info "  Disassociating: ${assoc_id}"
        run aws ec2 disassociate-route-table --association-id "${assoc_id}" --region "${region}"
      done

      run aws ec2 delete-route-table --route-table-id "${rtb}" --region "${region}"
    else
      log_info "Skipping main route table: ${rtb}"
    fi
  done <<< "${rt_ids}"
fi

# =============================================================================
# SUBNETS
# =============================================================================

log_step "SUBNET_CLEANUP" "Finding subnets with BuildId=${build_id}..."

subnets=$(aws ec2 describe-subnets \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Subnets[].SubnetId" --output text 2>/dev/null || true)

# Fallback: search by name pattern
if [[ -z "${subnets}" ]]; then
  log_info "No subnets found by tag, searching by name pattern *${build_id}*..."
  subnets=$(aws ec2 describe-subnets \
    --region "${region}" \
    --query "Subnets[?contains(Tags[?Key=='Name'].Value | [0], '${build_id}')].SubnetId" \
    --output text 2>/dev/null || true)
fi

for subnet in ${subnets}; do
  log_step "DELETE_SUBNET" "Deleting subnet: ${subnet}"
  run aws ec2 delete-subnet --subnet-id "${subnet}" --region "${region}"
done

# =============================================================================
# SECURITY GROUPS
# =============================================================================

log_step "SG_CLEANUP" "Finding security groups with BuildId=${build_id}..."

sgs=$(aws ec2 describe-security-groups \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "SecurityGroups[?GroupName!=\`default\`].GroupId" --output text 2>/dev/null || true)

for sg in ${sgs}; do
  log_step "DELETE_SG" "Deleting security group: ${sg}"
  run aws ec2 delete-security-group --group-id "${sg}" --region "${region}"
done

# =============================================================================
# INTERNET GATEWAYS
# =============================================================================

log_step "IGW_CLEANUP" "Finding internet gateways with BuildId=${build_id}..."

igws=$(aws ec2 describe-internet-gateways \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "InternetGateways[].InternetGatewayId" --output text 2>/dev/null || true)

# Fallback: search by name pattern
if [[ -z "${igws}" ]]; then
  log_info "No IGWs found by tag, searching by name pattern *${build_id}*..."
  igws=$(aws ec2 describe-internet-gateways \
    --region "${region}" \
    --query "InternetGateways[?contains(Tags[?Key=='Name'].Value | [0], '${build_id}')].InternetGatewayId" \
    --output text 2>/dev/null || true)
fi

for igw in ${igws}; do
  log_step "DELETE_IGW" "Processing internet gateway: ${igw}"

  vpcs=$(aws ec2 describe-internet-gateways \
    --internet-gateway-ids "${igw}" \
    --region "${region}" \
    --query "InternetGateways[].Attachments[].VpcId" --output text 2>/dev/null || true)

  for vpc in ${vpcs}; do
    log_info "  Detaching from VPC: ${vpc}"
    run aws ec2 detach-internet-gateway --internet-gateway-id "${igw}" --vpc-id "${vpc}" --region "${region}"
  done

  log_info "  Deleting IGW: ${igw}"
  run aws ec2 delete-internet-gateway --internet-gateway-id "${igw}" --region "${region}"
done

# =============================================================================
# VPCS
# =============================================================================

log_step "VPC_CLEANUP" "Finding VPCs with BuildId=${build_id}..."

vpcs=$(aws ec2 describe-vpcs \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Vpcs[].VpcId" --output text 2>/dev/null || true)

# Fallback: search by name pattern
if [[ -z "${vpcs}" ]]; then
  log_info "No VPCs found by tag, searching by name pattern *${build_id}*..."
  vpcs=$(aws ec2 describe-vpcs \
    --region "${region}" \
    --query "Vpcs[?contains(Tags[?Key=='Name'].Value | [0], '${build_id}')].VpcId" \
    --output text 2>/dev/null || true)
fi

for vpc in ${vpcs}; do
  log_step "DELETE_VPC" "Deleting VPC: ${vpc}"

  # Try to delete the VPC
  if [[ "${dry_run}" == "true" ]]; then
    echo "[DRY-RUN] aws ec2 delete-vpc --vpc-id ${vpc} --region ${region}"
  elif ! aws ec2 delete-vpc --vpc-id "${vpc}" --region "${region}" 2>&1; then
    log_warn "VPC deletion failed, checking for remaining dependencies..."

    # Check for remaining NAT gateways
    remaining_nats=$(aws ec2 describe-nat-gateways \
      --filter "Name=vpc-id,Values=${vpc}" \
      --region "${region}" \
      --query "NatGateways[?State!='deleted'].[NatGatewayId,State]" --output text 2>/dev/null || true)
    if [[ -n "${remaining_nats}" ]]; then
      log_warn "  Remaining NAT gateways in VPC:"
      echo "${remaining_nats}" | while read -r nat_id nat_state; do
        log_warn "    - ${nat_id}: ${nat_state}"
      done
    fi

    # Check for remaining subnets
    remaining_subnets=$(aws ec2 describe-subnets \
      --filters "Name=vpc-id,Values=${vpc}" \
      --region "${region}" \
      --query "Subnets[].SubnetId" --output text 2>/dev/null || true)
    if [[ -n "${remaining_subnets}" ]]; then
      log_warn "  Remaining subnets in VPC: ${remaining_subnets}"
    fi

    # Check for remaining ENIs
    remaining_enis=$(aws ec2 describe-network-interfaces \
      --filters "Name=vpc-id,Values=${vpc}" \
      --region "${region}" \
      --query "NetworkInterfaces[].[NetworkInterfaceId,Status,Description]" --output text 2>/dev/null || true)
    if [[ -n "${remaining_enis}" ]]; then
      log_warn "  Remaining ENIs in VPC:"
      echo "${remaining_enis}" | while read -r eni_id eni_status eni_desc; do
        log_warn "    - ${eni_id}: ${eni_status} (${eni_desc})"
      done
    fi

    # Check for remaining security groups (non-default)
    remaining_sgs=$(aws ec2 describe-security-groups \
      --filters "Name=vpc-id,Values=${vpc}" \
      --region "${region}" \
      --query "SecurityGroups[?GroupName!='default'].GroupId" --output text 2>/dev/null || true)
    if [[ -n "${remaining_sgs}" ]]; then
      log_warn "  Remaining security groups in VPC: ${remaining_sgs}"
    fi

    # Check for remaining internet gateways
    remaining_igws=$(aws ec2 describe-internet-gateways \
      --filters "Name=attachment.vpc-id,Values=${vpc}" \
      --region "${region}" \
      --query "InternetGateways[].InternetGatewayId" --output text 2>/dev/null || true)
    if [[ -n "${remaining_igws}" ]]; then
      log_warn "  Remaining internet gateways attached to VPC: ${remaining_igws}"
    fi
  fi
done

# =============================================================================
# CLEANUP COMPLETE
# =============================================================================

echo ""
echo "============================================================================="
echo "ORPHAN CLEANUP COMPLETED"
echo "============================================================================="
echo "BuildId: ${build_id}"
echo "Region: ${region}"
echo "Dry Run: ${dry_run}"
echo "Completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "============================================================================="
