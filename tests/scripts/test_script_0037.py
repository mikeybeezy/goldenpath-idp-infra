"""
Tests for SCRIPT-0037: S3 Request Parser

Run with: pytest -q tests/scripts/test_script_0037.py

Reference: ADR-0170, schemas/requests/s3.schema.yaml
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Import from scripts directory
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from s3_request_parser import (
    S3Request,
    parse_request,
    validate_enums,
    validate_guardrails,
    validate_request,
    generate_tfvars,
    generate_iam_policy,
    tfvars_output_path,
    iam_policy_output_path,
    VALID_ENVIRONMENTS,
    VALID_PURPOSE_TYPES,
    VALID_ENCRYPTION_TYPES,
)


# --- Fixtures ---


@pytest.fixture
def valid_s3_request_doc():
    """Valid S3 request document matching schema."""
    return {
        "apiVersion": "goldenpath.io/v1",
        "kind": "S3BucketRequest",
        "id": "S3-0001",
        "environment": "dev",
        "owner": "platform-team",
        "application": "payments-api",
        "requester": "platform-team",
        "metadata": {
            "title": "Payments Uploads",
            "description": "User uploads for payments",
            "created": "2026-01-17",
        },
        "spec": {
            "bucket_name": "goldenpath-dev-payments-api-uploads",
            "purpose": {
                "type": "uploads",
                "description": "User-uploaded documents for payment verification",
            },
            "storage_class": "standard",
            "encryption": {
                "type": "sse-s3",
            },
            "versioning": True,
            "public_access": "blocked",
            "retention_policy": {
                "type": "indefinite",
                "rationale": "User documents retained for compliance",
            },
            "access_logging": {
                "enabled": False,
            },
            "cost_alert_gb": 50,
            "cors_enabled": False,
            "tags": {
                "cost-center": "payments",
            },
        },
    }


@pytest.fixture
def valid_s3_request_file(valid_s3_request_doc):
    """Create temporary YAML file with valid request."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(valid_s3_request_doc, f)
        return Path(f.name)


@pytest.fixture
def prod_s3_request_doc(valid_s3_request_doc):
    """Prod request requiring SSE-KMS and access logging."""
    doc = valid_s3_request_doc.copy()
    doc["environment"] = "prod"
    doc["spec"] = valid_s3_request_doc["spec"].copy()
    doc["spec"]["bucket_name"] = "goldenpath-prod-payments-api-uploads"
    doc["spec"]["encryption"] = {
        "type": "sse-kms",
        "kms_key_alias": "alias/platform-s3",
    }
    doc["spec"]["access_logging"] = {
        "enabled": True,
        "target_bucket": "goldenpath-prod-logs",
    }
    return doc


@pytest.fixture
def parsed_request(valid_s3_request_doc):
    """Parsed S3Request object."""
    return parse_request(valid_s3_request_doc, Path("test.yaml"))


# --- Parse Request Tests ---


