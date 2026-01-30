#!/usr/bin/env python3
"""
---
id: SCRIPT-0076
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-29
test:
  runner: pytest
  command: "pytest -q tests/unit/test_query_cli.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0186-llamaindex-retrieval-layer
  - PRD-0008-governance-rag-pipeline
  - SCRIPT-0073-retriever
---
Purpose: CLI query tool for GoldenPath governance RAG.

Provides command-line interface to query governance documents
using the RAG retriever. Supports text and JSON output formats,
metadata filtering, and citation formatting.

Per PRD-0008: CLI interface for `gov-rag query "..."` pattern.
Per ADR-0186: Returns results with citations (file path + heading).

Example:
    >>> # Query governance documents
    >>> python -m scripts.rag.cli query "What are TDD requirements?"

    >>> # Query with JSON output
    >>> python -m scripts.rag.cli query "coverage targets" --format json

    >>> # Query with filters
    >>> python -m scripts.rag.cli query "testing" --filter doc_type=governance
"""

import argparse
import json
import sys
from enum import Enum
from typing import Any, Dict, List, Optional

from scripts.rag.retriever import GovernanceRetriever, RetrievalResult, format_citation


class OutputFormat(Enum):
    """Output format options for CLI results."""

    TEXT = "text"
    JSON = "json"


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: List of argument strings. If None, uses sys.argv.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="gov-rag",
        description="Query GoldenPath governance documents using RAG",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query governance documents")
    query_parser.add_argument(
        "query",
        nargs="?",
        help="Search query string",
    )
    query_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )
    query_parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Metadata filter in key=value format",
    )
    query_parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    query_parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="ChromaDB collection name",
    )
    query_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including query metadata",
    )
    query_parser.add_argument(
        "--no-citations",
        action="store_true",
        help="Exclude citations from output",
    )
    query_parser.add_argument(
        "--hybrid",
        action="store_true",
        help="Use hybrid retrieval (vector + graph expansion)",
    )
    query_parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Generate LLM-synthesized answer",
    )
    query_parser.add_argument(
        "--provider",
        type=str,
        choices=["ollama", "claude", "openai"],
        default=None,
        help="LLM provider for synthesis (default: ollama)",
    )
    query_parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name for synthesis (provider-specific)",
    )

    return parser.parse_args(args)


