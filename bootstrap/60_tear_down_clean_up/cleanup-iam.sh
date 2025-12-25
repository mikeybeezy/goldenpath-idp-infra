#!/usr/bin/env bash
set -euo pipefail

# Cleanup IAM roles and policies created by this repo.
# Usage:
#   bootstrap/60_tear_down_clean_up/cleanup-iam.sh [--yes]
#
# Default is dry-run. Use --yes to delete.

confirm="${1:-}"

debug_echo() {
  echo "$*"
}

if [[ "${confirm}" != "--yes" ]]; then
  debug_echo "Dry-run mode. Re-run with --yes to delete."
fi

ROLE_PREFIX="goldenpath-"
POLICY_PREFIX="goldenpath-"

roles=$(aws iam list-roles --query "Roles[?starts_with(RoleName, \`${ROLE_PREFIX}\`)].RoleName" --output text)
policies=$(aws iam list-policies --scope Local --query "Policies[?starts_with(PolicyName, \`${POLICY_PREFIX}\`)].Arn" --output text)

debug_echo "Roles to review:"
debug_echo "${roles:-<none>}"

debug_echo "Policies to review:"
debug_echo "${policies:-<none>}"

if [[ "${confirm}" != "--yes" ]]; then
  exit 0
fi

for role in ${roles}; do
  debug_echo "Cleaning role: ${role}"

  attached=$(aws iam list-attached-role-policies --role-name "${role}" --query "AttachedPolicies[].PolicyArn" --output text)
  for arn in ${attached}; do
    aws iam detach-role-policy --role-name "${role}" --policy-arn "${arn}"
  done

  inline=$(aws iam list-role-policies --role-name "${role}" --query "PolicyNames[]" --output text)
  for name in ${inline}; do
    aws iam delete-role-policy --role-name "${role}" --policy-name "${name}"
  done

  aws iam delete-role --role-name "${role}"
done

for arn in ${policies}; do
  debug_echo "Deleting policy: ${arn}"

  roles_for=$(aws iam list-entities-for-policy --policy-arn "${arn}" --query "PolicyRoles[].RoleName" --output text)
  for role in ${roles_for}; do
    aws iam detach-role-policy --role-name "${role}" --policy-arn "${arn}"
  done

  users_for=$(aws iam list-entities-for-policy --policy-arn "${arn}" --query "PolicyUsers[].UserName" --output text)
  for user in ${users_for}; do
    aws iam detach-user-policy --user-name "${user}" --policy-arn "${arn}"
  done

  groups_for=$(aws iam list-entities-for-policy --policy-arn "${arn}" --query "PolicyGroups[].GroupName" --output text)
  for group in ${groups_for}; do
    aws iam detach-group-policy --group-name "${group}" --policy-arn "${arn}"
  done

  aws iam delete-policy --policy-arn "${arn}"
done

debug_echo "IAM cleanup done."
