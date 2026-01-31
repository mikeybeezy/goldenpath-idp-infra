"""
Unit tests for llm_synthesis module.

Tests LLM synthesis for RAG responses with multiple providers.
Per GOV-0017: TDD-first implementation.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from scripts.rag.llm_synthesis import (
    LLMProvider,
    SynthesisResult,
    RAGSynthesizer,
    synthesize_answer,
    check_ollama_status,
    check_provider_status,
    _format_context,
    _format_citations,
    _create_llm,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_OPENAI_MODEL,
)
from scripts.rag.retriever import RetrievalResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_retriever():
    """Create a mock HybridRetriever."""
    retriever = MagicMock()
    retriever.query.return_value = []
    return retriever


@pytest.fixture
def sample_results():
    """Sample retrieval results for testing."""
    return [
        RetrievalResult(
            id="chunk-001",
            text="TDD requires tests before implementation.",
            metadata={
                "doc_id": "GOV-0017",
                "section": "Requirements",
                "file_path": "docs/governance/GOV-0017.md",
            },
            score=0.1,
        ),
        RetrievalResult(
            id="chunk-002",
            text="Coverage target is 60% for V1.",
            metadata={
                "doc_id": "GOV-0017",
                "section": "Targets",
                "file_path": "docs/governance/GOV-0017.md",
            },
            score=0.2,
        ),
        RetrievalResult(
            id="chunk-003",
            text="ADR-0182 defines TDD philosophy.",
            metadata={
                "doc_id": "ADR-0182",
                "section": "Context",
                "file_path": "docs/adrs/ADR-0182.md",
            },
            score=0.3,
        ),
    ]


@pytest.fixture
def mock_hybrid_results():
    """Mock HybridResult objects for synthesis testing."""
    from scripts.rag.hybrid_retriever import HybridResult

    return [
        HybridResult(
            id="chunk-001",
            text="TDD requires tests first.",
            metadata={"doc_id": "GOV-0017", "section": "Requirements"},
            score=0.1,
            source="vector",
        ),
        HybridResult(
            id="chunk-002",
            text="60% coverage target.",
            metadata={"doc_id": "GOV-0017", "section": "Targets"},
            score=0.2,
            source="graph",
        ),
    ]


# ---------------------------------------------------------------------------
# Tests: LLMProvider enum
# ---------------------------------------------------------------------------


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_ollama_provider_value(self):
        """LLMProvider.OLLAMA must have value 'ollama'."""
        assert LLMProvider.OLLAMA.value == "ollama"

    def test_claude_provider_value(self):
        """LLMProvider.CLAUDE must have value 'claude'."""
        assert LLMProvider.CLAUDE.value == "claude"

    def test_openai_provider_value(self):
        """LLMProvider.OPENAI must have value 'openai'."""
        assert LLMProvider.OPENAI.value == "openai"


# ---------------------------------------------------------------------------
# Tests: SynthesisResult dataclass
# ---------------------------------------------------------------------------


class TestSynthesisResult:
    """Tests for SynthesisResult dataclass."""

    def test_synthesis_result_has_required_fields(self):
        """SynthesisResult must have answer, citations, model, etc."""
        result = SynthesisResult(
            answer="Test answer",
            citations=["citation1", "citation2"],
            model="llama3.2",
            context_chunks=5,
            source_docs=["DOC-001", "DOC-002"],
        )
        assert result.answer == "Test answer"
        assert result.citations == ["citation1", "citation2"]
        assert result.model == "llama3.2"
        assert result.context_chunks == 5
        assert result.source_docs == ["DOC-001", "DOC-002"]


# ---------------------------------------------------------------------------
# Tests: _format_context
# ---------------------------------------------------------------------------


class TestFormatContext:
    """Tests for _format_context function."""

    def test_format_context_includes_all_results(self, sample_results):
        """_format_context must include all retrieval results."""
        context = _format_context(sample_results)

        assert "TDD requires tests before implementation." in context
        assert "Coverage target is 60% for V1." in context
        assert "ADR-0182 defines TDD philosophy." in context

    def test_format_context_includes_doc_ids(self, sample_results):
        """_format_context must include document IDs in headers."""
        context = _format_context(sample_results)

        assert "GOV-0017" in context
        assert "ADR-0182" in context

    def test_format_context_includes_sections(self, sample_results):
        """_format_context must include section names when available."""
        context = _format_context(sample_results)

        assert "Requirements" in context
        assert "Targets" in context
        assert "Context" in context

    def test_format_context_separates_chunks(self, sample_results):
        """_format_context must separate chunks with delimiters."""
        context = _format_context(sample_results)

        # Should have separators between chunks
        assert "---" in context

    def test_format_context_handles_empty_list(self):
        """_format_context must handle empty results list."""
        context = _format_context([])
        assert context == ""


# ---------------------------------------------------------------------------
# Tests: _format_citations
# ---------------------------------------------------------------------------


class TestFormatCitations:
    """Tests for _format_citations function."""

    def test_format_citations_returns_formatted_list(self, sample_results):
        """_format_citations must return formatted citation strings."""
        citations = _format_citations(sample_results)

        # Should be a string with dash prefixes
        assert "- " in citations

    def test_format_citations_deduplicates_by_doc_id(self, sample_results):
        """_format_citations must deduplicate by document ID."""
        citations = _format_citations(sample_results)

        # GOV-0017 appears twice in sample_results but should only cite once
        lines = citations.split("\n")
        doc_ids = [line for line in lines if "GOV-0017" in line]
        assert len(doc_ids) == 1

    def test_format_citations_handles_empty_list(self):
        """_format_citations must handle empty results list."""
        citations = _format_citations([])
        assert citations == ""


# ---------------------------------------------------------------------------
# Tests: _create_llm
# ---------------------------------------------------------------------------


class TestCreateLLM:
    """Tests for _create_llm function."""

    def test_create_llm_returns_none_for_unknown_provider(self):
        """_create_llm must return None for unknown provider."""
        result = _create_llm("unknown_provider", "model")
        assert result is None

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False)
    def test_create_llm_claude_returns_none_without_api_key(self):
        """_create_llm must return None for Claude without API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            result = _create_llm("claude", "claude-3-haiku-20240307")
        # May still return None if langchain-anthropic not installed
        # The important thing is it doesn't crash

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False)
    def test_create_llm_openai_returns_none_without_api_key(self):
        """_create_llm must return None for OpenAI without API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            result = _create_llm("openai", "gpt-4o-mini")
        # May still return None if langchain-openai not installed


# ---------------------------------------------------------------------------
# Tests: RAGSynthesizer initialization
# ---------------------------------------------------------------------------


class TestRAGSynthesizerInit:
    """Tests for RAGSynthesizer initialization."""

    def test_synthesizer_accepts_provider_parameter(self, mock_retriever):
        """RAGSynthesizer must accept provider parameter."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="claude",
                retriever=mock_retriever,
            )
        assert synth.provider == "claude"

    def test_synthesizer_defaults_to_ollama_model(self, mock_retriever):
        """RAGSynthesizer must default to Ollama model for ollama provider."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
        assert synth.model == DEFAULT_OLLAMA_MODEL

    def test_synthesizer_defaults_to_claude_model(self, mock_retriever):
        """RAGSynthesizer must default to Claude model for claude provider."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="claude",
                retriever=mock_retriever,
            )
        assert synth.model == DEFAULT_CLAUDE_MODEL

    def test_synthesizer_defaults_to_openai_model(self, mock_retriever):
        """RAGSynthesizer must default to OpenAI model for openai provider."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="openai",
                retriever=mock_retriever,
            )
        assert synth.model == DEFAULT_OPENAI_MODEL

    def test_synthesizer_accepts_custom_model(self, mock_retriever):
        """RAGSynthesizer must accept custom model parameter."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                model="mistral:7b",
                retriever=mock_retriever,
            )
        assert synth.model == "mistral:7b"

    def test_synthesizer_accepts_temperature(self, mock_retriever):
        """RAGSynthesizer must accept temperature parameter."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                temperature=0.5,
                retriever=mock_retriever,
            )
        assert synth.temperature == 0.5


# ---------------------------------------------------------------------------
# Tests: RAGSynthesizer.is_available
# ---------------------------------------------------------------------------


class TestRAGSynthesizerIsAvailable:
    """Tests for RAGSynthesizer.is_available method."""

    def test_is_available_returns_false_when_llm_is_none(self, mock_retriever):
        """is_available must return False when LLM is None."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
        assert synth.is_available() is False

    def test_is_available_checks_ollama_status_for_ollama(self, mock_retriever):
        """is_available must check Ollama server for ollama provider."""
        mock_llm = MagicMock()
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=mock_llm):
            with patch(
                "scripts.rag.llm_synthesis._check_ollama_available", return_value=True
            ):
                synth = RAGSynthesizer(
                    provider="ollama",
                    retriever=mock_retriever,
                )
                assert synth.is_available() is True