def parse_filter_string(filter_string: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Parse a filter string into a dictionary.

    Args:
        filter_string: Filter in "key=value" format.

    Returns:
        Dictionary with filter key-value pairs, or None.
    """
    if not filter_string:
        return None

    if "=" not in filter_string:
        return None

    key, value = filter_string.split("=", 1)
    return {key.strip(): value.strip()}


def run_query(
    query: str,
    retriever: Optional[GovernanceRetriever] = None,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    filter_string: Optional[str] = None,
) -> List[RetrievalResult]:
    """
    Execute a retrieval query.

    Args:
        query: Search query string.
        retriever: GovernanceRetriever instance. If None, creates one.
        top_k: Number of results to return.
        filters: Metadata filters as dictionary.
        filter_string: Metadata filter as string (alternative to filters).

    Returns:
        List of RetrievalResult objects.
    """
    if retriever is None:
        retriever = GovernanceRetriever(usage_log_path=None)

    # Parse filter string if provided
    if filter_string and not filters:
        filters = parse_filter_string(filter_string)

    return retriever.query(query, top_k=top_k, filters=filters)


def format_results(
    results: List[RetrievalResult],
    format_type: OutputFormat = OutputFormat.TEXT,
    include_citations: bool = True,
) -> str:
    """
    Format retrieval results for output.

    Args:
        results: List of RetrievalResult objects.
        format_type: Output format (TEXT or JSON).
        include_citations: Whether to include citations.

    Returns:
        Formatted string output.
    """
    if not results:
        if format_type == OutputFormat.JSON:
            return json.dumps({"results": [], "count": 0}, indent=2)
        return "No results found."

    if format_type == OutputFormat.JSON:
        json_results = []
        for result in results:
            item = {
                "id": result.id,
                "text": result.text,
                "metadata": result.metadata,
                "score": result.score,
            }
            if include_citations:
                item["citation"] = format_citation(result)
            json_results.append(item)

        return json.dumps(
            {"results": json_results, "count": len(json_results)}, indent=2
        )

    # Text format
    lines = []
    for i, result in enumerate(results, 1):
        lines.append(f"--- Result {i} ---")
        if include_citations:
            citation = format_citation(result)
            lines.append(f"Source: {citation}")
        lines.append(f"Score: {result.score:.4f}")
        lines.append("")
        lines.append(result.text)
        lines.append("")

    return "\n".join(lines)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command-line arguments. If None, uses sys.argv.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        parsed = parse_args(args)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1

    if parsed.command != "query":
        print("Error: Unknown command. Use 'query' subcommand.", file=sys.stderr)
        return 1

    if not parsed.query:
        print("Error: Query argument is required.", file=sys.stderr)
        return 1

    # Validate format
    try:
        output_format = OutputFormat(parsed.format)
    except ValueError:
        print(f"Error: Invalid format '{parsed.format}'.", file=sys.stderr)
        return 1

    # Parse filters
    filters = parse_filter_string(parsed.filter)

    # Handle synthesize mode (includes hybrid by default)
    if parsed.synthesize:
        try:
            from scripts.rag.llm_synthesis import RAGSynthesizer, check_provider_status

            # Determine provider
            provider = parsed.provider or "ollama"

            # Check provider status
            status = check_provider_status(provider)
            provider_info = status["providers"].get(provider, {})

            if not provider_info.get("available"):
                error = provider_info.get("error", "unknown")
                print(f"Warning: {provider} not available: {error}", file=sys.stderr)
                print("Falling back to raw retrieval...", file=sys.stderr)
                parsed.synthesize = False
            else:
                model = parsed.model or provider_info.get("default_model")
                synthesizer = RAGSynthesizer(provider=provider, model=model)

                result = synthesizer.synthesize(
                    question=parsed.query,
                    top_k=parsed.top_k,
                    expand_graph=True,  # Always use graph with synthesis
                )
                synthesizer.close()

                if output_format == OutputFormat.JSON:
                    output = json.dumps(
                        {
                            "answer": result.answer,
                            "citations": result.citations,
                            "model": result.model,
                            "context_chunks": result.context_chunks,
                            "source_docs": result.source_docs,
                        },
                        indent=2,
                    )
                else:
                    output = f"{result.answer}\n\n---\nSources ({result.context_chunks} chunks from {len(result.source_docs)} docs):\n"
                    for citation in result.citations[:5]:  # Limit citations shown
                        output += f"  - {citation}\n"
                    output += f"\nModel: {result.model}"

                if parsed.verbose:
                    print(f"Query: {parsed.query}", file=sys.stderr)
                    print(f"Model: {result.model}", file=sys.stderr)
                    print(f"Context chunks: {result.context_chunks}", file=sys.stderr)
                    print("---", file=sys.stderr)

                print(output)
                return 0

        except ImportError as e:
            print(f"Warning: LLM synthesis not available: {e}", file=sys.stderr)
            print("Falling back to raw retrieval...", file=sys.stderr)
            parsed.synthesize = False

    # Handle hybrid mode
    if parsed.hybrid:
        try:
            from scripts.rag.hybrid_retriever import HybridRetriever

            retriever = HybridRetriever()
            results = retriever.query(
                query_text=parsed.query,
                top_k=parsed.top_k,
                filters=filters,
                expand_graph=True,
            )
            retriever.close()

            # Convert HybridResult to RetrievalResult for formatting
            converted_results = [
                RetrievalResult(
                    id=r.id,
                    text=r.text,
                    metadata=r.metadata,
                    score=r.score,
                )
                for r in results
            ]

        except ImportError as e:
            print(f"Warning: Hybrid retrieval not available: {e}", file=sys.stderr)
            print("Falling back to vector-only retrieval...", file=sys.stderr)
            parsed.hybrid = False

    # Standard vector-only retrieval
    if not parsed.hybrid and not parsed.synthesize:
        try:
            retriever_kwargs = {"usage_log_path": None}
            if parsed.collection:
                retriever_kwargs["collection_name"] = parsed.collection
            retriever = GovernanceRetriever(**retriever_kwargs)
        except Exception as e:
            print(f"Error: Failed to initialize retriever: {e}", file=sys.stderr)
            return 1

        try:
            converted_results = run_query(
                query=parsed.query,
                retriever=retriever,
                top_k=parsed.top_k,
                filters=filters,
            )
        except Exception as e:
            print(f"Error: Query failed: {e}", file=sys.stderr)
            return 1

    # Format output for non-synthesis modes
    include_citations = not parsed.no_citations
    output = format_results(
        converted_results,
        format_type=output_format,
        include_citations=include_citations,
    )

    # Print verbose info if requested
    if parsed.verbose:
        print(f"Query: {parsed.query}", file=sys.stderr)
        print(f"Top-K: {parsed.top_k}", file=sys.stderr)
        if filters:
            print(f"Filters: {filters}", file=sys.stderr)
        print(f"Results: {len(converted_results)}", file=sys.stderr)
        print("---", file=sys.stderr)

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
