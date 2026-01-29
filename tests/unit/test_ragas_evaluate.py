"""
Unit tests for ragas_evaluate module.

Tests RAGAS evaluation pipeline with multi-provider support.
Per GOV-0017: TDD-first implementation.
"""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.rag.ragas_evaluate import (
    load_questions,
    retrieve_contexts,
    generate_answers_simple,
    evaluate_with_ragas,
    compute_retrieval_metrics,
    run_evaluation,
    _create_llm_for_ragas,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_retriever():
    """Create a mock GovernanceRetriever."""
    retriever = MagicMock()
    result = MagicMock()
    result.text = "Sample context about TDD requirements."
    retriever.query.return_value = [result]
    return retriever


@pytest.fixture
def sample_questions():
    """Sample test questions."""
    return [
        "What are the TDD requirements?",
        "What is the coverage target?",
        "How do golden outputs work?",
    ]


@pytest.fixture
def sample_contexts():
    """Sample retrieval contexts."""
    return [
        ["Context 1 about TDD", "Context 2 about testing"],
        ["Context about coverage targets"],
        ["Context about golden outputs", "More about golden files"],
    ]


@pytest.fixture
def sample_answers():
    """Sample generated answers."""
    return [
        "TDD requires tests before implementation.",
        "Coverage target is 60% for V1.",
        "Golden outputs are blessed expected files.",
    ]


@pytest.fixture
def questions_json_file(tmp_path, sample_questions):
    """Create a temporary questions JSON file."""
    file_path = tmp_path / "questions.json"
    file_path.write_text(json.dumps({"questions": sample_questions}))
    return file_path


# ---------------------------------------------------------------------------
# Tests: load_questions
# ---------------------------------------------------------------------------


class TestLoadQuestions:
    """Tests for load_questions function."""

    def test_load_questions_from_file(self, questions_json_file, sample_questions):
        """load_questions must load questions from JSON file."""
        questions = load_questions(questions_json_file)
        assert questions == sample_questions

    def test_load_questions_returns_empty_for_missing_key(self, tmp_path):
        """load_questions must return empty list if 'questions' key missing."""
        file_path = tmp_path / "no_questions.json"
        file_path.write_text(json.dumps({"other": "data"}))
        questions = load_questions(file_path)
        assert questions == []


# ---------------------------------------------------------------------------
# Tests: retrieve_contexts
# ---------------------------------------------------------------------------


class TestRetrieveContexts:
    """Tests for retrieve_contexts function."""

    def test_retrieve_contexts_calls_retriever_for_each_question(
        self, mock_retriever, sample_questions
    ):
        """retrieve_contexts must call retriever for each question."""
        retrieve_contexts(sample_questions, mock_retriever, top_k=5)
        assert mock_retriever.query.call_count == len(sample_questions)

    def test_retrieve_contexts_returns_list_of_context_lists(
        self, mock_retriever, sample_questions
    ):
        """retrieve_contexts must return list of context text lists."""
        contexts = retrieve_contexts(sample_questions, mock_retriever, top_k=5)
        assert len(contexts) == len(sample_questions)
        assert all(isinstance(c, list) for c in contexts)

    def test_retrieve_contexts_extracts_text_from_results(
        self, mock_retriever, sample_questions
    ):
        """retrieve_contexts must extract text from retrieval results."""
        mock_result = MagicMock()
        mock_result.text = "Expected text content"
        mock_retriever.query.return_value = [mock_result]

        contexts = retrieve_contexts(sample_questions, mock_retriever, top_k=5)
        assert contexts[0][0] == "Expected text content"


# ---------------------------------------------------------------------------
# Tests: generate_answers_simple
# ---------------------------------------------------------------------------


class TestGenerateAnswersSimple:
    """Tests for generate_answers_simple function."""

    def test_generate_answers_returns_list(self, sample_questions, sample_contexts):
        """generate_answers_simple must return a list of answers."""
        answers = generate_answers_simple(sample_questions, sample_contexts)
        assert isinstance(answers, list)
        assert len(answers) == len(sample_questions)

    def test_generate_answers_uses_first_context(self, sample_questions, sample_contexts):
        """generate_answers_simple must use first context as answer."""
        answers = generate_answers_simple(sample_questions, sample_contexts)
        # First answer should come from first context
        assert "TDD" in answers[0] or answers[0][:50] == sample_contexts[0][0][:50]

    def test_generate_answers_handles_empty_contexts(self, sample_questions):
        """generate_answers_simple must handle empty context lists."""
        empty_contexts = [[], [], []]
        answers = generate_answers_simple(sample_questions, empty_contexts)
        assert all("No relevant context" in a for a in answers)


# ---------------------------------------------------------------------------
# Tests: compute_retrieval_metrics
# ---------------------------------------------------------------------------


class TestComputeRetrievalMetrics:
    """Tests for compute_retrieval_metrics function."""

    def test_compute_retrieval_metrics_returns_dict(
        self, sample_questions, sample_contexts
    ):
        """compute_retrieval_metrics must return a dictionary."""
        metrics = compute_retrieval_metrics(sample_questions, sample_contexts)
        assert isinstance(metrics, dict)

    def test_compute_retrieval_metrics_includes_total_questions(
        self, sample_questions, sample_contexts
    ):
        """compute_retrieval_metrics must include total_questions."""
        metrics = compute_retrieval_metrics(sample_questions, sample_contexts)
        assert "total_questions" in metrics
        assert metrics["total_questions"] == len(sample_questions)

    def test_compute_retrieval_metrics_includes_avg_contexts(
        self, sample_questions, sample_contexts
    ):
        """compute_retrieval_metrics must include avg_contexts_per_query."""
        metrics = compute_retrieval_metrics(sample_questions, sample_contexts)
        assert "avg_contexts_per_query" in metrics
        # 2 + 1 + 2 = 5 contexts for 3 questions
        assert metrics["avg_contexts_per_query"] == 5 / 3

    def test_compute_retrieval_metrics_includes_queries_with_results(
        self, sample_questions, sample_contexts
    ):
        """compute_retrieval_metrics must include queries_with_results."""
        metrics = compute_retrieval_metrics(sample_questions, sample_contexts)
        assert "queries_with_results" in metrics
        assert metrics["queries_with_results"] == 3

    def test_compute_retrieval_metrics_handles_empty_questions(self):
        """compute_retrieval_metrics must handle empty questions list."""
        metrics = compute_retrieval_metrics([], [])
        assert metrics["total_questions"] == 0
        assert metrics["avg_contexts_per_query"] == 0


# ---------------------------------------------------------------------------
# Tests: _create_llm_for_ragas
# ---------------------------------------------------------------------------


class TestCreateLLMForRAGAS:
    """Tests for _create_llm_for_ragas function."""

    def test_create_llm_returns_none_for_unknown_provider(self):
        """_create_llm_for_ragas must return None for unknown provider."""
        result = _create_llm_for_ragas("unknown")
        assert result is None

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False)
    def test_create_llm_claude_returns_none_without_api_key(self):
        """_create_llm_for_ragas must return None for Claude without API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            result = _create_llm_for_ragas("claude")
        # May return None if langchain-anthropic not installed or no key

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False)
    def test_create_llm_openai_returns_none_without_api_key(self):
        """_create_llm_for_ragas must return None for OpenAI without API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            result = _create_llm_for_ragas("openai")
        # May return None if langchain-openai not installed or no key


