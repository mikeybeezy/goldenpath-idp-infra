"""
Tests for scripts/eks_request_parser.py (SCRIPT-0043)
EKS Request Parser/Generator

Test Categories:
- Parsing: YAML document parsing and field extraction
- Validation: Required fields, enum validation, business rules
- Generation: tfvars output, catalog updates, audit records
- Edge cases: Missing fields, invalid values, boundary conditions
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from eks_request_parser import (
    EksRequest,
    load_yaml,
    load_enums,
    parse_request,
    validate_enums,
    generate_tfvars,
    validate_request,
    tfvars_output_path,
    NODE_TIER_TO_INSTANCE,
    derive_risk,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def valid_eks_request_doc():
    """Minimal valid EKS request document."""
    return {
        "id": "EKS-0001",
        "environment": "dev",
        "region": "eu-west-2",
        "owner": "platform-team",
        "requester": "engineer@example.com",
        "spec": {
            "mode": "cluster-only",
            "build": {"buildId": "26-01-26-01"},
            "cluster": {
                "clusterName": "test-cluster",
                "kubernetesVersion": "1.29",
            },
            "nodePool": {
                "nodeTier": "small",
                "nodeDesired": 2,
                "nodeMax": 4,
            },
        },
    }


@pytest.fixture
def valid_enums():
    """Valid enums configuration."""
    return {
        "eks_environments": ["dev", "test", "staging", "prod"],
        "eks_modes": ["cluster-only", "cluster+bootstrap", "bootstrap-only"],
        "eks_node_tiers": ["small", "medium", "large", "xlarge"],
        "kubernetes_versions": ["1.28", "1.29", "1.30"],
        "eks_capacity_types": ["ON_DEMAND", "SPOT"],
        "eks_gitops_controllers": ["argocd", "flux"],
        "eks_bootstrap_profiles": ["core-tooling", "minimal", "full"],
        "eks_ingress_providers": ["kong", "nginx", "none"],
        "eks_aws_lb_types": ["nlb", "alb"],
        "owners": ["platform-team", "app-team-a", "app-team-b"],
    }


@pytest.fixture
def enums_file(valid_enums, tmp_path):
    """Create a temporary enums file."""
    enums_path = tmp_path / "enums.yaml"
    enums_path.write_text(yaml.safe_dump(valid_enums))
    return enums_path


@pytest.fixture
def request_file(valid_eks_request_doc, tmp_path):
    """Create a temporary request file."""
    req_path = tmp_path / "EKS-0001.yaml"
    req_path.write_text(yaml.safe_dump(valid_eks_request_doc))
    return req_path


# ============================================================================
# Test: load_yaml
# ============================================================================

class TestLoadYaml:
    def test_loads_valid_yaml(self, tmp_path):
        """Should load a valid YAML file."""
        path = tmp_path / "test.yaml"
        path.write_text("key: value\nnested:\n  a: 1")
        result = load_yaml(path)
        assert result == {"key": "value", "nested": {"a": 1}}

    def test_returns_empty_dict_for_empty_file(self, tmp_path):
        """Should return empty dict for empty YAML."""
        path = tmp_path / "empty.yaml"
        path.write_text("")
        result = load_yaml(path)
        assert result == {}

    def test_returns_dict_for_null_yaml(self, tmp_path):
        """Should return empty dict for null YAML."""
        path = tmp_path / "null.yaml"
        path.write_text("---\n")
        result = load_yaml(path)
        assert result == {}


# ============================================================================
# Test: load_enums
# ============================================================================

class TestLoadEnums:
    def test_loads_enum_mappings(self, enums_file, valid_enums):
        """Should load and map enums correctly."""
        enums = load_enums(enums_file)
        assert enums["environment"] == valid_enums["eks_environments"]
        assert enums["mode"] == valid_enums["eks_modes"]
        assert enums["node_tier"] == valid_enums["eks_node_tiers"]
        assert enums["owner"] == valid_enums["owners"]

    def test_returns_empty_lists_for_missing_enums(self, tmp_path):
        """Should return empty lists for missing enum keys."""
        path = tmp_path / "minimal.yaml"
        path.write_text("other_key: value")
        enums = load_enums(path)
        assert enums["environment"] == []
        assert enums["mode"] == []


# ============================================================================
# Test: parse_request
# ============================================================================

class TestParseRequest:
    def test_parses_minimal_valid_request(self, valid_eks_request_doc, tmp_path):
        """Should parse a minimal valid request."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        assert req.eks_id == "EKS-0001"
        assert req.environment == "dev"
        assert req.region == "eu-west-2"
        assert req.owner == "platform-team"
        assert req.cluster_name == "test-cluster"
        assert req.kubernetes_version == "1.29"
        assert req.instance_type == "t3.small"  # Resolved from node_tier

    def test_raises_on_missing_required_fields(self, tmp_path):
        """Should raise ValueError for missing required fields."""
        doc = {"id": "EKS-0001"}  # Missing most fields
        path = tmp_path / "invalid.yaml"

        with pytest.raises(ValueError) as exc_info:
            parse_request(doc, path)

        assert "missing required fields" in str(exc_info.value)

    def test_raises_on_missing_build_id_for_cluster_only(self, valid_eks_request_doc, tmp_path):
        """Should raise when build_id missing for cluster-only mode."""
        del valid_eks_request_doc["spec"]["build"]["buildId"]
        path = tmp_path / "req.yaml"

        with pytest.raises(ValueError) as exc_info:
            parse_request(valid_eks_request_doc, path)

        assert "spec.build.buildId" in str(exc_info.value)

    def test_raises_on_invalid_node_sizing(self, valid_eks_request_doc, tmp_path):
        """Should raise when min > desired or desired > max."""
        valid_eks_request_doc["spec"]["nodePool"]["nodeMin"] = 10
        valid_eks_request_doc["spec"]["nodePool"]["nodeDesired"] = 2
        path = tmp_path / "req.yaml"

        with pytest.raises(ValueError) as exc_info:
            parse_request(valid_eks_request_doc, path)

        assert "min <= desired <= max" in str(exc_info.value)

    def test_resolves_instance_type_from_tier(self, valid_eks_request_doc, tmp_path):
        """Should resolve instance type from node tier."""
        valid_eks_request_doc["spec"]["nodePool"]["nodeTier"] = "large"
        path = tmp_path / "req.yaml"

        req = parse_request(valid_eks_request_doc, path)
        assert req.instance_type == "t3.large"

    def test_uses_explicit_instance_type_over_tier(self, valid_eks_request_doc, tmp_path):
        """Should prefer explicit instance_type over node_tier."""
        valid_eks_request_doc["spec"]["nodePool"]["instanceType"] = "m5.xlarge"
        path = tmp_path / "req.yaml"

        req = parse_request(valid_eks_request_doc, path)
        assert req.instance_type == "m5.xlarge"

    def test_parses_camelCase_fields(self, tmp_path):
        """Should handle camelCase field names as expected by the parser."""
        doc = {
            "metadata": {
                "id": "EKS-0002",
                "environment": "test",
                "region": "us-east-1",
                "owner": "platform-team",
                "requester": "test@example.com",
            },
            "spec": {
                "mode": "cluster-only",
                "build": {"buildId": "26-01-26-02"},
                "cluster": {
                    "clusterName": "camel-cluster",
                    "kubernetesVersion": "1.29",
                    "privateEndpointOnly": True,
                },
                "nodePool": {
                    "nodeTier": "medium",
                    "nodeDesired": 3,
                    "nodeMax": 6,
                },
            },
        }
        path = tmp_path / "camel.yaml"

        req = parse_request(doc, path)
        assert req.cluster_name == "camel-cluster"
        assert req.build_id == "26-01-26-02"

    def test_defaults_are_applied(self, valid_eks_request_doc, tmp_path):
        """Should apply default values for optional fields."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        assert req.capacity_type == "ON_DEMAND"
        assert req.gitops_controller == "argocd"
        assert req.gitops_install == True
        assert req.ingress_provider == "kong"
        assert req.ssm_break_glass == True
        assert req.ssh_break_glass == False


# ============================================================================
# Test: validate_enums
# ============================================================================

class TestValidateEnums:
    def test_passes_for_valid_values(self, valid_eks_request_doc, valid_enums, tmp_path):
        """Should pass validation for valid enum values."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)
        loaded_enums = {
            "environment": valid_enums["eks_environments"],
            "mode": valid_enums["eks_modes"],
            "node_tier": valid_enums["eks_node_tiers"],
            "kubernetes_version": valid_enums["kubernetes_versions"],
            "capacity_type": valid_enums["eks_capacity_types"],
            "gitops_controller": valid_enums["eks_gitops_controllers"],
            "bootstrap_profile": valid_enums["eks_bootstrap_profiles"],
            "ingress_provider": valid_enums["eks_ingress_providers"],
            "aws_lb_type": valid_enums["eks_aws_lb_types"],
            "owner": valid_enums["owners"],
        }

        # Should not raise
        validate_enums(req, loaded_enums, path)

    def test_raises_for_invalid_environment(self, valid_eks_request_doc, valid_enums, tmp_path):
        """Should raise for invalid environment value."""
        valid_eks_request_doc["environment"] = "invalid-env"
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)
        loaded_enums = {
            "environment": valid_enums["eks_environments"],
            "mode": [],
            "node_tier": [],
            "kubernetes_version": [],
            "capacity_type": [],
            "gitops_controller": [],
            "bootstrap_profile": [],
            "ingress_provider": [],
            "aws_lb_type": [],
            "owner": [],
        }

        with pytest.raises(ValueError) as exc_info:
            validate_enums(req, loaded_enums, path)

        assert "invalid environment" in str(exc_info.value)

    def test_skips_empty_enum_lists(self, valid_eks_request_doc, tmp_path):
        """Should skip validation when enum list is empty."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)
        empty_enums = {k: [] for k in ["environment", "mode", "node_tier",
                                        "kubernetes_version", "capacity_type",
                                        "gitops_controller", "bootstrap_profile",
                                        "ingress_provider", "aws_lb_type", "owner"]}

        # Should not raise
        validate_enums(req, empty_enums, path)


# ============================================================================
# Test: generate_tfvars
# ============================================================================

class TestGenerateTfvars:
    def test_generates_valid_tfvars(self, valid_eks_request_doc, tmp_path):
        """Should generate valid tfvars structure."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        tfvars = generate_tfvars(req)

        assert tfvars["build_id"] == "26-01-26-01"
        assert tfvars["cluster_lifecycle"] == "ephemeral"
        assert tfvars["eks_config"]["enabled"] == True
        assert tfvars["eks_config"]["cluster_name"] == "test-cluster"
        assert tfvars["eks_config"]["version"] == "1.29"

    def test_node_group_structure(self, valid_eks_request_doc, tmp_path):
        """Should generate correct node group structure."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        tfvars = generate_tfvars(req)
        node_group = tfvars["eks_config"]["node_group"]

        assert node_group["name"] == "dev-default"
        assert node_group["min_size"] == 2  # Defaults to desired if not set
        assert node_group["desired_size"] == 2
        assert node_group["max_size"] == 4
        assert node_group["instance_types"] == ["t3.small"]
        assert node_group["capacity_type"] == "ON_DEMAND"

    def test_cluster_lifecycle_persistent_without_build_id(self, valid_eks_request_doc, tmp_path):
        """Should set cluster_lifecycle to persistent when no build_id."""
        valid_eks_request_doc["spec"]["mode"] = "bootstrap-only"
        valid_eks_request_doc["spec"]["build"]["buildId"] = ""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        tfvars = generate_tfvars(req)
        assert tfvars["cluster_lifecycle"] == "persistent"

    def test_bootstrap_mode_enables_k8s_resources(self, valid_eks_request_doc, tmp_path):
        """Should enable k8s resources for bootstrap modes."""
        valid_eks_request_doc["spec"]["mode"] = "cluster+bootstrap"
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        tfvars = generate_tfvars(req)
        assert tfvars["enable_k8s_resources"] == True
        assert tfvars["apply_kubernetes_addons"] == True


# ============================================================================
# Test: tfvars_output_path
# ============================================================================

class TestTfvarsOutputPath:
    def test_generates_correct_path(self, valid_eks_request_doc, tmp_path):
        """Should generate the correct output path."""
        path = tmp_path / "req.yaml"
        req = parse_request(valid_eks_request_doc, path)

        out_path = tfvars_output_path(Path("envs"), req)

        assert str(out_path) == "envs/dev/clusters/generated/EKS-0001.auto.tfvars.json"


# ============================================================================
# Test: derive_risk
# ============================================================================

class TestDeriveRisk:
    def test_prod_is_high(self):
        assert derive_risk("prod") == "high"

    def test_staging_is_medium(self):
        assert derive_risk("staging") == "medium"

    def test_dev_is_low(self):
        assert derive_risk("dev") == "low"

    def test_test_is_low(self):
        assert derive_risk("test") == "low"


# ============================================================================
# Test: NODE_TIER_TO_INSTANCE mapping
# ============================================================================

class TestNodeTierMapping:
    def test_all_tiers_mapped(self):
        """Should have all expected tier mappings."""
        assert NODE_TIER_TO_INSTANCE["small"] == "t3.small"
        assert NODE_TIER_TO_INSTANCE["medium"] == "t3.medium"
        assert NODE_TIER_TO_INSTANCE["large"] == "t3.large"
        assert NODE_TIER_TO_INSTANCE["xlarge"] == "t3.xlarge"

    def test_unknown_tier_returns_empty(self):
        """Should return empty string for unknown tier."""
        assert NODE_TIER_TO_INSTANCE.get("unknown", "") == ""


# ============================================================================
# Test: Integration - Full flow
# ============================================================================

class TestIntegrationFlow:
    def test_validate_mode_full_flow(self, request_file, enums_file, valid_enums):
        """Test the full validation flow."""
        doc = load_yaml(request_file)
        enums = load_enums(enums_file)
        req = parse_request(doc, request_file)
        validate_request(req, enums, request_file)  # Should not raise

    def test_generate_mode_full_flow(self, request_file, enums_file, tmp_path):
        """Test the full generation flow."""
        doc = load_yaml(request_file)
        enums = load_enums(enums_file)
        req = parse_request(doc, request_file)
        validate_request(req, enums, request_file)

        tfvars = generate_tfvars(req)
        out_path = tfvars_output_path(tmp_path, req)

        # Write output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(tfvars, indent=2))

        # Verify
        assert out_path.exists()
        written = json.loads(out_path.read_text())
        assert written["eks_config"]["cluster_name"] == "test-cluster"
