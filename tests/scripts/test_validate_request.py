"""
Tests for scripts/validate_request.py - Bespoke Schema Validator.

Tests:
- Type validation (string, integer, boolean, object, array)
- Pattern validation (regex)
- Enum validation (inline and enum_from)
- Required field validation
- Nested object validation
- Conditional rule evaluation
- Numeric constraints (minimum, maximum)
- String length constraints (minLength, maxLength)

Reference: EC-0016-bespoke-schema-validator.md
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validate_request import (
    BespokeSchemaValidator,
    EnumResolver,
    ValidationError,
    ValidationResult,
    find_schema_for_request,
)


class TestEnumResolver:
    """Tests for EnumResolver."""

    def test_load_flat_enums(self, tmp_path):
        """Should load flat enum lists."""
        enums_file = tmp_path / "enums.yaml"
        enums_file.write_text("""
environments:
  - dev
  - test
  - prod
owners:
  - platform-team
  - app-team
""")
        resolver = EnumResolver(enums_file)

        assert resolver.resolve("environments") == ["dev", "test", "prod"]
        assert resolver.resolve("owners") == ["platform-team", "app-team"]

    def test_load_nested_enums(self, tmp_path):
        """Should load nested enums with values key."""
        enums_file = tmp_path / "enums.yaml"
        enums_file.write_text("""
security:
  secret_types:
    description: "Secret classification"
    values:
      - database-credentials
      - api-key
      - generic
""")
        resolver = EnumResolver(enums_file)

        assert resolver.resolve("security.secret_types") == [
            "database-credentials", "api-key", "generic"
        ]

    def test_resolve_missing_enum(self, tmp_path):
        """Should return None for missing enum."""
        enums_file = tmp_path / "enums.yaml"
        enums_file.write_text("environments: [dev]")
        resolver = EnumResolver(enums_file)

        assert resolver.resolve("nonexistent") is None


class TestBespokeSchemaValidator:
    """Tests for BespokeSchemaValidator."""

    @pytest.fixture
    def validator(self):
        """Create a validator without enums."""
        return BespokeSchemaValidator()

    @pytest.fixture
    def validator_with_enums(self, tmp_path):
        """Create a validator with enums."""
        enums_file = tmp_path / "enums.yaml"
        enums_file.write_text("""
owners:
  - platform-team
  - app-team
environments:
  - dev
  - test
  - prod
