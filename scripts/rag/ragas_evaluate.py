#!/usr/bin/env python3
"""
---
id: SCRIPT-0080
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-29
test:
  runner: pytest
  command: "pytest -q tests/unit/test_ragas_evaluate.py"
  evidence: declared
dry_run:
  supported: true
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
---
Purpose: RAGAS evaluation script for RAG pipeline quality metrics.

Evaluates retrieval quality using RAGAS metrics:
- context_precision: Are retrieved contexts relevant?
- faithfulness: Is the answer grounded in context?
- answer_relevancy: Does the answer address the question?

Usage:
    python -m scripts.rag.ragas_evaluate
    python -m scripts.rag.ragas_evaluate --questions tests/ragas/questions.json --output reports/ragas_metrics.json
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.rag.retriever import GovernanceRetriever


def load_questions(path: Path) -> List[str]:
    """Load test questions from JSON file."""
    data = json.loads(path.read_text())
    return data.get("questions", [])


def retrieve_contexts(
    questions: List[str],
    retriever: GovernanceRetriever,
    top_k: int = 5,
) -> List[List[str]]:
    """Retrieve contexts for each question."""
    all_contexts = []
    for question in questions:
        results = retriever.query(question, top_k=top_k)
        contexts = [r.text for r in results]
        all_contexts.append(contexts)
    return all_contexts


def generate_answers_simple(
    questions: List[str],
    contexts: List[List[str]],
) -> List[str]:
    """
    Generate simple answers by concatenating top contexts.

    This is a placeholder - for production, use an LLM to synthesize answers.
    """
    answers = []
    for question, ctx_list in zip(questions, contexts):
        if ctx_list:
            # Use first context as answer (simple baseline)
            answer = ctx_list[0][:500] if ctx_list[0] else "No relevant context found."
        else:
            answer = "No relevant context found."
        answers.append(answer)
    return answers


def evaluate_with_ragas(
    questions: List[str],
    answers: List[str],
    contexts: List[List[str]],
    use_openai: bool = True,
) -> Dict[str, Any]:
    """
    Run RAGAS evaluation on the retrieval results.

    Args:
        questions: List of test questions.
        answers: Generated answers for each question.
        contexts: Retrieved contexts for each question.
        use_openai: If True, use OpenAI for evaluation. Otherwise skip LLM metrics.

    Returns:
        Dictionary with RAGAS metrics.
    """
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
        )
    except ImportError as e:
        return {
            "error": f"RAGAS import failed: {e}",
            "metrics": {},
        }

    # Build RAGAS dataset
    data = {
        "user_input": questions,
        "response": answers,
        "retrieved_contexts": contexts,
    }
    dataset = Dataset.from_dict(data)

    # Select metrics
    metrics = [faithfulness, answer_relevancy]

    try:
        # Run evaluation
        result = evaluate(dataset, metrics=metrics)

        return {
            "faithfulness": float(result["faithfulness"]) if "faithfulness" in result else None,
            "answer_relevancy": float(result["answer_relevancy"]) if "answer_relevancy" in result else None,
        }
    except Exception as e:
        return {
            "error": str(e),
            "metrics": {},
        }


def compute_retrieval_metrics(
    questions: List[str],
    contexts: List[List[str]],
) -> Dict[str, float]:
    """
    Compute basic retrieval metrics without LLM.

    - avg_contexts_per_query: Average number of contexts retrieved
    - queries_with_results: Percentage of queries that returned results
    """
    total_contexts = sum(len(c) for c in contexts)
    queries_with_results = sum(1 for c in contexts if c)

    return {
        "total_questions": len(questions),
        "avg_contexts_per_query": total_contexts / len(questions) if questions else 0,
        "queries_with_results": queries_with_results,
        "queries_with_results_pct": queries_with_results / len(questions) * 100 if questions else 0,
    }


def run_evaluation(
    questions_path: Path = Path("tests/ragas/questions.json"),
    output_path: Path = Path("reports/ragas_metrics.json"),
    top_k: int = 5,
    skip_llm: bool = False,
) -> Dict[str, Any]:
    """
    Run full RAGAS evaluation pipeline.

    Args:
        questions_path: Path to questions JSON file.
        output_path: Path to write results.
        top_k: Number of contexts to retrieve per question.
        skip_llm: If True, skip LLM-based metrics (faster, cheaper).

    Returns:
        Evaluation results dictionary.
    """
    # Load questions
    questions = load_questions(questions_path)
    print(f"Loaded {len(questions)} questions")

    # Initialize retriever
    retriever = GovernanceRetriever()

    # Retrieve contexts
    print("Retrieving contexts...")
    contexts = retrieve_contexts(questions, retriever, top_k=top_k)

    # Generate answers
    print("Generating answers...")
    answers = generate_answers_simple(questions, contexts)

    # Compute basic metrics
    basic_metrics = compute_retrieval_metrics(questions, contexts)
    print(f"Basic metrics: {basic_metrics}")

    # Run RAGAS evaluation (if not skipped)
    ragas_metrics = {}
    if not skip_llm:
        print("Running RAGAS evaluation (this may take a few minutes)...")
        ragas_metrics = evaluate_with_ragas(questions, answers, contexts)
        print(f"RAGAS metrics: {ragas_metrics}")
    else:
        print("Skipping LLM-based RAGAS metrics")

    # Build result
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_count": len(questions),
        "top_k": top_k,
        "basic_metrics": basic_metrics,
        "ragas_metrics": ragas_metrics,
        "status": "completed" if not ragas_metrics.get("error") else "partial",
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(f"Results written to {output_path}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run RAGAS evaluation")
    parser.add_argument(
        "--questions",
        type=Path,
        default=Path("tests/ragas/questions.json"),
        help="Path to questions JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/ragas_metrics.json"),
        help="Path to write results",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of contexts to retrieve per question",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM-based metrics (faster, cheaper)",
    )

    args = parser.parse_args()
    run_evaluation(
        questions_path=args.questions,
        output_path=args.output,
        top_k=args.top_k,
        skip_llm=args.skip_llm,
    )
