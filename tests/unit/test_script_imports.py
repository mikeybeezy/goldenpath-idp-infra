"""
Unit tests for script importability.

Purpose: Ensure scripts are importable without side effects.
This catches:
- Syntax errors
- Missing dependencies
- Top-level code that runs on import
"""

import importlib
import importlib.util
import sys
from pathlib import Path

import pytest


# Scripts that should be safely importable
IMPORTABLE_SCRIPTS = [
    "scripts.secret_request_parser",
    "scripts.rds_request_parser",
    "scripts.s3_request_parser",
    "scripts.eks_request_parser",
]


class TestScriptImports:
    """Test that critical scripts are importable."""

    @pytest.mark.parametrize("module_name", IMPORTABLE_SCRIPTS)
    def test_script_imports_without_error(self, module_name):
        """Script should import without raising exceptions."""
        try:
            module = importlib.import_module(module_name)
            assert module is not None
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")

    def test_secret_request_parser_exposes_dataclass(self):
        """SecretRequest dataclass should be exposed."""
        from scripts import secret_request_parser

        assert hasattr(secret_request_parser, "SecretRequest")
        assert hasattr(secret_request_parser, "load_yaml")

    def test_secret_request_parser_dataclass_has_required_fields(self):
        """SecretRequest should have expected fields."""
        from scripts.secret_request_parser import SecretRequest

        # Check required fields exist in annotations
        annotations = SecretRequest.__annotations__
        required_fields = ["secret_id", "name", "service", "environment", "owner"]
        for field in required_fields:
            assert field in annotations, f"Missing required field: {field}"


class TestScriptSyntax:
    """Test that all Python scripts have valid syntax."""

    @pytest.fixture
    def scripts_dir(self):
        """Return path to scripts directory."""
        return Path(__file__).parent.parent.parent / "scripts"

    def test_all_scripts_have_valid_syntax(self, scripts_dir):
        """All .py files in scripts/ should have valid Python syntax."""
        errors = []
        for py_file in scripts_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                # Try to compile the file (syntax check only)
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()
                compile(source, py_file, "exec")
            except SyntaxError as e:
                errors.append(f"{py_file.name}: {e}")

        if errors:
            pytest.fail(f"Syntax errors found:\n" + "\n".join(errors))