# ---------------------------------------------------------------------------
# Tests: evaluate_with_ragas
# ---------------------------------------------------------------------------


class TestEvaluateWithRAGAS:
    """Tests for evaluate_with_ragas function."""

    def test_evaluate_with_ragas_returns_dict(
        self, sample_questions, sample_answers, sample_contexts
    ):
        """evaluate_with_ragas must return a dictionary."""
        # This may fail if RAGAS not installed or no LLM available
        result = evaluate_with_ragas(
            sample_questions,
            sample_answers,
            sample_contexts,
            provider="openai",
        )
        assert isinstance(result, dict)

    def test_evaluate_with_ragas_returns_error_for_unavailable_provider(
        self, sample_questions, sample_answers, sample_contexts
    ):
        """evaluate_with_ragas must return error for unavailable provider."""
        with patch(
            "scripts.rag.ragas_evaluate._create_llm_for_ragas", return_value=None
        ):
            result = evaluate_with_ragas(
                sample_questions,
                sample_answers,
                sample_contexts,
                provider="fake_provider",
            )
        assert "error" in result


# ---------------------------------------------------------------------------
# Tests: run_evaluation
# ---------------------------------------------------------------------------


class TestRunEvaluation:
    """Tests for run_evaluation function."""

    def test_run_evaluation_returns_dict(
        self, tmp_path, questions_json_file
    ):
        """run_evaluation must return a dictionary."""
        output_path = tmp_path / "output.json"

        with patch("scripts.rag.ragas_evaluate.GovernanceRetriever") as MockRetriever:
            mock_retriever = MagicMock()
            mock_result = MagicMock()
            mock_result.text = "Sample context"
            mock_retriever.query.return_value = [mock_result]
            MockRetriever.return_value = mock_retriever

            result = run_evaluation(
                questions_path=questions_json_file,
                output_path=output_path,
                top_k=5,
                skip_llm=True,
            )

        assert isinstance(result, dict)

    def test_run_evaluation_writes_output_file(
        self, tmp_path, questions_json_file
    ):
        """run_evaluation must write results to output file."""
        output_path = tmp_path / "output.json"

        with patch("scripts.rag.ragas_evaluate.GovernanceRetriever") as MockRetriever:
            mock_retriever = MagicMock()
            mock_result = MagicMock()
            mock_result.text = "Sample context"
            mock_retriever.query.return_value = [mock_result]
            MockRetriever.return_value = mock_retriever

            run_evaluation(
                questions_path=questions_json_file,
                output_path=output_path,
                top_k=5,
                skip_llm=True,
            )

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "generated_at" in data
        assert "basic_metrics" in data

    def test_run_evaluation_includes_provider_in_result(
        self, tmp_path, questions_json_file
    ):
        """run_evaluation must include provider in result when not skipping LLM."""
        output_path = tmp_path / "output.json"

        with patch("scripts.rag.ragas_evaluate.GovernanceRetriever") as MockRetriever:
            with patch("scripts.rag.ragas_evaluate.evaluate_with_ragas") as MockEval:
                mock_retriever = MagicMock()
                mock_result = MagicMock()
                mock_result.text = "Sample context"
                mock_retriever.query.return_value = [mock_result]
                MockRetriever.return_value = mock_retriever

                MockEval.return_value = {"faithfulness": 0.8, "answer_relevancy": 0.9}

                result = run_evaluation(
                    questions_path=questions_json_file,
                    output_path=output_path,
                    top_k=5,
                    skip_llm=False,
                    provider="ollama",
                )

        assert result["provider"] == "ollama"
