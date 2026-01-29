"""
Unit tests for RAG query CLI.

Tests the CLI module's ability to:
- Parse command-line arguments
- Query the retriever with user input
- Format and display results with citations
- Support filtering and output options

Per GOV-0017: "Nothing that generates infrastructure, parses config, or emits
scaffolds may change without tests."

References:
- GOV-0017: TDD and Determinism Policy
- ADR-0186: LlamaIndex as Retrieval Layer
- PRD-0008: Governance RAG Pipeline
"""

import pytest
from unittest.mock import MagicMock, patch
import json

# Import will fail until cli.py is implemented (RED phase)
from scripts.rag.cli import (
    parse_args,
    parse_filter_string,
    run_query,
    format_results,
    main,
    OutputFormat,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_retriever():
    """Create a mock GovernanceRetriever."""
    with patch("scripts.rag.cli.GovernanceRetriever") as MockRetriever:
        mock_instance = MagicMock()
        MockRetriever.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_results():
    """Create sample retrieval results."""
    from scripts.rag.retriever import RetrievalResult

    return [
        RetrievalResult(
            id="GOV-0017_0",
            text="## Purpose\n\nThis policy defines testing requirements.",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Purpose",
                "file_path": "docs/10-governance/policies/GOV-0017.md",
            },
            score=0.1,
        ),
        RetrievalResult(
            id="GOV-0017_1",
            text="## Core Principle\n\nTests are executable contracts.",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Core Principle",
                "file_path": "docs/10-governance/policies/GOV-0017.md",
            },
            score=0.3,
        ),
    ]


# ---------------------------------------------------------------------------
# Tests: Argument Parsing
# ---------------------------------------------------------------------------


class TestArgumentParsing:
    """Tests for CLI argument parsing."""

    def test_parse_query_argument(self):
        """parse_args must accept a query string."""
        args = parse_args(["query", "What are TDD requirements?"])

        assert args.command == "query"
        assert args.query == "What are TDD requirements?"

    def test_parse_top_k_option(self):
        """parse_args must accept --top-k option."""
        args = parse_args(["query", "test query", "--top-k", "10"])

        assert args.top_k == 10

    def test_parse_top_k_default(self):
        """parse_args must default top_k to 5."""
        args = parse_args(["query", "test query"])

        assert args.top_k == 5

    def test_parse_filter_option(self):
        """parse_args must accept --filter option."""
        args = parse_args(["query", "test query", "--filter", "doc_type=governance"])

        assert args.filter == "doc_type=governance"

    def test_parse_format_option_json(self):
        """parse_args must accept --format json option."""
        args = parse_args(["query", "test query", "--format", "json"])

        assert args.format == "json"

    def test_parse_format_option_text(self):
        """parse_args must accept --format text option."""
        args = parse_args(["query", "test query", "--format", "text"])

        assert args.format == "text"

    def test_parse_format_default(self):
        """parse_args must default format to text."""
        args = parse_args(["query", "test query"])

        assert args.format == "text"

    def test_parse_collection_option(self):
        """parse_args must accept --collection option."""
        args = parse_args(["query", "test query", "--collection", "my_docs"])

        assert args.collection == "my_docs"

    def test_parse_verbose_flag(self):
        """parse_args must accept --verbose flag."""
        args = parse_args(["query", "test query", "--verbose"])

        assert args.verbose is True

    def test_parse_no_citations_flag(self):
        """parse_args must accept --no-citations flag."""
        args = parse_args(["query", "test query", "--no-citations"])

        assert args.no_citations is True


# ---------------------------------------------------------------------------
# Tests: Query Execution
# ---------------------------------------------------------------------------


