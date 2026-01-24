#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# ORPHAN CLEANUP (PERSISTENT) - Clean up orphaned AWS resources by cluster name
# =============================================================================
#
# Version: 1.0.0
# Purpose: Clean up AWS resources left behind by failed persistent cluster teardowns
#
# Key difference from cleanup-orphans.sh:
#   - Uses cluster name pattern matching instead of BuildId tags
#   - Searches by Lifecycle=persistent, kubernetes.io/cluster/<name>, and name patterns
#   - Designed for persistent clusters that don't have BuildId tags
#
# Usage:
#   bootstrap/60_tear_down_clean_up/cleanup-orphans-persistent.sh <cluster-name> <region>
#
# Examples:
#   DRY_RUN=true ./cleanup-orphans-persistent.sh goldenpath-dev-eks eu-west-2
#   DRY_RUN=false ./cleanup-orphans-persistent.sh goldenpath-dev-eks eu-west-2
#
# Environment variables:
#   DRY_RUN=true|false (default true) - Set to false to perform actual deletions
#   ENVIRONMENT=<env> - Environment name for pattern matching (default: derived from cluster)
#   NAME_PREFIX=<prefix> - Resource name prefix (default: goldenpath)
#   IAM_REGION=<region> - Region for IAM operations (default: us-east-1)
#   NODEGROUP_WAIT_TIMEOUT=<seconds> - Max wait for nodegroup deletion (default: 600)
#   DELETE_VPC=true|false (default: false) - Delete VPC (dangerous for persistent!)
#   DELETE_RDS=true|false (default: false) - Delete RDS instances
#   RDS_SKIP_FINAL_SNAPSHOT=true|false (default: false) - Skip RDS final snapshot
#   CLEAN_TF_STATE=true|false (default: false) - Also remove deleted resources from Terraform state
#   TF_DIR=<path> - Terraform directory (default: envs/<env>)
#
# Resources cleaned up:
#   - EKS clusters and nodegroups (with proper wait)
#   - Load balancers (ALB/NLB/CLB) by cluster tag
#   - Target groups
#   - EC2 instances (with cluster tag)
#   - ENIs (unattached only, in cluster subnets)
#   - IAM roles (cluster name pattern + goldenpath-idp-* with Environment tag)
#   - IAM policies (goldenpath-idp-* with Environment tag)
#   - NAT gateways (OPTIONAL - only if DELETE_VPC=true)
#   - Elastic IPs (OPTIONAL - only if DELETE_VPC=true)
#   - Subnets (OPTIONAL - only if DELETE_VPC=true)
#   - Security groups (cluster-tagged only)
#   - Internet gateways (OPTIONAL - only if DELETE_VPC=true)
#   - VPCs (OPTIONAL - only if DELETE_VPC=true)
#
# Safety notes:
#   - VPC, subnets, NAT gateways NOT deleted by default (persistent infra)
#   - RDS NOT deleted by default
#   - Always runs in DRY_RUN=true mode unless explicitly overridden
#
# =============================================================================

cluster_name="${1:-}"
region="${2:-}"
dry_run="${DRY_RUN:-true}"
name_prefix="${NAME_PREFIX:-goldenpath}"
iam_region="${IAM_REGION:-us-east-1}"
nodegroup_wait_timeout="${NODEGROUP_WAIT_TIMEOUT:-600}"
delete_vpc="${DELETE_VPC:-false}"
delete_rds="${DELETE_RDS:-false}"
rds_skip_final_snapshot="${RDS_SKIP_FINAL_SNAPSHOT:-false}"
clean_tf_state="${CLEAN_TF_STATE:-false}"
tf_dir="${TF_DIR:-}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster-name> <region>" >&2
  echo "Example: DRY_RUN=true $0 goldenpath-dev-eks eu-west-2" >&2
  echo "" >&2
  echo "Set DRY_RUN=false to perform deletions." >&2
  echo "Set DELETE_VPC=true to also delete VPC resources (dangerous!)." >&2
  echo "Set DELETE_RDS=true to also delete RDS instances (requires confirmation)." >&2
  echo "Set CLEAN_TF_STATE=true to also remove resources from Terraform state." >&2
  exit 1
fi

# Derive environment from cluster name (e.g., goldenpath-dev-eks -> dev)
if [[ -z "${ENVIRONMENT:-}" ]]; then
  # Extract middle segment from goldenpath-<env>-eks pattern
  environment=$(echo "${cluster_name}" | sed -n 's/^'"${name_prefix}"'-\([^-]*\)-.*/\1/p')
  if [[ -z "${environment}" ]]; then
    environment="unknown"
  fi
else
  environment="${ENVIRONMENT}"
fi

# Derive TF_DIR if not set
if [[ -z "${tf_dir}" ]]; then
  tf_dir="envs/${environment}"
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

# Retry a command with exponential backoff
# Usage: run_with_retry <max_attempts> <initial_delay> <command...>
# Returns 0 on success, 1 on failure after all retries
run_with_retry() {
  local max_attempts="$1"
  local delay="$2"
  shift 2
  local cmd="$*"
  local attempt=1

  if [[ "${dry_run}" == "true" ]]; then
    echo "[DRY-RUN] $cmd"
    return 0
  fi

  while [[ $attempt -le $max_attempts ]]; do
    log_info "Attempt $attempt/$max_attempts: $cmd"
    if eval "$cmd" 2>&1; then
      return 0
    else
      local exit_code=$?
      if [[ $attempt -lt $max_attempts ]]; then
        log_warn "Attempt $attempt failed (exit $exit_code). Retrying in ${delay}s..."
        sleep "$delay"
        delay=$((delay * 2))  # Exponential backoff
      else
        log_error "All $max_attempts attempts failed for: $cmd"
        return 1
      fi
    fi
    attempt=$((attempt + 1))
  done
}

