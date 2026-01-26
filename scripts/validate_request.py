#!/usr/bin/env python3
"""
Bespoke Schema Validator for GoldenPath Request Contracts.

Validates request fixtures against bespoke GoldenPath schemas that include:
- Structure validation (type, pattern, enum, required)
- enum_from references (loads from schemas/metadata/enums.yaml)
- conditional_rules evaluation
- Detailed error reporting

Usage:
    # Validate single request
    python3 scripts/validate_request.py \
        --schema schemas/requests/s3.schema.yaml \
        --request tests/golden/fixtures/inputs/S3-0001.yaml

    # Auto-match requests to schemas by prefix
    python3 scripts/validate_request.py \
        --schema-dir schemas/requests \
        --request-dir tests/golden/fixtures/inputs \
        --auto-match

    # Output JSON for CI
    python3 scripts/validate_request.py \
        --schema-dir schemas/requests \
        --request-dir tests/golden/fixtures/inputs \
        --auto-match \
        --output json

Reference: EC-0016-bespoke-schema-validator.md
Script ID: SCRIPT-0058
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


@dataclass
class ValidationError:
    """A single validation error."""
    path: str
    message: str
    rule: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"path": self.path, "message": self.message}
        if self.rule:
            result["rule"] = self.rule
        return result


@dataclass
class ValidationResult:
    """Result of validating a request against a schema."""
    request_file: str
    schema_file: str
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_file": self.request_file,
            "schema_file": self.schema_file,
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }


class EnumResolver:
    """Resolves enum_from references from enums.yaml."""

    def __init__(self, enums_path: Path):
        self.enums: Dict[str, List[str]] = {}
        self._load_enums(enums_path)

    def _load_enums(self, path: Path) -> None:
        """Load enums from YAML file."""
        if not path.exists():
            return

        with open(path) as f:
            data = yaml.safe_load(f)

        if not data:
            return

        # Handle flat enums (key: [values])
        for key, value in data.items():
            if isinstance(value, list):
                self.enums[key] = value
            elif isinstance(value, dict):
                # Handle nested enums like security.secret_types
                if "values" in value:
                    self.enums[key] = value["values"]
                else:
                    # Nested dict like security: {secret_types: {values: [...]}}
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, dict) and "values" in subvalue:
                            self.enums[f"{key}.{subkey}"] = subvalue["values"]
                        elif isinstance(subvalue, list):
                            self.enums[f"{key}.{subkey}"] = subvalue

    def resolve(self, enum_from: str) -> Optional[List[str]]:
        """Resolve an enum_from reference to its values."""
        return self.enums.get(enum_from)


class BespokeSchemaValidator:
    """Validates requests against bespoke GoldenPath schemas."""

    def __init__(self, enums_path: Optional[Path] = None):
        self.enum_resolver: Optional[EnumResolver] = None
        if enums_path and enums_path.exists():
            self.enum_resolver = EnumResolver(enums_path)

    def validate(
        self,
        request: Dict[str, Any],
        schema: Dict[str, Any],
        request_file: str,
        schema_file: str,
    ) -> ValidationResult:
        """Validate a request against a schema."""
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        # Get properties and required fields from schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Flatten request if it has spec section
        flat_request = self._flatten_request(request)

        # Validate required fields
        for field_name in required:
            if not self._get_value(flat_request, field_name):
                errors.append(ValidationError(
                    path=field_name,
                    message=f"Required field '{field_name}' is missing",
                ))

        # Validate each property
        for prop_name, prop_schema in properties.items():
            value = self._get_value(flat_request, prop_name)
            if value is not None:
                prop_errors = self._validate_property(
                    value, prop_schema, prop_name
                )
                errors.extend(prop_errors)

        # Validate conditional rules
        conditional_rules = schema.get("conditional_rules", [])
        for rule in conditional_rules:
            rule_errors, rule_warnings = self._validate_conditional_rule(
                flat_request, rule
            )
            errors.extend(rule_errors)
            warnings.extend(rule_warnings)

        return ValidationResult(
            request_file=request_file,
            schema_file=schema_file,
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _flatten_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten a request with spec section to top-level fields."""
        flat = dict(request)

        # Merge spec fields to top level
        if "spec" in request:
            for key, value in request["spec"].items():
                if key not in flat:
                    flat[key] = value

        # Copy metadata fields like id, environment to top level if in root
        for key in ["id", "environment", "owner", "application", "requester"]:
            if key in request and key not in flat:
                flat[key] = request[key]

        return flat

    def _get_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get a value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
            if current is None:
                return None
        return current

    def _validate_property(
        self,
        value: Any,
        prop_schema: Dict[str, Any],
        path: str,
    ) -> List[ValidationError]:
        """Validate a single property value against its schema."""
        errors: List[ValidationError] = []
        prop_type = prop_schema.get("type")

        # Type validation
        if prop_type:
            type_error = self._validate_type(value, prop_type, path)
            if type_error:
                errors.append(type_error)
                return errors  # Skip further validation if type is wrong

        # Pattern validation (for strings)
        pattern = prop_schema.get("pattern")
        if pattern and isinstance(value, str):
            if not re.match(pattern, value):
                errors.append(ValidationError(
                    path=path,
                    message=f"Value '{value}' does not match pattern '{pattern}'",
                ))

        # Enum validation
        enum_values = prop_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(ValidationError(
                path=path,
                message=f"Value '{value}' not in allowed values: {enum_values}",
            ))

        # enum_from validation
        enum_from = prop_schema.get("enum_from")
        if enum_from and self.enum_resolver:
            allowed = self.enum_resolver.resolve(enum_from)
            if allowed and value not in allowed:
                errors.append(ValidationError(
                    path=path,
                    message=f"Value '{value}' not in enum '{enum_from}': {allowed}",
                ))

        # Numeric constraints
        if isinstance(value, (int, float)):
            minimum = prop_schema.get("minimum")
            maximum = prop_schema.get("maximum")
            if minimum is not None and value < minimum:
                errors.append(ValidationError(
                    path=path,
                    message=f"Value {value} is less than minimum {minimum}",
                ))
            if maximum is not None and value > maximum:
                errors.append(ValidationError(
                    path=path,
                    message=f"Value {value} is greater than maximum {maximum}",
                ))

        # String length constraints
        if isinstance(value, str):
            min_length = prop_schema.get("minLength")
            max_length = prop_schema.get("maxLength")
            if min_length is not None and len(value) < min_length:
                errors.append(ValidationError(
                    path=path,
                    message=f"String length {len(value)} is less than minLength {min_length}",
                ))
            if max_length is not None and len(value) > max_length:
                errors.append(ValidationError(
                    path=path,
                    message=f"String length {len(value)} is greater than maxLength {max_length}",
                ))

        # Nested object validation
        if prop_type == "object" and isinstance(value, dict):
            nested_props = prop_schema.get("properties", {})
            nested_required = prop_schema.get("required", [])

            for req_field in nested_required:
                if req_field not in value:
                    errors.append(ValidationError(
                        path=f"{path}.{req_field}",
                        message=f"Required field '{req_field}' is missing in '{path}'",
                    ))

            for nested_name, nested_schema in nested_props.items():
                nested_value = value.get(nested_name)
                if nested_value is not None:
                    nested_errors = self._validate_property(
                        nested_value, nested_schema, f"{path}.{nested_name}"
                    )
                    errors.extend(nested_errors)

        return errors

    def _validate_type(
        self,
        value: Any,
        expected_type: str,
        path: str,
    ) -> Optional[ValidationError]:
        """Validate that a value matches the expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return None  # Unknown type, skip validation

        # Special case: int is also a valid number
        if expected_type == "integer" and isinstance(value, bool):
            return ValidationError(
                path=path,
                message=f"Expected type '{expected_type}' but got boolean",
            )

        if not isinstance(value, expected_python_type):
            actual_type = type(value).__name__
            return ValidationError(
                path=path,
                message=f"Expected type '{expected_type}' but got '{actual_type}'",
            )

        return None

    def _validate_conditional_rule(
        self,
        request: Dict[str, Any],
        rule: Dict[str, Any],
    ) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate a conditional rule against a request."""
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        rule_name = rule.get("name", "unnamed_rule")
        when_conditions = rule.get("when", {})
        then_requirements = rule.get("then", {})

        # Check if the 'when' conditions are met
        if not self._evaluate_conditions(request, when_conditions):
            return errors, warnings  # Rule doesn't apply

        # Validate 'then' requirements
        for field_path, requirement in then_requirements.items():
            if field_path == "approval_required":
                # Handle approval_required specially
                warning_msg = requirement.get("warning")
                error_msg = requirement.get("error")
                if warning_msg:
                    warnings.append(ValidationError(
                        path="approval_required",
                        message=warning_msg,
                        rule=rule_name,
                    ))
                if error_msg:
                    # This is informational for CI, not a validation error
                    warnings.append(ValidationError(
                        path="approval_required",
                        message=error_msg,
                        rule=rule_name,
                    ))
                continue

            value = self._get_value(request, field_path)

            if isinstance(requirement, dict):
                if requirement.get("required"):
                    if value is None:
                        error_msg = requirement.get(
                            "error",
                            f"Field '{field_path}' is required when {rule_name} applies"
                        )
                        errors.append(ValidationError(
                            path=field_path,
                            message=error_msg,
                            rule=rule_name,
                        ))

                if "equals" in requirement:
                    expected = requirement["equals"]
                    if value != expected:
                        error_msg = requirement.get(
                            "error",
                            f"Field '{field_path}' must equal '{expected}' when {rule_name} applies"
                        )
                        errors.append(ValidationError(
                            path=field_path,
                            message=error_msg,
                            rule=rule_name,
                        ))

        return errors, warnings

    def _evaluate_conditions(
        self,
        request: Dict[str, Any],
        conditions: Dict[str, Any],
    ) -> bool:
        """Evaluate if all conditions are met."""
        for field_path, condition in conditions.items():
            value = self._get_value(request, field_path)

            if isinstance(condition, dict):
                if "in" in condition:
                    if value not in condition["in"]:
                        return False
                if "equals" in condition:
                    if value != condition["equals"]:
                        return False
                if "not_equals" in condition:
                    if value == condition["not_equals"]:
                        return False
            else:
                # Direct value comparison
                if value != condition:
                    return False

        return True


