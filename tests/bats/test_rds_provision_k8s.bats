#!/usr/bin/env bats
# Tests for RDS K8s-based provisioning
# Related: ADR-0165, ADR-0166, PRD-0001
# TDD Phase: RED (tests written before implementation)

load 'helpers/common'

# =============================================================================
# Test Setup
# =============================================================================

setup() {
    export PROJECT_ROOT="${BATS_TEST_DIRNAME}/../.."
    export MAKEFILE="${PROJECT_ROOT}/Makefile"
}

# =============================================================================
# Tier 1: Unit Tests - Makefile Target Existence
# =============================================================================

@test "rds-provision-k8s: target exists in Makefile" {
    # This test verifies that the rds-provision-k8s target exists in the Makefile
    # Expected: FAIL initially (target does not exist)
    run grep -E "^rds-provision-k8s:" "$MAKEFILE"
    assert_success
    assert_output_contains "rds-provision-k8s:"
}

@test "rds-provision-k8s: target is declared in .PHONY" {
    # Verify the target is properly declared as PHONY
    run grep -E "\.PHONY:.*rds-provision-k8s" "$MAKEFILE"
    assert_success
}

@test "rds-provision-k8s: checks for Argo WorkflowTemplate existence" {
    # The target must verify the WorkflowTemplate exists before proceeding
    # Expected behavior: kubectl get workflowtemplate check
    run grep -A 30 "^rds-provision-k8s:" "$MAKEFILE"
    assert_success
    assert_output_contains "kubectl"
    assert_output_contains "workflowtemplate"
}

@test "rds-provision-k8s: uses argo submit to trigger workflow" {
    # The target must use argo CLI or kubectl to submit the workflow
    run grep -A 30 "^rds-provision-k8s:" "$MAKEFILE"
    assert_success
    # Should use either argo submit or kubectl create workflow
    [[ "$output" =~ "argo submit" ]] || [[ "$output" =~ "kubectl create" ]]
}

@test "rds-provision-k8s: waits for workflow completion" {
    # The target must wait for the workflow to complete (not fire-and-forget)
    run grep -A 45 "^rds-provision-k8s:" "$MAKEFILE"
    assert_success
    # Should have --wait or argo wait
    [[ "$output" =~ "--wait" ]] || [[ "$output" =~ "argo wait" ]]
}

# =============================================================================
# Tier 1: Unit Tests - Deploy Ordering
# =============================================================================

@test "deploy-persistent v4: does NOT call rds-deploy (which bundles local provisioning)" {
    # After the fix, deploy-persistent should NOT call rds-deploy
    # because rds-deploy bundles terraform + local Python provisioning together
    # Instead it should call rds-infra-only + rds-provision-k8s (after bootstrap)
    run awk '/^ifeq.*BOOTSTRAP_VERSION.*v4/,/^else/' "$MAKEFILE"
    assert_success
    # Should NOT contain rds-deploy (bundles local provisioning)
    refute_output_contains "rds-deploy"
}

@test "deploy-persistent v4: calls rds-provision-k8s after bootstrap" {
    # The correct order is: rds-apply -> bootstrap -> rds-provision-k8s
    run awk '/^ifeq.*BOOTSTRAP_VERSION.*v4/,/^endif/' "$MAKEFILE"
    assert_success
    assert_output_contains "rds-provision-k8s"

    # Verify ordering: bootstrap-persistent-v4 comes before rds-provision-k8s
    local bootstrap_line=$(echo "$output" | grep -n "bootstrap-persistent-v4" | head -1 | cut -d: -f1)
    local provision_line=$(echo "$output" | grep -n "rds-provision-k8s" | head -1 | cut -d: -f1)

    # provision_line must be greater than bootstrap_line (comes after)
    [[ "$provision_line" -gt "$bootstrap_line" ]]
}

@test "deploy-persistent v4: rds-infra-only runs before bootstrap (Terraform only)" {
    # rds-infra-only should only run Terraform, not provision databases
    # The old rds-deploy bundled both - v4 uses rds-infra-only instead
    run awk '/^ifeq.*BOOTSTRAP_VERSION.*v4/,/^else/' "$MAKEFILE"
    assert_success
    # Should call rds-infra-only (Terraform only, no provisioning)
    assert_output_contains "rds-infra-only"
}

# =============================================================================
# Tier 1: Unit Tests - Error Handling
# =============================================================================

@test "rds-provision-k8s: fails with clear error if WorkflowTemplate not found" {
    # The target must provide a clear error message and exit non-zero
    run grep -A 30 "^rds-provision-k8s:" "$MAKEFILE"
    assert_success
    assert_output_contains "ERROR"
    assert_output_contains "WorkflowTemplate"
}

@test "rds-provision-k8s: suggests remediation command on failure" {
    # Error message should tell the user how to fix it
    run grep -A 30 "^rds-provision-k8s:" "$MAKEFILE"
    assert_success
    assert_output_contains "kubectl apply"
    assert_output_contains "platform-system"
}

# =============================================================================
# Tier 2: Integration Tests - WorkflowTemplate
# =============================================================================

@test "Argo WorkflowTemplate: rds-provision exists in gitops" {
    # Verify the WorkflowTemplate YAML exists in the repo
    run test -f "${PROJECT_ROOT}/gitops/kustomize/platform-system/rds-provision-workflowtemplate.yaml"
    assert_success
}

@test "Argo WorkflowTemplate: has correct name and namespace" {
    # Verify the template has the expected metadata
    local template="${PROJECT_ROOT}/gitops/kustomize/platform-system/rds-provision-workflowtemplate.yaml"
    run grep -E "name: rds-provision" "$template"
    assert_success
    run grep -E "namespace: platform-system" "$template"
    assert_success
}

@test "Argo WorkflowTemplate: is included in kustomization" {
    # Verify the template is included in the kustomization.yaml
    local kustomization="${PROJECT_ROOT}/gitops/kustomize/platform-system/kustomization.yaml"
    run grep "rds-provision-workflowtemplate.yaml" "$kustomization"
    assert_success
}

# =============================================================================
# Tier 1: Prevention Tests
# =============================================================================

@test "rds-infra-only: does NOT call rds-provision-auto (prevention)" {
    # rds-infra-only should only do Terraform (init + apply)
    # NOT database provisioning - that's done separately via rds-provision-k8s
    run grep -A 20 "^rds-infra-only:" "$MAKEFILE"
    assert_success
    # Should NOT contain rds-provision-auto (local Python provisioning)
    refute_output_contains "rds-provision-auto"
}

@test "Makefile: documents correct deployment order" {
    # The Makefile should document that provisioning happens after bootstrap
    run grep -B 5 -A 5 "rds-provision-k8s" "$MAKEFILE"
    assert_success
    # Should have a comment explaining the order
    assert_output_contains "after bootstrap"
}
