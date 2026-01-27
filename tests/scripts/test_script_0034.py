"""
Tests for SCRIPT-0034: RDS Request Parser

Run with: pytest -q tests/scripts/test_script_0034.py
"""

import json
from pathlib import Path

import pytest
import yaml

# Import from scripts directory
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from rds_request_parser import (
    parse_request,
    validate_enums,
    load_enums,
    generate_tfvars,
    generate_externalsecret,
    derive_secret_key,
    SIZE_TO_INSTANCE,
)


# --- Fixtures ---


@pytest.fixture
def enums_path():
    return Path(__file__).parent.parent.parent / "schemas" / "metadata" / "enums.yaml"


@pytest.fixture
def enums(enums_path):
    return load_enums(enums_path)


@pytest.fixture
def valid_request_doc():
    return {
        "id": "RDS-0001",
        "service": "postgres",
        "environment": "dev",
        "owner": "platform-team",
        "requester": "platform-team",
        "spec": {
            "databaseName": "test_db",
            "username": "test_user",
            "size": "small",
            "domain": "catalog",
            "risk": "low",
            "storageGb": 20,
            "maxStorageGb": 50,
            "backupRetentionDays": 7,
            "multiAz": False,
            "performanceInsights": True,
        },
    }


@pytest.fixture
def valid_request(valid_request_doc):
    return parse_request(valid_request_doc, Path("test.yaml"))


# --- Parse Request Tests ---


class TestParseRequest:
    def test_parses_valid_request(self, valid_request_doc):
        req = parse_request(valid_request_doc, Path("test.yaml"))

        assert req.rds_id == "RDS-0001"
        assert req.service == "postgres"
        assert req.environment == "dev"
        assert req.databaseName == "test_db"
        assert req.username == "test_user"
        assert req.size == "small"
        assert req.domain == "catalog"
        assert req.owner == "platform-team"
        assert req.requester == "platform-team"
        assert req.risk == "low"
        assert req.storageGb == 20
        assert req.maxStorageGb == 50
        assert req.backupRetentionDays == 7
        assert req.multiAz is False
        assert req.performanceInsights is True

    def test_missing_required_field_raises(self, valid_request_doc):
        del valid_request_doc["environment"]

        with pytest.raises(ValueError, match="missing required fields.*environment"):
            parse_request(valid_request_doc, Path("test.yaml"))

    def test_missing_spec_field_raises(self, valid_request_doc):
        del valid_request_doc["spec"]["databaseName"]

        with pytest.raises(
            ValueError, match="missing required fields.*spec.databaseName"
        ):
            parse_request(valid_request_doc, Path("test.yaml"))

    def test_uses_defaults_for_optional_fields(self, valid_request_doc):
        del valid_request_doc["spec"]["storageGb"]
        del valid_request_doc["spec"]["maxStorageGb"]

        req = parse_request(valid_request_doc, Path("test.yaml"))

        assert req.storageGb == 20
        assert req.maxStorageGb == 50


# --- Enum Validation Tests ---


class TestValidateEnums:
    def test_valid_enums_pass(self, valid_request, enums):
        # Should not raise
        validate_enums(valid_request, enums, Path("test.yaml"))

    def test_invalid_size_raises(self, valid_request_doc, enums):
        valid_request_doc["spec"]["size"] = "gigantic"
        req = parse_request(valid_request_doc, Path("test.yaml"))

        with pytest.raises(ValueError, match="invalid size='gigantic'"):
            validate_enums(req, enums, Path("test.yaml"))

    def test_invalid_environment_raises(self, valid_request_doc, enums):
        valid_request_doc["environment"] = "production"  # should be "prod"
        req = parse_request(valid_request_doc, Path("test.yaml"))

        with pytest.raises(ValueError, match="invalid environment='production'"):
            validate_enums(req, enums, Path("test.yaml"))

    def test_invalid_domain_raises(self, valid_request_doc, enums):
        valid_request_doc["spec"]["domain"] = "unknown-domain"
        req = parse_request(valid_request_doc, Path("test.yaml"))

        with pytest.raises(ValueError, match="invalid domain='unknown-domain'"):
            validate_enums(req, enums, Path("test.yaml"))


# --- Conditional Rule Tests ---