def find_schema_for_request(
    request_file: Path,
    schema_dir: Path,
) -> Tuple[Optional[Path], str]:
    """
    Find matching schema for a request file based on prefix.

    Returns:
        (schema_path, status) where status is:
        - "found": Schema exists and was found
        - "skip": Known prefix but no schema yet (skip gracefully)
        - "unknown": Unknown prefix (skip without error)
    """
    # Prefixes with bespoke schemas
    prefix_map = {
        "S3-": "s3.schema.yaml",
        "EKS-": "eks.schema.yaml",
        "RDS-": "rds.schema.yaml",
    }

    # Prefixes that are known but don't have bespoke schemas yet
    # These are skipped without being counted as validation failures
    skip_prefixes = ["SECRET-"]

    filename = request_file.name

    # Check for skip prefixes first
    for prefix in skip_prefixes:
        if filename.startswith(prefix):
            return None, "skip"

    # Check for schema-backed prefixes
    for prefix, schema_name in prefix_map.items():
        if filename.startswith(prefix):
            schema_path = schema_dir / schema_name
            if schema_path.exists():
                return schema_path, "found"
            return None, "skip"  # Schema missing, skip gracefully

    return None, "unknown"


def validate_all(
    schema_dir: Path,
    request_dir: Path,
    enums_path: Path,
) -> Tuple[List[ValidationResult], int]:
    """
    Validate all requests in a directory against their schemas.

    Returns:
        (results, skipped_count) - results for validated files, count of skipped files
    """
    validator = BespokeSchemaValidator(enums_path)
    results: List[ValidationResult] = []
    skipped = 0

    for request_file in request_dir.glob("*.yaml"):
        schema_path, status = find_schema_for_request(request_file, schema_dir)

        if status == "skip":
            skipped += 1
            continue
        elif status == "unknown":
            skipped += 1
            continue
        elif not schema_path:
            results.append(ValidationResult(
                request_file=str(request_file),
                schema_file="",
                valid=False,
                errors=[ValidationError(
                    path="",
                    message=f"No schema found for request {request_file.name}",
                )],
            ))
            continue

        with open(request_file) as f:
            request = yaml.safe_load(f)

        with open(schema_path) as f:
            schema = yaml.safe_load(f)

        result = validator.validate(
            request, schema, str(request_file), str(schema_path)
        )
        results.append(result)

    return results, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Validate request fixtures against bespoke GoldenPath schemas"
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to schema file (for single validation)",
    )
    parser.add_argument(
        "--request",
        type=Path,
        help="Path to request file (for single validation)",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        help="Directory containing schema files",
    )
    parser.add_argument(
        "--request-dir",
        type=Path,
        help="Directory containing request fixtures",
    )
    parser.add_argument(
        "--enums",
        type=Path,
        default=Path("schemas/metadata/enums.yaml"),
        help="Path to enums.yaml file",
    )
    parser.add_argument(
        "--auto-match",
        action="store_true",
        help="Auto-match requests to schemas by prefix",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    results: List[ValidationResult] = []

    if args.schema and args.request:
        # Single file validation
        validator = BespokeSchemaValidator(args.enums)

        with open(args.request) as f:
            request = yaml.safe_load(f)

        with open(args.schema) as f:
            schema = yaml.safe_load(f)

        result = validator.validate(
            request, schema, str(args.request), str(args.schema)
        )
        results.append(result)

    elif args.auto_match and args.schema_dir and args.request_dir:
        # Batch validation with auto-matching
        results, skipped = validate_all(args.schema_dir, args.request_dir, args.enums)

    else:
        parser.error(
            "Either --schema and --request, or --auto-match with --schema-dir and --request-dir required"
        )
        skipped = 0  # For type checker

    # Output results
    if args.output == "json":
        output = {
            "total": len(results),
            "valid": sum(1 for r in results if r.valid),
            "invalid": sum(1 for r in results if not r.valid),
            "skipped": skipped if 'skipped' in dir() else 0,
            "results": [r.to_dict() for r in results],
        }
        print(json.dumps(output, indent=2))
    else:
        total_errors = 0
        for result in results:
            if result.valid:
                print(f"✅ {result.request_file}")
            else:
                print(f"❌ {result.request_file}")
                for error in result.errors:
                    print(f"   {error.path}: {error.message}")
                    total_errors += 1

            for warning in result.warnings:
                print(f"   ⚠️  {warning.path}: {warning.message}")

        print()
        if skipped > 0:
            print(f"ℹ️  Skipped {skipped} file(s) without bespoke schemas")
        if total_errors == 0 and results:
            print(f"OK: {len(results)} request(s) validated successfully")
        elif not results:
            print("WARNING: No requests with bespoke schemas found to validate")
        else:
            print(f"FAILED: {total_errors} validation error(s)")

    # Exit with error code if any validation failed
    if any(not r.valid for r in results):
        sys.exit(1)
    elif not results:
        # No requests to validate - this is now a failure per Codex feedback
        sys.exit(1)


if __name__ == "__main__":
    main()
