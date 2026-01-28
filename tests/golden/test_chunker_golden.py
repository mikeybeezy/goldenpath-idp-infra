"""
Golden output tests for the RAG chunker.

These tests verify that chunking output remains deterministic.

To update golden files (with human approval):
    pytest tests/golden/ --update-golden
"""

import json

from scripts.rag.chunker import chunk_document
from scripts.rag.loader import load_governance_document


def test_gov_0017_chunks_match_golden(assert_matches_golden):
    """GOV-0017 sample chunks should match the golden snapshot."""
    input_path = "tests/golden/fixtures/inputs/GOV-0017-sample.md"
    doc = load_governance_document(input_path)
    chunks = chunk_document(doc)

    payload = [{"text": c.text, "metadata": c.metadata} for c in chunks]
    actual = json.dumps(payload, indent=2, sort_keys=True)

    assert_matches_golden(actual, "chunks/GOV-0017/chunks.json")
