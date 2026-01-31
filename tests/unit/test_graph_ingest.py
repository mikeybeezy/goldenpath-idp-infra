"""
Unit tests for graph ingestion.

Tests the graph_ingest module's ability to:
- Upsert document nodes from governance metadata
- Create RELATES_TO edges from frontmatter
- Handle missing IDs and malformed relates_to
"""

from unittest.mock import MagicMock

from scripts.rag.graph_ingest import ingest_documents
from scripts.rag.loader import GovernanceDocument


def _make_doc(doc_id: str, relates_to=None) -> GovernanceDocument:
    metadata = {
        "id": doc_id,
        "title": "Test Doc",
        "type": "governance",
        "domain": "platform-core",
        "lifecycle": "active",
        "status": "active",
        "file_path": f"docs/{doc_id}.md",
        "relates_to": relates_to,
    }
    return GovernanceDocument(content="# Title", metadata=metadata, source_path="")


class TestGraphIngest:
    def test_ingest_upserts_documents(self):
        client = MagicMock()
        docs = [_make_doc("DOC-001"), _make_doc("DOC-002")]

        counts = ingest_documents(docs, client)

        assert counts["documents"] == 2
        assert client.upsert_document.call_count == 2

    def test_ingest_creates_relationships(self):
        client = MagicMock()
        docs = [_make_doc("DOC-001", relates_to=["DOC-002", "DOC-003"])]

        ingest_documents(docs, client)

        assert client.relate_documents.call_count == 2
        client.relate_documents.assert_any_call("DOC-001", "DOC-002", "RELATES_TO")
        client.relate_documents.assert_any_call("DOC-001", "DOC-003", "RELATES_TO")

    def test_ingest_handles_string_relates_to(self):
        client = MagicMock()
        docs = [_make_doc("DOC-001", relates_to="DOC-002")]

        ingest_documents(docs, client)

        client.relate_documents.assert_called_once_with(
            "DOC-001", "DOC-002", "RELATES_TO"
        )

    def test_ingest_skips_missing_id(self):
        client = MagicMock()
        docs = [_make_doc(None), _make_doc("DOC-002")]

        counts = ingest_documents(docs, client)

        assert counts["documents"] == 1
        client.upsert_document.assert_called_once()