class TestConditionalRules:
    def test_dev_only_allows_small_size(self, valid_request_doc, enums):
        valid_request_doc["environment"] = "dev"
        valid_request_doc["spec"]["size"] = "large"
        req = parse_request(valid_request_doc, Path("test.yaml"))

        with pytest.raises(ValueError, match="Dev environment limited to size='small'"):
            validate_enums(req, enums, Path("test.yaml"))

    def test_prod_requires_backup_14_days(self, valid_request_doc, enums):
        valid_request_doc["environment"] = "prod"
        valid_request_doc["spec"]["size"] = "large"
        valid_request_doc["spec"]["backupRetentionDays"] = 7
        valid_request_doc["spec"]["multiAz"] = True
        req = parse_request(valid_request_doc, Path("test.yaml"))

        with pytest.raises(
            ValueError, match="Production requires backup_retention_days >= 14"
        ):
            validate_enums(req, enums, Path("test.yaml"))

    def test_max_storage_must_exceed_storage(self, valid_request_doc, enums):
        valid_request_doc["spec"]["storageGb"] = 50
        valid_request_doc["spec"]["maxStorageGb"] = 50
        req = parse_request(valid_request_doc, Path("test.yaml"))

        with pytest.raises(
            ValueError, match="maxStorageGb must be greater than storageGb"
        ):
            validate_enums(req, enums, Path("test.yaml"))


# --- Generation Tests ---


class TestGenerateTfvars:
    def test_generates_correct_structure(self, valid_request):
        tfvars = generate_tfvars(valid_request)

        assert "rds_databases" in tfvars
        assert "test_db" in tfvars["rds_databases"]

        db = tfvars["rds_databases"]["test_db"]
        assert db["identifier"] == "dev-test_db"
        assert db["database_name"] == "test_db"
        assert db["username"] == "test_user"
        assert db["instance_class"] == "db.t3.micro"
        assert db["allocated_storage"] == 20
        assert db["max_allocated_storage"] == 50
        assert db["backup_retention_period"] == 7
        assert db["multi_az"] is False
        assert db["performance_insights_enabled"] is True

        assert db["metadata"]["id"] == "RDS-0001"
        assert db["metadata"]["owner"] == "platform-team"

    def test_size_to_instance_mapping(self):
        assert SIZE_TO_INSTANCE["small"] == "db.t3.micro"
        assert SIZE_TO_INSTANCE["medium"] == "db.t3.small"
        assert SIZE_TO_INSTANCE["large"] == "db.t3.medium"
        assert SIZE_TO_INSTANCE["xlarge"] == "db.r6g.large"


class TestGenerateExternalSecret:
    def test_generates_correct_structure(self, valid_request):
        es = generate_externalsecret(valid_request)

        assert es["apiVersion"] == "external-secrets.io/v1beta1"
        assert es["kind"] == "ExternalSecret"

        metadata = es["metadata"]
        assert metadata["name"] == "test_db-credentials-sync"
        assert metadata["namespace"] == "test_db"
        assert metadata["labels"]["goldenpath.idp/id"] == "RDS-0001"
        assert metadata["labels"]["platform.idp/env"] == "dev"

        spec = es["spec"]
        assert spec["refreshInterval"] == "1h"
        assert spec["secretStoreRef"]["name"] == "aws-secretsmanager"
        assert spec["target"]["name"] == "test_db-db-credentials"
        assert (
            spec["dataFrom"][0]["extract"]["key"] == "goldenpath/dev/test_db/postgres"
        )


class TestDeriveSecretKey:
    def test_derives_correct_path(self, valid_request):
        key = derive_secret_key(valid_request)
        assert key == "goldenpath/dev/test_db/postgres"


# --- Integration Test ---


class TestIntegration:
    def test_full_flow_with_real_enums(self, enums_path):
        """Test the full parse -> validate -> generate flow."""
        doc = {
            "id": "RDS-INT-001",
            "service": "postgres",
            "environment": "dev",
            "owner": "platform-team",
            "requester": "platform-team",
            "spec": {
                "databaseName": "integration_db",
                "username": "int_user",
                "size": "small",
                "domain": "catalog",
                "risk": "low",
            },
        }

        enums = load_enums(enums_path)
        req = parse_request(doc, Path("test.yaml"))
        validate_enums(req, enums, Path("test.yaml"))

        tfvars = generate_tfvars(req)
        es = generate_externalsecret(req)

        # Verify outputs are valid JSON/YAML serializable
        json.dumps(tfvars)
        yaml.safe_dump(es)

        assert (
            tfvars["rds_databases"]["integration_db"]["identifier"]
            == "dev-integration_db"
        )
        assert (
            es["spec"]["dataFrom"][0]["extract"]["key"]
            == "goldenpath/dev/integration_db/postgres"
        )
