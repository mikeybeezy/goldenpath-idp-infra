"""
Golden tests for the RAG answer contract.

These tests enforce the answer schema and abstention rules.
Per GOV-0017, golden tests are Tier 2 guardrails against drift.
"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "metadata"
    / "answer_contract.schema.json"
)


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


class TestAnswerContractGolden:
    """Validate golden answer samples against the schema."""

    def test_valid_answer_matches_schema(self, load_input):
        schema = _load_schema()
        data = json.loads(load_input("ANSWER-CONTRACT-valid.json"))
        Draft202012Validator(schema).validate(data)

    def test_invalid_answer_rejected(self, load_input):
        schema = _load_schema()
        data = json.loads(load_input("ANSWER-CONTRACT-invalid.json"))
        with pytest.raises(ValidationError):
            Draft202012Validator(schema).validate(data)