""")
        return BespokeSchemaValidator(enums_file)

    # Type validation tests
    def test_validate_string_type(self, validator):
        """Should validate string type correctly."""
        schema = {"properties": {"name": {"type": "string"}}, "required": []}
        request = {"name": "test"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_string_type_failure(self, validator):
        """Should fail when string expected but got number."""
        schema = {"properties": {"name": {"type": "string"}}, "required": []}
        request = {"name": 123}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("Expected type 'string'" in e.message for e in result.errors)

    def test_validate_integer_type(self, validator):
        """Should validate integer type correctly."""
        schema = {"properties": {"count": {"type": "integer"}}, "required": []}
        request = {"count": 42}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_validate_boolean_type(self, validator):
        """Should validate boolean type correctly."""
        schema = {"properties": {"enabled": {"type": "boolean"}}, "required": []}
        request = {"enabled": True}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_validate_object_type(self, validator):
        """Should validate object type correctly."""
        schema = {"properties": {"config": {"type": "object"}}, "required": []}
        request = {"config": {"key": "value"}}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    # Pattern validation tests
    def test_validate_pattern_match(self, validator):
        """Should pass when pattern matches."""
        schema = {
            "properties": {"id": {"type": "string", "pattern": "^S3-[0-9]{4}$"}},
            "required": [],
        }
        request = {"id": "S3-0001"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_validate_pattern_mismatch(self, validator):
        """Should fail when pattern doesn't match."""
        schema = {
            "properties": {"id": {"type": "string", "pattern": "^S3-[0-9]{4}$"}},
            "required": [],
        }
        request = {"id": "INVALID"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("does not match pattern" in e.message for e in result.errors)

    # Enum validation tests
    def test_validate_inline_enum(self, validator):
        """Should validate against inline enum values."""
        schema = {
            "properties": {"env": {"type": "string", "enum": ["dev", "prod"]}},
            "required": [],
        }
        request = {"env": "dev"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_validate_inline_enum_failure(self, validator):
        """Should fail when value not in enum."""
        schema = {
            "properties": {"env": {"type": "string", "enum": ["dev", "prod"]}},
            "required": [],
        }
        request = {"env": "staging"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("not in allowed values" in e.message for e in result.errors)

    def test_validate_enum_from(self, validator_with_enums):
        """Should validate against enum_from reference."""
        schema = {
            "properties": {"owner": {"type": "string", "enum_from": "owners"}},
            "required": [],
        }
        request = {"owner": "platform-team"}

        result = validator_with_enums.validate(
            request, schema, "test.yaml", "schema.yaml"
        )

        assert result.valid is True

    def test_validate_enum_from_failure(self, validator_with_enums):
        """Should fail when value not in enum_from reference."""
        schema = {
            "properties": {"owner": {"type": "string", "enum_from": "owners"}},
            "required": [],
        }
        request = {"owner": "unknown-team"}

        result = validator_with_enums.validate(
            request, schema, "test.yaml", "schema.yaml"
        )

        assert result.valid is False
        assert any("not in enum 'owners'" in e.message for e in result.errors)

    # Required field tests
    def test_validate_required_field_present(self, validator):
        """Should pass when required field is present."""
        schema = {"properties": {"id": {"type": "string"}}, "required": ["id"]}
        request = {"id": "test"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_validate_required_field_missing(self, validator):
        """Should fail when required field is missing."""
        schema = {"properties": {"id": {"type": "string"}}, "required": ["id"]}
        request = {}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("Required field 'id' is missing" in e.message for e in result.errors)

    # Numeric constraint tests
    def test_validate_minimum(self, validator):
        """Should validate minimum constraint."""
        schema = {
            "properties": {"count": {"type": "integer", "minimum": 1}},
            "required": [],
        }
        request = {"count": 0}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("less than minimum" in e.message for e in result.errors)

    def test_validate_maximum(self, validator):
        """Should validate maximum constraint."""
        schema = {
            "properties": {"count": {"type": "integer", "maximum": 100}},
            "required": [],
        }
        request = {"count": 150}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("greater than maximum" in e.message for e in result.errors)

    # String length tests
    def test_validate_min_length(self, validator):
        """Should validate minLength constraint."""
        schema = {
            "properties": {"desc": {"type": "string", "minLength": 10}},
            "required": [],
        }
        request = {"desc": "short"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("less than minLength" in e.message for e in result.errors)

    def test_validate_max_length(self, validator):
        """Should validate maxLength constraint."""
        schema = {
            "properties": {"desc": {"type": "string", "maxLength": 5}},
            "required": [],
        }
        request = {"desc": "this is too long"}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("greater than maxLength" in e.message for e in result.errors)

    # Nested object tests
    def test_validate_nested_object(self, validator):
        """Should validate nested object properties."""
        schema = {
            "properties": {
                "config": {
                    "type": "object",
                    "properties": {"enabled": {"type": "boolean"}},
                    "required": ["enabled"],
                }
            },
            "required": [],
        }
        request = {"config": {"enabled": True}}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_validate_nested_object_missing_required(self, validator):
        """Should fail when nested required field is missing."""
        schema = {
            "properties": {
                "config": {
                    "type": "object",
                    "properties": {"enabled": {"type": "boolean"}},
                    "required": ["enabled"],
                }
            },
            "required": [],
        }
        request = {"config": {}}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("config.enabled" in e.path for e in result.errors)

    # Conditional rule tests
    def test_conditional_rule_applies(self, validator):
        """Should apply conditional rule when condition matches."""
        schema = {
            "properties": {
                "env": {"type": "string"},
                "encryption": {
                    "type": "object",
                    "properties": {"type": {"type": "string"}},
                },
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_requires_kms",
                    "when": {"env": {"equals": "prod"}},
                    "then": {
                        "encryption.type": {
                            "equals": "sse-kms",
                            "error": "Prod requires KMS",
                        }
                    },
                }
            ],
        }
        request = {"env": "prod", "encryption": {"type": "sse-s3"}}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("Prod requires KMS" in e.message for e in result.errors)

    def test_conditional_rule_does_not_apply(self, validator):
        """Should not apply conditional rule when condition doesn't match."""
        schema = {
            "properties": {
                "env": {"type": "string"},
                "encryption": {
                    "type": "object",
                    "properties": {"type": {"type": "string"}},
                },
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_requires_kms",
                    "when": {"env": {"equals": "prod"}},
                    "then": {"encryption.type": {"equals": "sse-kms"}},
                }
            ],
        }
        request = {"env": "dev", "encryption": {"type": "sse-s3"}}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_conditional_rule_in_condition(self, validator):
        """Should handle 'in' condition in conditional rules."""
        schema = {
            "properties": {"env": {"type": "string"}, "logging": {"type": "boolean"}},
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_staging_requires_logging",
                    "when": {"env": {"in": ["staging", "prod"]}},
                    "then": {
                        "logging": {
                            "equals": True,
                            "error": "Logging required for staging/prod",
                        }
                    },
                }
            ],
        }
        request = {"env": "staging", "logging": False}

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("Logging required" in e.message for e in result.errors)

    # Additional conditional rule operator tests
    def test_conditional_rule_minimum(self, validator):
        """Should enforce minimum value in conditional rules (prod_requires_backup)."""
        schema = {
            "properties": {
                "environment": {"type": "string"},
                "backupRetentionDays": {"type": "integer"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_requires_backup",
                    "when": {"environment": {"equals": "prod"}},
                    "then": {
                        "backupRetentionDays": {
                            "minimum": 14,
                            "error": "Production requires at least 14 days backup retention",
                        }
                    },
                }
            ],
        }
        # Should fail: prod with only 7 days retention
        request = {"environment": "prod", "backupRetentionDays": 7}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("14 days" in e.message for e in result.errors)

    def test_conditional_rule_minimum_passes(self, validator):
        """Should pass when minimum is met."""
        schema = {
            "properties": {
                "environment": {"type": "string"},
                "backupRetentionDays": {"type": "integer"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_requires_backup",
                    "when": {"environment": {"equals": "prod"}},
                    "then": {"backupRetentionDays": {"minimum": 14}},
                }
            ],
        }
        # Should pass: prod with 14+ days retention
        request = {"environment": "prod", "backupRetentionDays": 14}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_conditional_rule_enum(self, validator):
        """Should enforce enum values in conditional rules (dev_max_size)."""
        schema = {
            "properties": {
                "environment": {"type": "string"},
                "size": {"type": "string"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "dev_max_size",
                    "when": {"environment": {"equals": "dev"}},
                    "then": {
                        "size": {
                            "enum": ["small"],
                            "error": "Dev environments limited to small instances",
                        }
                    },
                }
            ],
        }
        # Should fail: dev with large size
        request = {"environment": "dev", "size": "large"}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("small" in e.message for e in result.errors)

    def test_conditional_rule_enum_passes(self, validator):
        """Should pass when value in conditional enum."""
        schema = {
            "properties": {
                "environment": {"type": "string"},
                "size": {"type": "string"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "dev_max_size",
                    "when": {"environment": {"equals": "dev"}},
                    "then": {"size": {"enum": ["small"]}},
                }
            ],
        }
        # Should pass: dev with small size
        request = {"environment": "dev", "size": "small"}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_conditional_rule_greater_than_field(self, validator):
        """Should enforce greater_than_field in conditional rules."""
        schema = {
            "properties": {
                "storageGb": {"type": "integer"},
                "maxStorageGb": {"type": "integer"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "storage_max_must_exceed_allocated",
                    "when": {"maxStorageGb": {"defined": True}},
                    "then": {
                        "maxStorageGb": {
                            "greater_than_field": "storageGb",
                            "error": "Max storage must exceed allocated storage",
                        }
                    },
                }
            ],
        }
        # Should fail: maxStorageGb <= storageGb
        request = {"storageGb": 50, "maxStorageGb": 50}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False
        assert any("exceed" in e.message for e in result.errors)

    def test_conditional_rule_greater_than_field_passes(self, validator):
        """Should pass when greater_than_field is satisfied."""
        schema = {
            "properties": {
                "storageGb": {"type": "integer"},
                "maxStorageGb": {"type": "integer"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "storage_max_must_exceed_allocated",
                    "when": {"maxStorageGb": {"defined": True}},
                    "then": {"maxStorageGb": {"greater_than_field": "storageGb"}},
                }
            ],
        }
        # Should pass: maxStorageGb > storageGb
        request = {"storageGb": 50, "maxStorageGb": 100}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_conditional_rule_defined_condition(self, validator):
        """Should handle 'defined' in when conditions."""
        schema = {
            "properties": {
                "maxStorageGb": {"type": "integer"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "when_max_defined",
                    "when": {"maxStorageGb": {"defined": True}},
                    "then": {
                        "maxStorageGb": {
                            "minimum": 50,
                            "error": "When defined, maxStorageGb must be >= 50",
                        }
                    },
                }
            ],
        }
        # Should fail: maxStorageGb defined but < 50
        request = {"maxStorageGb": 30}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is False

    def test_conditional_rule_defined_false_skips(self, validator):
        """Should skip rule when field not defined and condition requires defined."""
        schema = {
            "properties": {
                "maxStorageGb": {"type": "integer"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "when_max_defined",
                    "when": {"maxStorageGb": {"defined": True}},
                    "then": {"maxStorageGb": {"minimum": 50}},
                }
            ],
        }
        # Should pass: maxStorageGb not defined, rule doesn't apply
        request = {}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True

    def test_conditional_rule_recommended_warning(self, validator):
        """Should generate warning for recommended fields."""
        schema = {
            "properties": {
                "environment": {"type": "string"},
                "multiAz": {"type": "boolean"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_requires_multi_az",
                    "when": {"environment": {"equals": "prod"}},
                    "then": {
                        "multiAz": {
                            "recommended": True,
                            "warning": "Production databases without Multi-AZ may have availability gaps",
                        }
                    },
                }
            ],
        }
        # Should pass but with warning: prod without multiAz
        request = {"environment": "prod", "multiAz": False}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        # Recommended doesn't cause failure, but generates warning
        assert result.valid is True
        assert len(result.warnings) > 0
        assert any("Multi-AZ" in w.message for w in result.warnings)

    def test_conditional_rule_recommended_no_warning_when_set(self, validator):
        """Should not generate warning when recommended field is set."""
        schema = {
            "properties": {
                "environment": {"type": "string"},
                "multiAz": {"type": "boolean"},
            },
            "required": [],
            "conditional_rules": [
                {
                    "name": "prod_requires_multi_az",
                    "when": {"environment": {"equals": "prod"}},
                    "then": {
                        "multiAz": {
                            "recommended": True,
                            "warning": "Production databases without Multi-AZ may have availability gaps",
                        }
                    },
                }
            ],
        }
        # Should pass without warning: prod with multiAz enabled
        request = {"environment": "prod", "multiAz": True}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True
        assert len(result.warnings) == 0

    def test_rds_schema_prod_backup_validation(self, validator):
        """Integration test: RDS schema prod_requires_backup rule."""
        # Simulate the actual RDS schema rule
        schema = {
            "properties": {
                "id": {"type": "string", "pattern": "^RDS-[0-9]{4}$"},
                "environment": {"type": "string"},
                "backupRetentionDays": {"type": "integer", "minimum": 1, "maximum": 35},
            },
            "required": ["id", "environment"],
            "conditional_rules": [
                {
                    "name": "prod_requires_backup",
                    "when": {"environment": {"equals": "prod"}},
                    "then": {"backupRetentionDays": {"minimum": 14}},
                }
            ],
        }

        # Invalid: prod with 7 days
        request = {"id": "RDS-0001", "environment": "prod", "backupRetentionDays": 7}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")
        assert result.valid is False
        assert any("backupRetentionDays" in e.path for e in result.errors)

        # Valid: prod with 14 days
        request = {"id": "RDS-0001", "environment": "prod", "backupRetentionDays": 14}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")
        assert result.valid is True

        # Valid: dev with 7 days (rule doesn't apply)
        request = {"id": "RDS-0001", "environment": "dev", "backupRetentionDays": 7}
        result = validator.validate(request, schema, "test.yaml", "schema.yaml")
        assert result.valid is True

    # Request flattening tests
    def test_flatten_request_with_spec(self, validator):
        """Should flatten request with spec section."""
        schema = {
            "properties": {
                "id": {"type": "string"},
                "bucketName": {"type": "string"},
            },
            "required": ["id", "bucketName"],
        }
        request = {
            "id": "S3-0001",
            "spec": {"bucketName": "my-bucket"},
        }

        result = validator.validate(request, schema, "test.yaml", "schema.yaml")

        assert result.valid is True


class TestFindSchemaForRequest:
    """Tests for find_schema_for_request function."""

    def test_find_s3_schema(self, tmp_path):
        """Should find s3.schema.yaml for S3- prefix."""
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        (schema_dir / "s3.schema.yaml").write_text("id: test")

        request_file = tmp_path / "S3-0001.yaml"
        request_file.write_text("id: S3-0001")

        schema_path, status = find_schema_for_request(request_file, schema_dir)

        assert status == "found"
        assert schema_path == schema_dir / "s3.schema.yaml"

    def test_find_eks_schema(self, tmp_path):
        """Should find eks.schema.yaml for EKS- prefix."""
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        (schema_dir / "eks.schema.yaml").write_text("id: test")

        request_file = tmp_path / "EKS-0001.yaml"
        request_file.write_text("id: EKS-0001")

        schema_path, status = find_schema_for_request(request_file, schema_dir)

        assert status == "found"
        assert schema_path == schema_dir / "eks.schema.yaml"

    def test_skip_secret_prefix(self, tmp_path):
        """Should skip SECRET- prefix gracefully."""
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()

        request_file = tmp_path / "SECRET-0001.yaml"
        request_file.write_text("id: SECRET-0001")

        schema_path, status = find_schema_for_request(request_file, schema_dir)

        assert status == "skip"
        assert schema_path is None

    def test_unknown_prefix(self, tmp_path):
        """Should return unknown for unrecognized prefix."""
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()

        request_file = tmp_path / "UNKNOWN-0001.yaml"
        request_file.write_text("id: UNKNOWN-0001")

        schema_path, status = find_schema_for_request(request_file, schema_dir)

        assert status == "unknown"
        assert schema_path is None