# =============================================================================
# RESOURCE DISCOVERY HELPERS
# =============================================================================

# Find resources by kubernetes.io/cluster/<cluster-name> tag
find_by_cluster_tag() {
  local resource_type="$1"
  aws resourcegroupstaggingapi get-resources \
    --tag-filters "Key=kubernetes.io/cluster/${cluster_name},Values=owned,shared" \
    --resource-type-filters "${resource_type}" \
    --region "${region}" \
    --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true
}

# Find resources by Lifecycle=persistent + Environment tag
find_by_lifecycle_tag() {
  local resource_type="$1"
  aws resourcegroupstaggingapi get-resources \
    --tag-filters "Key=Lifecycle,Values=persistent" "Key=Environment,Values=${environment}" \
    --resource-type-filters "${resource_type}" \
    --region "${region}" \
    --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true
}

# Find LBs by elbv2.k8s.aws/cluster tag
find_lbs_by_cluster_tag() {
  local all_lbs
  all_lbs=$(aws elbv2 describe-load-balancers \
    --region "${region}" \
    --query "LoadBalancers[].LoadBalancerArn" --output text 2>/dev/null || true)

  for arn in ${all_lbs}; do
    local cluster_tag
    cluster_tag=$(aws elbv2 describe-tags \
      --resource-arns "${arn}" \
      --region "${region}" \
      --query "TagDescriptions[0].Tags[?Key=='elbv2.k8s.aws/cluster'].Value | [0]" \
      --output text 2>/dev/null || true)

    if [[ "${cluster_tag}" == "${cluster_name}" ]]; then
      echo "${arn}"
    fi
  done
}

# Find Classic ELBs by kubernetes.io/cluster tag
find_classic_elbs_by_cluster_tag() {
  local all_elbs
  all_elbs=$(aws elb describe-load-balancers \
    --region "${region}" \
    --query "LoadBalancerDescriptions[].LoadBalancerName" --output text 2>/dev/null || true)

  for elb_name in ${all_elbs}; do
    local cluster_tag
    cluster_tag=$(aws elb describe-tags \
      --load-balancer-names "${elb_name}" \
      --region "${region}" \
      --query "TagDescriptions[0].Tags[?Key=='kubernetes.io/cluster/${cluster_name}'].Value | [0]" \
      --output text 2>/dev/null || true)

    if [[ -n "${cluster_tag}" && "${cluster_tag}" != "None" ]]; then
      echo "${elb_name}"
    fi
  done
}

# =============================================================================
# MAIN CLEANUP
# =============================================================================

echo "============================================================================="
echo "PERSISTENT ORPHAN CLEANUP STARTING"
echo "============================================================================="
echo "Cluster Name: ${cluster_name}"
echo "Environment: ${environment}"
echo "Region: ${region}"
echo "Name Prefix: ${name_prefix}"
echo "Dry Run: ${dry_run}"
echo "Delete VPC: ${delete_vpc}"
echo "Delete RDS: ${delete_rds}"
echo "Clean TF State: ${clean_tf_state}"
echo "TF Dir: ${tf_dir}"
echo "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""
echo "Discovery methods:"
echo "  1. kubernetes.io/cluster/${cluster_name} tag"
echo "  2. elbv2.k8s.aws/cluster=${cluster_name} tag (for LBs)"
echo "  3. Lifecycle=persistent + Environment=${environment} tags"
echo "  4. Name pattern: *${cluster_name}* or *${name_prefix}-${environment}*"
echo "  5. IAM pattern: ${name_prefix}-idp-* with Environment=${environment} tag"
echo "============================================================================="

if [[ "${dry_run}" == "true" ]]; then
  echo ""
  echo "*** DRY RUN MODE - No resources will be deleted ***"
  echo ""
fi

# =============================================================================
# EKS CLUSTERS AND NODEGROUPS
# =============================================================================

log_step "EKS_CLEANUP" "Checking EKS cluster: ${cluster_name}..."

# Check if cluster exists
cluster_status=$(aws eks describe-cluster \
  --name "${cluster_name}" \
  --region "${region}" \
  --query "cluster.status" --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "${cluster_status}" == "NOT_FOUND" ]]; then
  log_info "Cluster ${cluster_name} does not exist, skipping EKS cleanup."
else
  log_info "Cluster ${cluster_name} exists (status: ${cluster_status})"

  # Delete nodegroups first
  nodegroups=$(aws eks list-nodegroups \
    --cluster-name "${cluster_name}" \
    --region "${region}" \
    --query "nodegroups[]" --output text 2>/dev/null || true)

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
        remaining_ngs=$(aws eks list-nodegroups \
          --cluster-name "${cluster_name}" \
          --region "${region}" \
          --query "nodegroups[]" --output text 2>/dev/null || true)

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

  # Delete Fargate profiles
  fargate_profiles=$(aws eks list-fargate-profiles \
    --cluster-name "${cluster_name}" \
    --region "${region}" \
    --query "fargateProfileNames[]" --output text 2>/dev/null || true)

  for fp in ${fargate_profiles}; do
    log_step "DELETE_FARGATE" "Deleting Fargate profile: ${fp}"
    run aws eks delete-fargate-profile \
      --cluster-name "${cluster_name}" \
      --fargate-profile-name "${fp}" \
      --region "${region}"
  done

  # Now delete the cluster
  log_step "DELETE_CLUSTER" "Deleting EKS cluster: ${cluster_name}"
  run aws eks delete-cluster --name "${cluster_name}" --region "${region}"

  if [[ "${dry_run}" != "true" ]]; then
    log_step "WAIT_CLUSTER" "Waiting for cluster deletion..."
    aws eks wait cluster-deleted --name "${cluster_name}" --region "${region}" 2>/dev/null || \
      log_warn "Cluster deletion wait timed out or cluster already deleted."
  fi
