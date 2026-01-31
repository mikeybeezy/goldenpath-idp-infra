"""
Pytest configuration for unit tests.

Auto-skips RAG tests when ML dependencies are not installed.
This allows CI to run fast with lightweight deps while still
supporting full test runs locally with requirements-dev.txt.
"""

import importlib.util

import pytest

# Check for RAG dependencies availability using find_spec (avoids F401 lint warning)
HAS_RAG_DEPS = (
    importlib.util.find_spec("chromadb") is not None
    and importlib.util.find_spec("llama_index") is not None
)

# RAG test files that require ML dependencies
RAG_TEST_FILES = {
    "test_chunker.py",
    "test_indexer.py",
    "test_retriever.py",
    "test_hybrid_retriever.py",
    "test_loader.py",
    "test_scope.py",
    "test_index_build.py",
    "test_index_metadata.py",
    "test_graph_ingest.py",
    "test_llm_synthesis.py",
    "test_ragas_evaluate.py",
    "test_ragas_baseline.py",
    "test_query_cli.py",
}


def pytest_collection_modifyitems(config, items):
    """Skip RAG tests when dependencies are not installed."""
    if HAS_RAG_DEPS:
        return  # All deps available, run everything

    skip_rag = pytest.mark.skip(
        reason="RAG dependencies not installed (chromadb, llama-index)"
    )

    for item in items:
        # Get the test file name
        test_file = (
            item.fspath.basename
            if hasattr(item.fspath, "basename")
            else str(item.fspath).split("/")[-1]
        )

        if test_file in RAG_TEST_FILES:
            item.add_marker(skip_rag)