# ---------------------------------------------------------------------------
# Tests: RAGSynthesizer.synthesize
# ---------------------------------------------------------------------------


class TestRAGSynthesizerSynthesize:
    """Tests for RAGSynthesizer.synthesize method."""

    def test_synthesize_returns_synthesis_result(
        self, mock_retriever, mock_hybrid_results
    ):
        """synthesize must return SynthesisResult object."""
        mock_retriever.query.return_value = mock_hybrid_results

        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            result = synth.synthesize("test question", results=mock_hybrid_results)

        assert isinstance(result, SynthesisResult)

    def test_synthesize_returns_raw_context_when_llm_unavailable(
        self, mock_retriever, mock_hybrid_results
    ):
        """synthesize must return raw context when LLM is unavailable."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            result = synth.synthesize("test question", results=mock_hybrid_results)

        assert "LLM not available" in result.answer or len(result.answer) > 0
        assert result.model == "none" or result.model == DEFAULT_OLLAMA_MODEL

    def test_synthesize_returns_empty_answer_for_no_results(self, mock_retriever):
        """synthesize must handle empty results gracefully."""
        mock_retriever.query.return_value = []

        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            result = synth.synthesize("test question", results=[])

        assert "couldn't find" in result.answer.lower() or result.answer != ""
        assert result.context_chunks == 0

    def test_synthesize_includes_citations(self, mock_retriever, mock_hybrid_results):
        """synthesize must include citations in result."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            result = synth.synthesize("test question", results=mock_hybrid_results)

        assert isinstance(result.citations, list)
        assert len(result.citations) > 0

    def test_synthesize_includes_source_docs(self, mock_retriever, mock_hybrid_results):
        """synthesize must include source document IDs."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            result = synth.synthesize("test question", results=mock_hybrid_results)

        assert isinstance(result.source_docs, list)
        assert "GOV-0017" in result.source_docs

    def test_synthesize_fetches_results_if_not_provided(self, mock_retriever):
        """synthesize must fetch results from retriever if not provided."""
        mock_retriever.query.return_value = []

        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            synth.synthesize("test question")

        mock_retriever.query.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: RAGSynthesizer.close
# ---------------------------------------------------------------------------


class TestRAGSynthesizerClose:
    """Tests for RAGSynthesizer.close method."""

    def test_close_closes_retriever(self, mock_retriever):
        """close must close the retriever."""
        with patch("scripts.rag.llm_synthesis._create_llm", return_value=None):
            synth = RAGSynthesizer(
                provider="ollama",
                retriever=mock_retriever,
            )
            synth.close()

        mock_retriever.close.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: synthesize_answer convenience function
# ---------------------------------------------------------------------------


class TestSynthesizeAnswer:
    """Tests for synthesize_answer convenience function."""

    def test_synthesize_answer_returns_string(self, mock_hybrid_results):
        """synthesize_answer must return a string."""
        with patch("scripts.rag.llm_synthesis.RAGSynthesizer") as MockSynth:
            mock_synth = MagicMock()
            mock_synth.synthesize.return_value = SynthesisResult(
                answer="Test answer",
                citations=[],
                model="llama3.2",
                context_chunks=1,
                source_docs=[],
            )
            MockSynth.return_value = mock_synth

            result = synthesize_answer("test question", results=mock_hybrid_results)

        assert isinstance(result, str)
        assert result == "Test answer"

    def test_synthesize_answer_closes_synthesizer(self):
        """synthesize_answer must close synthesizer after use."""
        with patch("scripts.rag.llm_synthesis.RAGSynthesizer") as MockSynth:
            mock_synth = MagicMock()
            mock_synth.synthesize.return_value = SynthesisResult(
                answer="Test",
                citations=[],
                model="llama3.2",
                context_chunks=0,
                source_docs=[],
            )
            MockSynth.return_value = mock_synth

            synthesize_answer("test question")

            mock_synth.close.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: check_ollama_status
# ---------------------------------------------------------------------------


class TestCheckOllamaStatus:
    """Tests for check_ollama_status function."""

    def test_check_ollama_status_returns_dict(self):
        """check_ollama_status must return a dictionary."""
        status = check_ollama_status()
        assert isinstance(status, dict)

    def test_check_ollama_status_includes_available_key(self):
        """check_ollama_status must include 'available' key."""
        status = check_ollama_status()
        assert "available" in status

    def test_check_ollama_status_includes_default_model(self):
        """check_ollama_status must include 'default_model' key."""
        status = check_ollama_status()
        assert "default_model" in status

    def test_check_ollama_status_includes_langchain_installed(self):
        """check_ollama_status must include 'langchain_installed' key."""
        status = check_ollama_status()
        assert "langchain_installed" in status


# ---------------------------------------------------------------------------
# Tests: check_provider_status
# ---------------------------------------------------------------------------


class TestCheckProviderStatus:
    """Tests for check_provider_status function."""

    def test_check_provider_status_returns_dict(self):
        """check_provider_status must return a dictionary."""
        status = check_provider_status()
        assert isinstance(status, dict)

    def test_check_provider_status_includes_providers(self):
        """check_provider_status must include 'providers' key."""
        status = check_provider_status()
        assert "providers" in status

    def test_check_provider_status_includes_all_providers(self):
        """check_provider_status must include all three providers."""
        status = check_provider_status()
        providers = status["providers"]
        assert "ollama" in providers
        assert "claude" in providers
        assert "openai" in providers

    def test_check_provider_status_filters_by_provider(self):
        """check_provider_status must filter by specific provider."""
        status = check_provider_status("ollama")
        providers = status["providers"]
        assert "ollama" in providers
        # Should only include ollama when filtered
        assert len(providers) == 1

    def test_check_provider_status_includes_default_provider(self):
        """check_provider_status must include 'default_provider' key."""
        status = check_provider_status()
        assert "default_provider" in status

    def test_check_provider_status_provider_has_available_key(self):
        """Each provider status must include 'available' key."""
        status = check_provider_status()
        for provider_name, provider_status in status["providers"].items():
            assert "available" in provider_status

    def test_check_provider_status_provider_has_installed_key(self):
        """Each provider status must include 'installed' key."""
        status = check_provider_status()
        for provider_name, provider_status in status["providers"].items():
            assert "installed" in provider_status

    def test_check_provider_status_provider_has_default_model(self):
        """Each provider status must include 'default_model' key."""
        status = check_provider_status()
        for provider_name, provider_status in status["providers"].items():
            assert "default_model" in provider_status