fi

# =============================================================================
# RDS INSTANCES (Optional - must be explicitly enabled)
# =============================================================================

if [[ "${delete_rds}" == "true" ]]; then
  log_step "RDS_CLEANUP" "Finding RDS instances for ${environment}..."

  # Find by cluster tag
  rds_arns=$(find_by_cluster_tag "rds:db")

  # Also find by lifecycle tag
  lifecycle_rds=$(find_by_lifecycle_tag "rds:db")
  rds_arns="${rds_arns} ${lifecycle_rds}"

  for arn in ${rds_arns}; do
    [[ -z "${arn}" ]] && continue
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

    run "aws rds delete-db-instance ${delete_args}"
  done
else
  log_info "Skipping RDS cleanup (DELETE_RDS=false). Set DELETE_RDS=true to include."
fi

# =============================================================================
# LOAD BALANCERS (by cluster tag)
# =============================================================================

log_step "LB_CLEANUP" "Finding load balancers for cluster ${cluster_name}..."

# Find ALB/NLB by elbv2.k8s.aws/cluster tag
lb_arns=$(find_lbs_by_cluster_tag)

for arn in ${lb_arns}; do
  [[ -z "${arn}" ]] && continue
  lb_name=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns "${arn}" \
    --region "${region}" \
    --query "LoadBalancers[0].LoadBalancerName" \
    --output text 2>/dev/null || echo "${arn}")
  log_step "DELETE_LB_V2" "Deleting load balancer: ${lb_name}"
  run aws elbv2 delete-load-balancer --load-balancer-arn "${arn}" --region "${region}"
done

# Find Classic ELBs
classic_elbs=$(find_classic_elbs_by_cluster_tag)

for elb_name in ${classic_elbs}; do
  [[ -z "${elb_name}" ]] && continue
  log_step "DELETE_LB_CLASSIC" "Deleting classic load balancer: ${elb_name}"
  run aws elb delete-load-balancer --load-balancer-name "${elb_name}" --region "${region}"
done

# =============================================================================
# TARGET GROUPS
# =============================================================================

log_step "TG_CLEANUP" "Finding target groups for cluster ${cluster_name}..."

# Search by cluster tag
tg_arns=$(find_by_cluster_tag "elasticloadbalancing:targetgroup")

# Also search by name pattern (k8s-<cluster>-*)
all_tgs=$(aws elbv2 describe-target-groups \
  --region "${region}" \
  --query "TargetGroups[?contains(TargetGroupName, 'k8s-')].TargetGroupArn" \
  --output text 2>/dev/null || true)

for arn in ${tg_arns} ${all_tgs}; do
  [[ -z "${arn}" ]] && continue

  # Verify this TG belongs to our cluster by checking tags
  tg_cluster_tag=$(aws elbv2 describe-tags \
    --resource-arns "${arn}" \
    --region "${region}" \
    --query "TagDescriptions[0].Tags[?Key=='elbv2.k8s.aws/cluster'].Value | [0]" \
    --output text 2>/dev/null || true)

  if [[ "${tg_cluster_tag}" == "${cluster_name}" ]] || \
     [[ "${arn}" == *"${cluster_name}"* ]]; then
    tg_name=$(aws elbv2 describe-target-groups \
      --target-group-arns "${arn}" \
      --region "${region}" \
      --query "TargetGroups[0].TargetGroupName" \
      --output text 2>/dev/null || echo "${arn}")
    log_step "DELETE_TARGET_GROUP" "Deleting target group: ${tg_name}"
    run aws elbv2 delete-target-group --target-group-arn "${arn}" --region "${region}"
  fi
done

# =============================================================================
# EC2 INSTANCES (with cluster tag or name pattern)
# =============================================================================

log_step "EC2_CLEANUP" "Finding EC2 instances for cluster ${cluster_name}..."

# Strategy 1: Find by kubernetes.io/cluster tag
instances=$(aws ec2 describe-instances \
  --filters "Name=tag:kubernetes.io/cluster/${cluster_name},Values=owned,shared" \
  --region "${region}" \
  --query "Reservations[].Instances[?State.Name!='terminated'].InstanceId" \
  --output text 2>/dev/null || true)

# Strategy 2: Find by Name tag pattern (e.g., goldenpath-dev-app, goldenpath-dev-bastion)
name_pattern_instances=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=${name_prefix}-${environment}-*" \
  --region "${region}" \
  --query "Reservations[].Instances[?State.Name!='terminated'].InstanceId" \
  --output text 2>/dev/null || true)