class TestParseRequest:
    def test_parses_valid_request(self, valid_s3_request_doc):
        req = parse_request(valid_s3_request_doc, Path("test.yaml"))

        assert req.s3_id == "S3-0001"
        assert req.environment == "dev"
        assert req.bucket_name == "goldenpath-dev-payments-api-uploads"
        assert req.owner == "platform-team"
        assert req.application == "payments-api"
        assert req.purpose_type == "uploads"
        assert req.encryption_type == "sse-s3"
        assert req.versioning is True
        assert req.public_access == "blocked"
        assert req.retention_type == "indefinite"
        assert req.cost_alert_gb == 50
        assert req.cost_center == "payments"

    def test_missing_required_field_raises(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        del doc["spec"]["bucket_name"]

        with pytest.raises(ValueError) as exc_info:
            parse_request(doc, Path("test.yaml"))

        assert "spec.bucket_name" in str(exc_info.value)

    def test_missing_purpose_type_raises(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["purpose"] = {"description": "Test"}

        with pytest.raises(ValueError) as exc_info:
            parse_request(doc, Path("test.yaml"))

        assert "spec.purpose.type" in str(exc_info.value)

    def test_missing_cost_center_raises(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["tags"] = {}

        with pytest.raises(ValueError) as exc_info:
            parse_request(doc, Path("test.yaml"))

        assert "spec.tags.cost-center" in str(exc_info.value)


# --- Validate Enums Tests ---


class TestValidateEnums:
    def test_valid_enums_pass(self, parsed_request):
        # Should not raise
        validate_enums(parsed_request, Path("test.yaml"))

    def test_invalid_environment_raises(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["environment"] = "ephemeral"

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_enums(req, Path("test.yaml"))

        assert "environment='ephemeral'" in str(exc_info.value)

    def test_invalid_purpose_type_raises(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["purpose"] = {
            "type": "invalid-purpose",
            "description": "Test",
        }

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_enums(req, Path("test.yaml"))

        assert "purpose.type='invalid-purpose'" in str(exc_info.value)


# --- Validate Guardrails Tests ---


class TestValidateGuardrails:
    def test_dev_sse_s3_allowed(self, parsed_request):
        # Should not raise
        warnings = validate_guardrails(parsed_request, Path("test.yaml"))
        assert isinstance(warnings, list)

    def test_prod_requires_sse_kms(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["environment"] = "prod"
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["bucket_name"] = "goldenpath-prod-payments-api-uploads"
        # Keep SSE-S3 (should fail)

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_guardrails(req, Path("test.yaml"))

        assert "SSE-KMS encryption required" in str(exc_info.value)

    def test_prod_requires_access_logging(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["environment"] = "prod"
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["bucket_name"] = "goldenpath-prod-payments-api-uploads"
        doc["spec"]["encryption"] = {
            "type": "sse-kms",
            "kms_key_alias": "alias/platform-s3",
        }
        # Keep access_logging disabled (should fail)

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_guardrails(req, Path("test.yaml"))

        assert "access_logging required" in str(exc_info.value)

    def test_kms_requires_key_alias(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["encryption"] = {"type": "sse-kms"}  # Missing kms_key_alias

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_guardrails(req, Path("test.yaml"))

        assert "kms_key_alias required" in str(exc_info.value)

    def test_time_bounded_requires_lifecycle(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["retention_policy"] = {
            "type": "time-bounded",
            "rationale": "Expire after 90 days",
        }
        # No lifecycle rules

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_guardrails(req, Path("test.yaml"))

        assert "lifecycle rules required" in str(exc_info.value)

    def test_bucket_naming_convention(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["bucket_name"] = "wrong-prefix-bucket"

        req = parse_request(doc, Path("test.yaml"))

        with pytest.raises(ValueError) as exc_info:
            validate_guardrails(req, Path("test.yaml"))

        assert "bucket_name must start with" in str(exc_info.value)

    def test_public_access_exception_warning(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["public_access"] = "exception-approved"

        req = parse_request(doc, Path("test.yaml"))
        warnings = validate_guardrails(req, Path("test.yaml"))

        assert any("platform-approval" in w for w in warnings)

    def test_static_assets_warning(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["purpose"] = {
            "type": "static-assets",
            "description": "CDN content",
        }

        req = parse_request(doc, Path("test.yaml"))
        warnings = validate_guardrails(req, Path("test.yaml"))

        assert any("platform review" in w for w in warnings)


# --- Generate Tfvars Tests ---


class TestGenerateTfvars:
    def test_generates_bucket_config(self, parsed_request):
        tfvars = generate_tfvars(parsed_request)

        assert "s3_bucket" in tfvars
        bucket = tfvars["s3_bucket"]

        assert bucket["bucket_name"] == "goldenpath-dev-payments-api-uploads"
        assert bucket["versioning_enabled"] is True
        assert bucket["encryption"]["type"] == "SSE_S3"
        assert bucket["public_access_block"]["restrict_public_buckets"] is True

    def test_generates_tags(self, parsed_request):
        tfvars = generate_tfvars(parsed_request)
        tags = tfvars["s3_bucket"]["tags"]

        assert tags["Environment"] == "dev"
        assert tags["Owner"] == "platform-team"
        assert tags["Application"] == "payments-api"
        assert tags["Purpose"] == "uploads"
        assert tags["CostCenter"] == "payments"
        assert tags["RequestId"] == "S3-0001"

    def test_generates_cost_alert(self, parsed_request):
        tfvars = generate_tfvars(parsed_request)

        assert "cost_alert" in tfvars
        assert tfvars["cost_alert"]["threshold_gb"] == 50

    def test_generates_lifecycle_rules(self, valid_s3_request_doc):
        doc = valid_s3_request_doc.copy()
        doc["spec"] = valid_s3_request_doc["spec"].copy()
        doc["spec"]["retention_policy"] = {
            "type": "time-bounded",
            "rationale": "Expire after 90 days",
        }
        doc["spec"]["lifecycle"] = {
            "expire_days": 90,
            "transition_to_ia_days": 30,
        }

        req = parse_request(doc, Path("test.yaml"))
        tfvars = generate_tfvars(req)

        rules = tfvars["s3_bucket"]["lifecycle_rules"]
        assert len(rules) == 2
        assert rules[0]["id"] == "expire-objects"
        assert rules[0]["expiration"]["days"] == 90


# --- Generate IAM Policy Tests ---


class TestGenerateIamPolicy:
    def test_generates_valid_policy(self, parsed_request):
        policy = generate_iam_policy(parsed_request)

        assert policy["Version"] == "2012-10-17"
        assert len(policy["Statement"]) == 1

        statement = policy["Statement"][0]
        assert statement["Effect"] == "Allow"
        assert "s3:GetObject" in statement["Action"]
        assert "s3:PutObject" in statement["Action"]

    def test_policy_resources_match_bucket(self, parsed_request):
        policy = generate_iam_policy(parsed_request)
        resources = policy["Statement"][0]["Resource"]

        assert "arn:aws:s3:::goldenpath-dev-payments-api-uploads" in resources
        assert "arn:aws:s3:::goldenpath-dev-payments-api-uploads/*" in resources


# --- Output Path Tests ---


class TestOutputPaths:
    def test_tfvars_output_path(self, parsed_request):
        path = tfvars_output_path(Path("envs"), parsed_request)

        assert path == Path("envs/dev/s3/generated/S3-0001.auto.tfvars.json")

    def test_iam_policy_output_path(self, parsed_request):
        path = iam_policy_output_path(Path("envs"), parsed_request)

        assert path == Path("envs/generated/iam/payments-api-s3-policy.json")


# --- Full Validation Tests ---


class TestFullValidation:
    def test_valid_dev_request_passes(self, valid_s3_request_doc):
        req = parse_request(valid_s3_request_doc, Path("test.yaml"))
        warnings = validate_request(req, Path("test.yaml"))

        assert isinstance(warnings, list)

    def test_valid_prod_request_passes(self, prod_s3_request_doc):
        req = parse_request(prod_s3_request_doc, Path("test.yaml"))
        warnings = validate_request(req, Path("test.yaml"))

        assert isinstance(warnings, list)


# --- Idempotence Tests ---


class TestIdempotence:
    def test_same_input_produces_same_output(self, valid_s3_request_doc):
        req1 = parse_request(valid_s3_request_doc, Path("test.yaml"))
        req2 = parse_request(valid_s3_request_doc, Path("test.yaml"))

        tfvars1 = generate_tfvars(req1)
        tfvars2 = generate_tfvars(req2)

        assert json.dumps(tfvars1, sort_keys=True) == json.dumps(tfvars2, sort_keys=True)