class TestQueryExecution:
    """Tests for query execution."""

    def test_run_query_calls_retriever(self, mock_retriever, sample_results):
        """run_query must call the retriever with the query."""
        mock_retriever.query.return_value = sample_results

        run_query("What are TDD requirements?", retriever=mock_retriever)

        mock_retriever.query.assert_called_once()
        call_args = mock_retriever.query.call_args
        assert call_args[0][0] == "What are TDD requirements?"

    def test_run_query_passes_top_k(self, mock_retriever, sample_results):
        """run_query must pass top_k to retriever."""
        mock_retriever.query.return_value = sample_results

        run_query("test query", retriever=mock_retriever, top_k=10)

        call_args = mock_retriever.query.call_args
        assert call_args[1]["top_k"] == 10

    def test_run_query_passes_filters(self, mock_retriever, sample_results):
        """run_query must pass filters to retriever."""
        mock_retriever.query.return_value = sample_results

        run_query(
            "test query",
            retriever=mock_retriever,
            filters={"doc_type": "governance"},
        )

        call_args = mock_retriever.query.call_args
        assert call_args[1]["filters"] == {"doc_type": "governance"}

    def test_run_query_returns_results(self, mock_retriever, sample_results):
        """run_query must return retrieval results."""
        mock_retriever.query.return_value = sample_results

        results = run_query("test query", retriever=mock_retriever)

        assert results == sample_results


# ---------------------------------------------------------------------------
# Tests: Output Formatting
# ---------------------------------------------------------------------------


class TestOutputFormatting:
    """Tests for result formatting."""

    def test_format_results_text_includes_content(self, sample_results):
        """format_results text mode must include chunk content."""
        output = format_results(sample_results, format_type=OutputFormat.TEXT)

        assert "This policy defines testing requirements" in output

    def test_format_results_text_includes_citations(self, sample_results):
        """format_results text mode must include citations."""
        output = format_results(
            sample_results, format_type=OutputFormat.TEXT, include_citations=True
        )

        assert "GOV-0017" in output
        assert "docs/10-governance/policies/GOV-0017.md" in output

    def test_format_results_text_no_citations(self, sample_results):
        """format_results text mode can exclude citations."""
        output = format_results(
            sample_results, format_type=OutputFormat.TEXT, include_citations=False
        )

        # Content should be present
        assert "This policy defines testing requirements" in output

    def test_format_results_json_valid(self, sample_results):
        """format_results json mode must produce valid JSON."""
        output = format_results(sample_results, format_type=OutputFormat.JSON)

        parsed = json.loads(output)
        assert isinstance(parsed, dict)
        assert "results" in parsed

    def test_format_results_json_structure(self, sample_results):
        """format_results json mode must include expected fields."""
        output = format_results(sample_results, format_type=OutputFormat.JSON)

        parsed = json.loads(output)
        results = parsed["results"]
        assert len(results) == 2
        assert "id" in results[0]
        assert "text" in results[0]
        assert "metadata" in results[0]
        assert "score" in results[0]

    def test_format_results_json_includes_citations(self, sample_results):
        """format_results json mode must include citations when requested."""
        output = format_results(
            sample_results, format_type=OutputFormat.JSON, include_citations=True
        )

        parsed = json.loads(output)
        assert "citation" in parsed["results"][0]

    def test_format_results_empty_list(self):
        """format_results must handle empty results."""
        output = format_results([], format_type=OutputFormat.TEXT)

        assert "No results found" in output or output.strip() == ""


# ---------------------------------------------------------------------------
# Tests: Filter Parsing
# ---------------------------------------------------------------------------