# Strategy 3: Find by Environment + Lifecycle tags
env_instances=$(aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=${environment}" \
            "Name=tag:Lifecycle,Values=persistent" \
  --region "${region}" \
  --query "Reservations[].Instances[?State.Name!='terminated'].InstanceId" \
  --output text 2>/dev/null || true)

# Combine and deduplicate
all_instances="${instances} ${name_pattern_instances} ${env_instances}"
unique_instances=$(echo "${all_instances}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [[ -n "${unique_instances// /}" ]]; then
  for instance in ${unique_instances}; do
    [[ -z "${instance}" ]] && continue
    instance_name=$(aws ec2 describe-instances \
      --instance-ids "${instance}" \
      --region "${region}" \
      --query "Reservations[0].Instances[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${instance}")
    log_step "TERMINATE_EC2" "Terminating EC2 instance: ${instance} (${instance_name})"
  done
  run aws ec2 terminate-instances --instance-ids ${unique_instances} --region "${region}"

  if [[ "${dry_run}" != "true" ]]; then
    log_step "WAIT_EC2" "Waiting for instance termination..."
    aws ec2 wait instance-terminated --instance-ids ${unique_instances} --region "${region}" 2>/dev/null || \
      log_warn "Instance termination wait timed out."
  fi
else
  log_info "No EC2 instances found."
fi

# =============================================================================
# SECURITY GROUPS (cluster-tagged)
# =============================================================================

log_step "SG_CLEANUP" "Finding security groups for cluster ${cluster_name}..."

sgs=$(aws ec2 describe-security-groups \
  --filters "Name=tag:kubernetes.io/cluster/${cluster_name},Values=owned,shared" \
  --region "${region}" \
  --query "SecurityGroups[?GroupName!='default'].GroupId" --output text 2>/dev/null || true)

# Also find by elbv2 cluster tag
elbv2_sgs=$(aws ec2 describe-security-groups \
  --filters "Name=tag:elbv2.k8s.aws/cluster,Values=${cluster_name}" \
  --region "${region}" \
  --query "SecurityGroups[?GroupName!='default'].GroupId" --output text 2>/dev/null || true)

all_sgs="${sgs} ${elbv2_sgs}"
processed_sgs=""

for sg in ${all_sgs}; do
  [[ -z "${sg}" ]] && continue
  # Skip duplicates
  if [[ "${processed_sgs}" == *"${sg}"* ]]; then
    continue
  fi
  processed_sgs="${processed_sgs} ${sg}"

  log_step "DELETE_SG" "Deleting security group: ${sg}"

  # First remove all ingress/egress rules that reference other SGs
  # This prevents "dependency violation" errors
  if [[ "${dry_run}" != "true" ]]; then
    # Get and revoke ingress rules
    aws ec2 describe-security-groups --group-ids "${sg}" --region "${region}" \
      --query "SecurityGroups[0].IpPermissions" --output json 2>/dev/null | \
      jq -c '.[]' 2>/dev/null | while read -r rule; do
        aws ec2 revoke-security-group-ingress \
          --group-id "${sg}" \
          --ip-permissions "${rule}" \
          --region "${region}" 2>/dev/null || true
      done

    # Get and revoke egress rules
    aws ec2 describe-security-groups --group-ids "${sg}" --region "${region}" \
      --query "SecurityGroups[0].IpPermissionsEgress" --output json 2>/dev/null | \
      jq -c '.[]' 2>/dev/null | while read -r rule; do
        aws ec2 revoke-security-group-egress \
          --group-id "${sg}" \
          --ip-permissions "${rule}" \
          --region "${region}" 2>/dev/null || true
      done
  fi

  # Use retry with exponential backoff to handle DependencyViolation from ENIs
  # ENIs from recently deleted load balancers take 10-30s to release
  run_with_retry 5 10 "aws ec2 delete-security-group --group-id ${sg} --region ${region}"
done

# =============================================================================
# IAM ROLES (with cluster name pattern and goldenpath-idp-* pattern)
# =============================================================================

log_step "IAM_CLEANUP" "Finding IAM roles for cluster ${cluster_name}..."

# Find by cluster tag
iam_arns=$(find_by_cluster_tag "iam:role")

# Also find by name pattern (cluster name)
pattern_roles=$(aws iam list-roles \
  --query "Roles[?contains(RoleName, '${cluster_name}')].Arn" \
  --output text 2>/dev/null || true)

# Also find by goldenpath-idp-* pattern (IRSA roles use this naming convention)
# These roles are environment-agnostic but belong to the platform
idp_pattern_roles=$(aws iam list-roles \
  --query "Roles[?starts_with(RoleName, '${name_prefix}-idp-')].Arn" \
  --output text 2>/dev/null || true)

# Filter idp_pattern_roles to only include roles tagged with our environment
filtered_idp_roles=""
for arn in ${idp_pattern_roles}; do
  [[ -z "${arn}" ]] && continue
  role_name="${arn##*/}"
  # Check if role has matching Environment tag
  env_tag=$(aws iam list-role-tags --role-name "${role_name}" \
    --query "Tags[?Key=='Environment'].Value" --output text 2>/dev/null || true)
  if [[ "${env_tag}" == "${environment}" ]]; then
    filtered_idp_roles="${filtered_idp_roles} ${arn}"
    log_info "Found IAM role by idp pattern: ${role_name} (Environment=${env_tag})"
  fi
done

all_iam_roles="${iam_arns} ${pattern_roles} ${filtered_idp_roles}"
processed_roles=""

for arn in ${all_iam_roles}; do
  [[ -z "${arn}" ]] && continue
  role_name="${arn##*/}"

  # Skip duplicates
  if [[ "${processed_roles}" == *"${role_name}"* ]]; then
    continue
  fi
  processed_roles="${processed_roles} ${role_name}"

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
    run aws iam remove-role-from-instance-profile \
      --instance-profile-name "${profile}" \
      --role-name "${role_name}"

    # Delete instance profile if it has the cluster name
    if [[ "${profile}" == *"${cluster_name}"* ]]; then
      log_info "  Deleting instance profile: ${profile}"
      run aws iam delete-instance-profile --instance-profile-name "${profile}"
    fi
  done

  log_info "  Deleting IAM role: ${role_name}"
  run aws iam delete-role --role-name "${role_name}"
done

# =============================================================================
# IAM POLICIES (with goldenpath-idp-* pattern)
# =============================================================================

log_step "IAM_POLICY_CLEANUP" "Finding IAM policies with ${name_prefix}-idp-* pattern..."

# Find policies by name pattern
# Account ID needed for policy ARN construction
account_id=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || true)

if [[ -n "${account_id}" ]]; then
  idp_policies=$(aws iam list-policies --scope Local \
    --query "Policies[?starts_with(PolicyName, '${name_prefix}-idp-')].Arn" \
    --output text 2>/dev/null || true)

  for policy_arn in ${idp_policies}; do
    [[ -z "${policy_arn}" ]] && continue
    policy_name="${policy_arn##*/}"

    # Check if policy has matching Environment tag (if tagged)
    env_tag=$(aws iam list-policy-tags --policy-arn "${policy_arn}" \
      --query "Tags[?Key=='Environment'].Value" --output text 2>/dev/null || true)

    # Only delete if untagged or matches our environment
    if [[ -z "${env_tag}" || "${env_tag}" == "${environment}" ]]; then
      log_step "DELETE_IAM_POLICY" "Deleting IAM policy: ${policy_name}"

      # Delete all non-default versions first
      versions=$(aws iam list-policy-versions --policy-arn "${policy_arn}" \
        --query "Versions[?IsDefaultVersion==\`false\`].VersionId" --output text 2>/dev/null || true)
      for version in ${versions}; do
        log_info "  Deleting policy version: ${version}"
        run aws iam delete-policy-version --policy-arn "${policy_arn}" --version-id "${version}"
      done

      # Delete the policy
      run aws iam delete-policy --policy-arn "${policy_arn}"
    fi
  done
else
  log_warn "Could not determine AWS account ID. Skipping IAM policy cleanup."
fi

# =============================================================================
# ENIs (unattached, in cluster subnets or with cluster/name tags)
# =============================================================================

log_step "ENI_CLEANUP" "Finding unattached ENIs for cluster ${cluster_name}..."

# Strategy 1: Find by kubernetes.io/cluster tag
enis=$(aws ec2 describe-network-interfaces \
  --filters "Name=tag:kubernetes.io/cluster/${cluster_name},Values=owned,shared" \
            "Name=status,Values=available" \
  --region "${region}" \
  --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)

# Strategy 2: Find by elbv2 cluster tag
elbv2_enis=$(aws ec2 describe-network-interfaces \
  --filters "Name=tag:elbv2.k8s.aws/cluster,Values=${cluster_name}" \
            "Name=status,Values=available" \
  --region "${region}" \
  --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)

# Strategy 3: Find by Name tag pattern (e.g., goldenpath-dev-app-eni)
name_pattern_enis=$(aws ec2 describe-network-interfaces \
  --filters "Name=tag:Name,Values=${name_prefix}-${environment}-*" \
            "Name=status,Values=available" \
  --region "${region}" \
  --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)

# Strategy 4: Find by Environment + Lifecycle tags
env_enis=$(aws ec2 describe-network-interfaces \
  --filters "Name=tag:Environment,Values=${environment}" \
            "Name=tag:Lifecycle,Values=persistent" \
            "Name=status,Values=available" \
  --region "${region}" \
  --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)

# Combine and deduplicate
all_enis="${enis} ${elbv2_enis} ${name_pattern_enis} ${env_enis}"
unique_enis=$(echo "${all_enis}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

for eni in ${unique_enis}; do
  [[ -z "${eni}" ]] && continue
  eni_name=$(aws ec2 describe-network-interfaces \
    --network-interface-ids "${eni}" \
    --region "${region}" \
    --query "NetworkInterfaces[0].TagSet[?Key=='Name'].Value | [0]" \
    --output text 2>/dev/null || echo "${eni}")
  log_step "DELETE_ENI" "Deleting ENI: ${eni} (${eni_name})"
  run aws ec2 delete-network-interface --network-interface-id "${eni}" --region "${region}"
done

# =============================================================================
# VPC RESOURCES (Optional - only if DELETE_VPC=true)
# =============================================================================

if [[ "${delete_vpc}" == "true" ]]; then
  echo ""
  log_warn "============================================================================="
  log_warn "VPC DELETION ENABLED - This will delete persistent VPC infrastructure!"
  log_warn "============================================================================="
  echo ""

  # NAT Gateways
  log_step "NAT_CLEANUP" "Finding NAT gateways for ${environment}..."

  # Strategy 1: Find by Environment + Lifecycle tags
  nat_gws=$(aws ec2 describe-nat-gateways \
    --filter "Name=tag:Environment,Values=${environment}" \
             "Name=tag:Lifecycle,Values=persistent" \
    --region "${region}" \
    --query "NatGateways[?State!='deleted'].NatGatewayId" --output text 2>/dev/null || true)

  # Strategy 2: Find by Name tag pattern (e.g., goldenpath-dev-nat)
  name_pattern_nats=$(aws ec2 describe-nat-gateways \
    --region "${region}" \
    --query "NatGateways[?State!='deleted' && contains(Tags[?Key=='Name'].Value | [0], '${name_prefix}-${environment}')].NatGatewayId" \
    --output text 2>/dev/null || true)

  # Combine and deduplicate
  all_nats="${nat_gws} ${name_pattern_nats}"
  unique_nats=$(echo "${all_nats}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

  nat_deleted=0
  for nat in ${unique_nats}; do
    [[ -z "${nat}" ]] && continue
    nat_name=$(aws ec2 describe-nat-gateways \
      --nat-gateway-ids "${nat}" \
      --region "${region}" \
      --query "NatGateways[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${nat}")
    log_step "DELETE_NAT_GW" "Deleting NAT gateway: ${nat} (${nat_name})"
    run aws ec2 delete-nat-gateway --nat-gateway-id "${nat}" --region "${region}"
    nat_deleted=$((nat_deleted + 1))
  done

  # Wait for NAT gateway deletion (they take time to release ENIs)
  if [[ "${nat_deleted}" -gt 0 && "${dry_run}" != "true" ]]; then
    log_step "WAIT_NAT_GW" "Waiting for NAT gateway deletion to release ENIs..."
    nat_wait_timeout=120
    nat_wait_start=$(date +%s)

    while true; do
      all_deleted=true
      for nat in ${unique_nats}; do
        [[ -z "${nat}" ]] && continue
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
  fi

  # Elastic IPs
  log_step "EIP_CLEANUP" "Finding Elastic IPs for ${environment}..."

  # Strategy 1: Find by Environment + Lifecycle tags
  eips=$(aws ec2 describe-addresses \
    --filters "Name=tag:Environment,Values=${environment}" \
              "Name=tag:Lifecycle,Values=persistent" \
    --region "${region}" \
    --query "Addresses[].AllocationId" --output text 2>/dev/null || true)

  # Strategy 2: Find by Name tag pattern (e.g., goldenpath-dev-nat-eip)
  name_pattern_eips=$(aws ec2 describe-addresses \
    --region "${region}" \
    --query "Addresses[?contains(Tags[?Key=='Name'].Value | [0], '${name_prefix}-${environment}')].AllocationId" \
    --output text 2>/dev/null || true)

  # Strategy 3: Find unassociated EIPs with matching name pattern
  unassociated_eips=$(aws ec2 describe-addresses \
    --filters "Name=tag:Name,Values=${name_prefix}-${environment}-*" \
    --region "${region}" \
    --query "Addresses[?AssociationId==null].AllocationId" --output text 2>/dev/null || true)

  # Combine and deduplicate
  all_eips="${eips} ${name_pattern_eips} ${unassociated_eips}"
  unique_eips=$(echo "${all_eips}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

  for eip in ${unique_eips}; do
    [[ -z "${eip}" ]] && continue
    eip_name=$(aws ec2 describe-addresses \
      --allocation-ids "${eip}" \
      --region "${region}" \
      --query "Addresses[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${eip}")
    log_step "RELEASE_EIP" "Releasing Elastic IP: ${eip} (${eip_name})"
    run aws ec2 release-address --allocation-id "${eip}" --region "${region}"
  done

  # =========================================================================
  # SECOND PASS: ENIs (after NAT gateway deletion releases them)
  # =========================================================================
  log_step "ENI_CLEANUP_PASS2" "Second pass: Finding ENIs released by NAT gateway deletion..."

  pass2_enis=$(aws ec2 describe-network-interfaces \
    --filters "Name=tag:Name,Values=${name_prefix}-${environment}-*" \
              "Name=status,Values=available" \
    --region "${region}" \
    --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)

  for eni in ${pass2_enis}; do
    [[ -z "${eni}" ]] && continue
    eni_name=$(aws ec2 describe-network-interfaces \
      --network-interface-ids "${eni}" \
      --region "${region}" \
      --query "NetworkInterfaces[0].TagSet[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${eni}")
    log_step "DELETE_ENI" "Deleting ENI (pass 2): ${eni} (${eni_name})"
    run aws ec2 delete-network-interface --network-interface-id "${eni}" --region "${region}"
  done

  # =========================================================================
  # SECOND PASS: Security Groups (after ENIs are deleted)
  # =========================================================================
  log_step "SG_CLEANUP_PASS2" "Second pass: Finding remaining security groups..."

  pass2_sgs=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=${name_prefix}-${environment}-*" \
    --region "${region}" \
    --query "SecurityGroups[?GroupName!='default'].GroupId" --output text 2>/dev/null || true)

  for sg in ${pass2_sgs}; do
    [[ -z "${sg}" ]] && continue
    sg_name=$(aws ec2 describe-security-groups \
      --group-ids "${sg}" \
      --region "${region}" \
      --query "SecurityGroups[0].GroupName" \
      --output text 2>/dev/null || echo "${sg}")
    log_step "DELETE_SG" "Deleting security group (pass 2): ${sg} (${sg_name})"

    # Revoke rules first
    if [[ "${dry_run}" != "true" ]]; then
      aws ec2 describe-security-groups --group-ids "${sg}" --region "${region}" \
        --query "SecurityGroups[0].IpPermissions" --output json 2>/dev/null | \
        jq -c '.[]' 2>/dev/null | while read -r rule; do
          aws ec2 revoke-security-group-ingress \
            --group-id "${sg}" \
            --ip-permissions "${rule}" \
            --region "${region}" 2>/dev/null || true
        done
      aws ec2 describe-security-groups --group-ids "${sg}" --region "${region}" \
        --query "SecurityGroups[0].IpPermissionsEgress" --output json 2>/dev/null | \
        jq -c '.[]' 2>/dev/null | while read -r rule; do
          aws ec2 revoke-security-group-egress \
            --group-id "${sg}" \
            --ip-permissions "${rule}" \
            --region "${region}" 2>/dev/null || true
        done
    fi

    run aws ec2 delete-security-group --group-id "${sg}" --region "${region}"
  done

  # =========================================================================
  # Route Tables (must disassociate before deleting subnets)
  # =========================================================================
  log_step "RT_CLEANUP" "Finding route tables for ${environment}..."

  # Strategy 1: Find by Environment + Lifecycle tags
  rt_ids=$(aws ec2 describe-route-tables \
    --filters "Name=tag:Environment,Values=${environment}" \
              "Name=tag:Lifecycle,Values=persistent" \
    --region "${region}" \
    --query "RouteTables[].RouteTableId" --output text 2>/dev/null || true)

  # Strategy 2: Find by Name tag pattern
  name_pattern_rts=$(aws ec2 describe-route-tables \
    --region "${region}" \
    --query "RouteTables[?contains(Tags[?Key=='Name'].Value | [0], '${name_prefix}-${environment}')].RouteTableId" \
    --output text 2>/dev/null || true)

  all_rts="${rt_ids} ${name_pattern_rts}"
  unique_rts=$(echo "${all_rts}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

  for rtb in ${unique_rts}; do
    [[ -z "${rtb}" ]] && continue

    # Check if main route table
    is_main=$(aws ec2 describe-route-tables \
      --route-table-ids "${rtb}" \
      --region "${region}" \
      --query "RouteTables[0].Associations[?Main==\`true\`] | [0].Main" \
      --output text 2>/dev/null || echo "False")

    if [[ "${is_main}" == "True" ]]; then
      log_info "Skipping main route table: ${rtb}"
      continue
    fi

    rt_name=$(aws ec2 describe-route-tables \
      --route-table-ids "${rtb}" \
      --region "${region}" \
      --query "RouteTables[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${rtb}")
    log_step "DELETE_ROUTE_TABLE" "Deleting route table: ${rtb} (${rt_name})"

    # Disassociate first
    assoc_ids=$(aws ec2 describe-route-tables \
      --route-table-ids "${rtb}" \
      --region "${region}" \
      --query "RouteTables[].Associations[?Main!=\`true\`].RouteTableAssociationId" \
      --output text 2>/dev/null || true)

    for assoc_id in ${assoc_ids}; do
      [[ -z "${assoc_id}" ]] && continue
      log_info "  Disassociating: ${assoc_id}"
      run aws ec2 disassociate-route-table \
        --association-id "${assoc_id}" \
        --region "${region}"
    done

    run aws ec2 delete-route-table --route-table-id "${rtb}" --region "${region}"
  done

  # =========================================================================
  # Subnets (after route tables are disassociated)
  # =========================================================================
  log_step "SUBNET_CLEANUP" "Finding subnets for ${environment}..."

  # Strategy 1: Find by Environment + Lifecycle tags
  subnets=$(aws ec2 describe-subnets \
    --filters "Name=tag:Environment,Values=${environment}" \
              "Name=tag:Lifecycle,Values=persistent" \
    --region "${region}" \
    --query "Subnets[].SubnetId" --output text 2>/dev/null || true)

  # Strategy 2: Find by Name tag pattern
  name_pattern_subnets=$(aws ec2 describe-subnets \
    --region "${region}" \
    --query "Subnets[?contains(Tags[?Key=='Name'].Value | [0], '${name_prefix}-${environment}')].SubnetId" \
    --output text 2>/dev/null || true)

  all_subnets="${subnets} ${name_pattern_subnets}"
  unique_subnets=$(echo "${all_subnets}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

  for subnet in ${unique_subnets}; do
    [[ -z "${subnet}" ]] && continue
    subnet_name=$(aws ec2 describe-subnets \
      --subnet-ids "${subnet}" \
      --region "${region}" \
      --query "Subnets[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${subnet}")
    log_step "DELETE_SUBNET" "Deleting subnet: ${subnet} (${subnet_name})"
    run aws ec2 delete-subnet --subnet-id "${subnet}" --region "${region}"
  done

  # =========================================================================
  # Internet Gateways (detach + delete before VPC)
  # =========================================================================
  log_step "IGW_CLEANUP" "Finding internet gateways for ${environment}..."

  # Strategy 1: Find by Environment + Lifecycle tags
  igws=$(aws ec2 describe-internet-gateways \
    --filters "Name=tag:Environment,Values=${environment}" \
              "Name=tag:Lifecycle,Values=persistent" \
    --region "${region}" \
    --query "InternetGateways[].InternetGatewayId" --output text 2>/dev/null || true)

  # Strategy 2: Find by Name tag pattern
  name_pattern_igws=$(aws ec2 describe-internet-gateways \
    --region "${region}" \
    --query "InternetGateways[?contains(Tags[?Key=='Name'].Value | [0], '${name_prefix}-${environment}')].InternetGatewayId" \
    --output text 2>/dev/null || true)

  all_igws="${igws} ${name_pattern_igws}"
  unique_igws=$(echo "${all_igws}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

  for igw in ${unique_igws}; do
    [[ -z "${igw}" ]] && continue
    igw_name=$(aws ec2 describe-internet-gateways \
      --internet-gateway-ids "${igw}" \
      --region "${region}" \
      --query "InternetGateways[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${igw}")
    log_step "DELETE_IGW" "Processing internet gateway: ${igw} (${igw_name})"

    # Detach from VPCs first
    attached_vpcs=$(aws ec2 describe-internet-gateways \
      --internet-gateway-ids "${igw}" \
      --region "${region}" \
      --query "InternetGateways[].Attachments[].VpcId" --output text 2>/dev/null || true)

    for vpc in ${attached_vpcs}; do
      [[ -z "${vpc}" ]] && continue
      log_info "  Detaching from VPC: ${vpc}"
      run aws ec2 detach-internet-gateway \
        --internet-gateway-id "${igw}" \
        --vpc-id "${vpc}" \
        --region "${region}"
    done

    log_info "  Deleting IGW: ${igw}"
    run aws ec2 delete-internet-gateway --internet-gateway-id "${igw}" --region "${region}"
  done

  # =========================================================================
  # VPCs (final step)
  # =========================================================================
  log_step "VPC_CLEANUP" "Finding VPCs for ${environment}..."

  # Strategy 1: Find by Environment + Lifecycle tags
  vpcs=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Environment,Values=${environment}" \
              "Name=tag:Lifecycle,Values=persistent" \
    --region "${region}" \
    --query "Vpcs[].VpcId" --output text 2>/dev/null || true)

  # Strategy 2: Find by Name tag pattern
  name_pattern_vpcs=$(aws ec2 describe-vpcs \
    --region "${region}" \
    --query "Vpcs[?contains(Tags[?Key=='Name'].Value | [0], '${name_prefix}-${environment}')].VpcId" \
    --output text 2>/dev/null || true)

  all_vpcs="${vpcs} ${name_pattern_vpcs}"
  unique_vpcs=$(echo "${all_vpcs}" | tr ' ' '\n' | sort -u | tr '\n' ' ')

  for vpc in ${unique_vpcs}; do
    [[ -z "${vpc}" ]] && continue
    vpc_name=$(aws ec2 describe-vpcs \
      --vpc-ids "${vpc}" \
      --region "${region}" \
      --query "Vpcs[0].Tags[?Key=='Name'].Value | [0]" \
      --output text 2>/dev/null || echo "${vpc}")
    log_step "DELETE_VPC" "Deleting VPC: ${vpc} (${vpc_name})"

    if [[ "${dry_run}" != "true" ]]; then
      if ! aws ec2 delete-vpc --vpc-id "${vpc}" --region "${region}" 2>&1; then
        log_warn "VPC deletion failed. Checking remaining dependencies..."

        # Diagnostic output
        remaining_enis=$(aws ec2 describe-network-interfaces \
          --filters "Name=vpc-id,Values=${vpc}" \
          --region "${region}" \
          --query "NetworkInterfaces[].NetworkInterfaceId" --output text 2>/dev/null || true)
        if [[ -n "${remaining_enis}" ]]; then
          log_warn "  Remaining ENIs: ${remaining_enis}"
        fi

        remaining_sgs=$(aws ec2 describe-security-groups \
          --filters "Name=vpc-id,Values=${vpc}" \
          --region "${region}" \
          --query "SecurityGroups[?GroupName!='default'].GroupId" --output text 2>/dev/null || true)
        if [[ -n "${remaining_sgs}" ]]; then
          log_warn "  Remaining security groups: ${remaining_sgs}"
        fi
      fi
    else
      echo "[DRY-RUN] aws ec2 delete-vpc --vpc-id ${vpc} --region ${region}"
    fi
  done
else
  log_info "Skipping VPC cleanup (DELETE_VPC=false). VPC resources preserved for persistent infra."
  log_info "Set DELETE_VPC=true to also delete NAT gateways, EIPs, subnets, IGWs, VPCs."
fi

# =============================================================================
# TERRAFORM STATE CLEANUP (Optional)
# =============================================================================

if [[ "${clean_tf_state}" == "true" ]]; then
  log_step "TF_STATE_CLEANUP" "Cleaning up Terraform state in ${tf_dir}..."

  if [[ ! -d "${tf_dir}" ]]; then
    log_warn "Terraform directory not found: ${tf_dir}. Skipping state cleanup."
  else
    # Check if state exists
    if ! terraform -chdir="${tf_dir}" state list >/dev/null 2>&1; then
      log_warn "No Terraform state found or state inaccessible. Skipping."
    else
      log_info "Removing stale resources from Terraform state..."

      # List of resource patterns to remove from state
      # These match what this script deletes from AWS
      state_patterns=(
        "data.aws_eks_cluster.this"
        "data.aws_eks_cluster_auth.this"
        "data.kubernetes_service_v1.kong_proxy"
        "module.eks"
        "module.kubernetes_addons"
        "module.iam"
        "module.compute"
        "aws_eip.nat"
        "aws_nat_gateway.this"
        "kubernetes_config_map_v1.argocd_bootstrap"
        "kubernetes_ingress_class_v1.kong"
        "kubernetes_namespace_v1.argocd"
        "kubernetes_namespace_v1.external_secrets"
      )

      # Add VPC patterns if DELETE_VPC was set
      if [[ "${delete_vpc}" == "true" ]]; then
        state_patterns+=(
          "module.vpc"
          "module.subnets"
          "module.private_route_table"
          "module.public_route_table"
          "module.web_security_group"
        )
      fi

      for pattern in "${state_patterns[@]}"; do
        # Check if pattern exists in state
        if terraform -chdir="${tf_dir}" state list 2>/dev/null | grep -q "^${pattern}"; then
          if [[ "${dry_run}" == "true" ]]; then
            echo "[DRY-RUN] terraform -chdir=${tf_dir} state rm '${pattern}'"
          else
            log_info "  Removing: ${pattern}"
            terraform -chdir="${tf_dir}" state rm "${pattern}" 2>/dev/null || \
              log_warn "  Failed to remove ${pattern} (may not exist)"
          fi
        fi
      done

      log_info "Terraform state cleanup complete."
    fi
  fi
else
  log_info "Skipping Terraform state cleanup (CLEAN_TF_STATE=false)."
  log_info "Set CLEAN_TF_STATE=true to also remove deleted resources from Terraform state."
fi

# =============================================================================
# CLEANUP COMPLETE
# =============================================================================

echo ""
echo "============================================================================="
echo "PERSISTENT ORPHAN CLEANUP COMPLETED"
echo "============================================================================="
echo "Cluster Name: ${cluster_name}"
echo "Environment: ${environment}"
echo "Region: ${region}"
echo "Dry Run: ${dry_run}"
echo "Delete VPC: ${delete_vpc}"
echo "Delete RDS: ${delete_rds}"
echo "Clean TF State: ${clean_tf_state}"
echo "TF Dir: ${tf_dir}"
echo "Completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "============================================================================="

if [[ "${dry_run}" == "true" ]]; then
  echo ""
  echo "*** DRY RUN COMPLETE - No resources were deleted ***"
  echo "To perform actual cleanup, run with: DRY_RUN=false"
  echo ""
fi