class TestFilterParsing:
    """Tests for filter string parsing."""

    def test_parse_single_filter(self):
        """CLI must parse single key=value filter."""
        args = parse_args(["query", "test", "--filter", "doc_type=governance"])

        # Filter should be parseable
        assert "=" in args.filter

    def test_run_query_parses_filter_string(self, mock_retriever, sample_results):
        """run_query must parse filter string to dict."""
        mock_retriever.query.return_value = sample_results

        run_query(
            "test query",
            retriever=mock_retriever,
            filter_string="doc_id=GOV-0017",
        )

        call_args = mock_retriever.query.call_args
        filters = call_args[1].get("filters")
        assert filters is not None
        assert filters.get("doc_id") == "GOV-0017"

    def test_parse_filter_string_valid(self):
        """parse_filter_string must parse key=value format."""
        result = parse_filter_string("doc_type=governance")

        assert result == {"doc_type": "governance"}

    def test_parse_filter_string_with_spaces(self):
        """parse_filter_string must strip whitespace."""
        result = parse_filter_string("  doc_id = GOV-0017  ")

        assert result == {"doc_id": "GOV-0017"}

    def test_parse_filter_string_none(self):
        """parse_filter_string must return None for None input."""
        result = parse_filter_string(None)

        assert result is None

    def test_parse_filter_string_empty(self):
        """parse_filter_string must return None for empty string."""
        result = parse_filter_string("")

        assert result is None

    def test_parse_filter_string_no_equals(self):
        """parse_filter_string must return None if no equals sign."""
        result = parse_filter_string("invalid_filter")

        assert result is None

    def test_parse_filter_string_value_with_equals(self):
        """parse_filter_string must handle values containing equals."""
        result = parse_filter_string("key=value=with=equals")

        assert result == {"key": "value=with=equals"}


# ---------------------------------------------------------------------------
# Tests: Main Entry Point
# ---------------------------------------------------------------------------


class TestMainEntryPoint:
    """Tests for the main CLI entry point."""

    def test_main_runs_query(self, mock_retriever, sample_results, capsys):
        """main must execute query and print results."""
        mock_retriever.query.return_value = sample_results

        with patch("scripts.rag.cli.GovernanceRetriever", return_value=mock_retriever):
            exit_code = main(["query", "What are TDD requirements?"])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "TDD" in captured.out or "testing" in captured.out.lower()

    def test_main_handles_empty_results(self, mock_retriever, capsys):
        """main must handle empty results gracefully."""
        mock_retriever.query.return_value = []

        with patch("scripts.rag.cli.GovernanceRetriever", return_value=mock_retriever):
            exit_code = main(["query", "nonexistent query"])

        assert exit_code == 0

    def test_main_json_output(self, mock_retriever, sample_results, capsys):
        """main must output JSON when --format json is specified."""
        mock_retriever.query.return_value = sample_results

        with patch("scripts.rag.cli.GovernanceRetriever", return_value=mock_retriever):
            main(["query", "test", "--format", "json"])

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "results" in parsed

    def test_main_verbose_output(self, mock_retriever, sample_results, capsys):
        """main must show additional info when --verbose is set."""
        mock_retriever.query.return_value = sample_results

        with patch("scripts.rag.cli.GovernanceRetriever", return_value=mock_retriever):
            main(["query", "test", "--verbose"])

        captured = capsys.readouterr()
        # Verbose should include query info or timing
        assert len(captured.out) > 0


# ---------------------------------------------------------------------------
# Tests: Error Handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for error handling."""

    def test_main_handles_missing_query(self, capsys):
        """main must handle missing query argument."""
        exit_code = main(["query"])

        # Should return error code or print usage
        assert exit_code != 0 or "usage" in capsys.readouterr().err.lower()

    def test_main_handles_invalid_format(self, capsys):
        """main must handle invalid format option."""
        exit_code = main(["query", "test", "--format", "invalid"])

        assert exit_code != 0

    def test_main_handles_retriever_error(self, mock_retriever, capsys):
        """main must handle retriever errors gracefully."""
        mock_retriever.query.side_effect = Exception("Connection failed")

        with patch("scripts.rag.cli.GovernanceRetriever", return_value=mock_retriever):
            exit_code = main(["query", "test"])

        assert exit_code != 0
        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or "failed" in captured.err.lower()


# ---------------------------------------------------------------------------
# Tests: OutputFormat Enum
# ---------------------------------------------------------------------------


class TestOutputFormatEnum:
    """Tests for OutputFormat enum."""

    def test_output_format_text_exists(self):
        """OutputFormat must have TEXT option."""
        assert OutputFormat.TEXT is not None

    def test_output_format_json_exists(self):
        """OutputFormat must have JSON option."""
        assert OutputFormat.JSON is not None
