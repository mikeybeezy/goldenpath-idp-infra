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
  command: "pytest -q tests/unit/test_llm_synthesis.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
  - SCRIPT-0079-hybrid-retriever
---
Purpose: LLM synthesis for RAG responses using multiple providers.

Supports:
- Ollama (local, free) - llama3.2, mistral, phi3, etc.
- Claude (API) - claude-3-haiku, claude-sonnet-4-20250514, etc.
- OpenAI (API) - gpt-4o-mini, gpt-4o, etc.

Phase 1 implementation per PRD-0008.

Example:
    >>> from scripts.rag.llm_synthesis import synthesize_answer
    >>> answer = synthesize_answer("What are TDD requirements?", provider="ollama")
    >>> answer = synthesize_answer("What are TDD requirements?", provider="claude")
    >>> answer = synthesize_answer("What are TDD requirements?", provider="openai")
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Union

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate

    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    LANGCHAIN_CORE_AVAILABLE = False
    ChatPromptTemplate = None

# Ollama
try:
    from langchain_ollama import ChatOllama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ChatOllama = None

# Claude/Anthropic
try:
    from langchain_anthropic import ChatAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

# OpenAI
try:
    from langchain_openai import ChatOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None

from scripts.rag.hybrid_retriever import HybridRetriever, HybridResult
from scripts.rag.retriever import RetrievalResult, format_citation


class LLMProvider(Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    CLAUDE = "claude"
    OPENAI = "openai"


# Default settings per provider
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Legacy aliases
DEFAULT_MODEL = DEFAULT_OLLAMA_MODEL
DEFAULT_BASE_URL = DEFAULT_OLLAMA_URL
LANGCHAIN_AVAILABLE = LANGCHAIN_CORE_AVAILABLE and OLLAMA_AVAILABLE

# System prompt for governance RAG
SYSTEM_PROMPT = """You are a helpful assistant for the GoldenPath platform governance documentation.
Your role is to answer questions about platform policies, architecture decisions, runbooks, and best practices.

Guidelines:
- Answer based ONLY on the provided context chunks
- If the context doesn't contain enough information, say so
- Include citations using the format [DOC-ID: Section](file_path)
- Be concise and direct
- For technical questions, include code examples if present in context
- If multiple documents are relevant, synthesize information from all of them

Context chunks are provided below. Use them to answer the user's question."""

RAG_PROMPT_TEMPLATE = """Context:
{context}

Question: {question}

Answer the question based on the context above. Include citations."""


def _check_ollama_available() -> bool:
    """Check if Ollama is installed and running."""
    if not LANGCHAIN_AVAILABLE:
        return False
    try:
        import httpx

        response = httpx.get(f"{DEFAULT_BASE_URL}/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def _format_context(results: List[Union[HybridResult, RetrievalResult]]) -> str:
    """Format retrieval results as context for LLM."""
    context_parts = []

    for i, result in enumerate(results, 1):
        # Get metadata
        if isinstance(result, HybridResult):
            metadata = result.metadata
            text = result.text
        else:
            metadata = result.metadata
            text = result.text

        doc_id = metadata.get("doc_id", "Unknown")
        section = metadata.get("section", "")
        file_path = metadata.get("file_path", "")

        # Format chunk
        header = f"[{i}] {doc_id}"
        if section:
            header += f" - {section}"
        if file_path:
            header += f" ({file_path})"

        context_parts.append(f"{header}\n{text}")

    return "\n\n---\n\n".join(context_parts)


def _format_citations(results: List[Union[HybridResult, RetrievalResult]]) -> str:
    """Format citations list."""
    citations = []
    seen = set()

    for result in results:
        if isinstance(result, HybridResult):
            # Convert to RetrievalResult for format_citation
            rr = RetrievalResult(
                id=result.id,
                text=result.text,
                metadata=result.metadata,
                score=result.score,
            )
        else:
            rr = result

        citation = format_citation(rr)
        doc_id = rr.metadata.get("doc_id", "")

        if doc_id and doc_id not in seen:
            seen.add(doc_id)
            citations.append(citation)

    return "\n".join(f"- {c}" for c in citations)


@dataclass
class SynthesisResult:
    """Result from LLM synthesis."""

    answer: str
    citations: List[str]
    model: str
    context_chunks: int
    source_docs: List[str]


def _create_llm(
    provider: str, model: str, temperature: float = 0.1, base_url: Optional[str] = None
):
    """
    Create an LLM instance for the specified provider.

    Args:
        provider: One of "ollama", "claude", "openai".
        model: Model name for the provider.
        temperature: LLM temperature.
        base_url: Base URL (only for Ollama).

    Returns:
        LangChain chat model instance or None.
    """
    provider = provider.lower()

    if provider == "ollama":
        if not OLLAMA_AVAILABLE:
            return None
        try:
            return ChatOllama(
                model=model,
                base_url=base_url or DEFAULT_OLLAMA_URL,
                temperature=temperature,
            )
        except Exception:
            return None

    elif provider == "claude":
        if not ANTHROPIC_AVAILABLE:
            return None
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        try:
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=api_key,
            )
        except Exception:
            return None

    elif provider == "openai":
        if not OPENAI_AVAILABLE:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key,
            )
        except Exception:
            return None

    return None


@dataclass
class RAGSynthesizer:
    """
    LLM synthesizer for RAG responses using multiple providers.

    Attributes:
        provider: LLM provider ("ollama", "claude", "openai").
        model: Model name for the provider.
        base_url: Ollama server URL (only for Ollama provider).
        temperature: LLM temperature (default: 0.1 for factual responses).
        retriever: HybridRetriever for context retrieval.
    """

    provider: str = DEFAULT_PROVIDER
    model: Optional[str] = None
    base_url: str = DEFAULT_OLLAMA_URL
    temperature: float = 0.1
    retriever: Optional[HybridRetriever] = None
    _llm: Any = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize LLM and retriever."""
        if self.retriever is None:
            self.retriever = HybridRetriever()

        # Set default model based on provider if not specified
        if self.model is None:
            if self.provider == "claude":
                self.model = DEFAULT_CLAUDE_MODEL
            elif self.provider == "openai":
                self.model = DEFAULT_OPENAI_MODEL
            else:
                self.model = DEFAULT_OLLAMA_MODEL

        # Create LLM
        self._llm = _create_llm(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            base_url=self.base_url,
        )

    def is_available(self) -> bool:
        """Check if LLM synthesis is available."""
        if self._llm is None:
            return False
        if self.provider == "ollama":
            return _check_ollama_available()
        # For API-based providers, having a valid LLM means we have an API key
        return True

    def synthesize(
        self,
        question: str,
        results: Optional[List[Union[HybridResult, RetrievalResult]]] = None,
        top_k: int = 5,
        expand_graph: bool = True,
    ) -> SynthesisResult:
        """
        Synthesize an answer from retrieved chunks.

        Args:
            question: User's question.
            results: Pre-fetched retrieval results. If None, fetches via retriever.
            top_k: Number of chunks to retrieve (if results not provided).
            expand_graph: Whether to use graph expansion.

        Returns:
            SynthesisResult with answer, citations, and metadata.
        """
        # Fetch results if not provided
        if results is None:
            results = self.retriever.query(
                query_text=question,
                top_k=top_k,
                expand_graph=expand_graph,
            )

        if not results:
            return SynthesisResult(
                answer="I couldn't find any relevant information to answer your question.",
                citations=[],
                model=self.model,
                context_chunks=0,
                source_docs=[],
            )

        # Format context
        context = _format_context(results)

        # Extract source docs
        source_docs = []
        seen_docs = set()
        for r in results:
            doc_id = r.metadata.get("doc_id")
            if doc_id and doc_id not in seen_docs:
                seen_docs.add(doc_id)
                source_docs.append(doc_id)

        # If LLM not available, return formatted context
        if not self.is_available():
            return SynthesisResult(
                answer=f"[LLM not available - raw context]\n\n{context}",
                citations=[
                    format_citation(
                        RetrievalResult(
                            id=r.id, text=r.text, metadata=r.metadata, score=r.score
                        )
                    )
                    for r in results
                ],
                model="none",
                context_chunks=len(results),
                source_docs=source_docs,
            )

        # Build prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", RAG_PROMPT_TEMPLATE),
            ]
        )

        # Generate response
        try:
            chain = prompt | self._llm
            response = chain.invoke(
                {
                    "context": context,
                    "question": question,
                }
            )
            answer = response.content
        except Exception as e:
            answer = f"Error generating response: {e}\n\nContext:\n{context}"

        # Extract citations
        citations = []
        for r in results:
            rr = RetrievalResult(
                id=r.id, text=r.text, metadata=r.metadata, score=r.score
            )
            citations.append(format_citation(rr))

        return SynthesisResult(
            answer=answer,
            citations=citations,
            model=self.model,
            context_chunks=len(results),
            source_docs=source_docs,
        )

    def close(self):
        """Close retriever resources."""
        if self.retriever is not None:
            self.retriever.close()


def synthesize_answer(
    question: str,
    results: Optional[List[Union[HybridResult, RetrievalResult]]] = None,
    provider: str = DEFAULT_PROVIDER,
    model: Optional[str] = None,
    top_k: int = 5,
    expand_graph: bool = True,
) -> str:
    """
    Convenience function to synthesize an answer.

    Args:
        question: User's question.
        results: Pre-fetched retrieval results.
        provider: LLM provider ("ollama", "claude", "openai").
        model: Model name (uses provider default if not specified).
        top_k: Number of chunks to retrieve.
        expand_graph: Whether to use graph expansion.

    Returns:
        Synthesized answer string.
    """
    synthesizer = RAGSynthesizer(provider=provider, model=model)
    try:
        result = synthesizer.synthesize(
            question=question,
            results=results,
            top_k=top_k,
            expand_graph=expand_graph,
        )
        return result.answer
    finally:
        synthesizer.close()


def check_ollama_status() -> Dict[str, Any]:
    """
    Check Ollama server status and available models.

    Returns:
        Dict with status, available models, and default model.
    """
    status = {
        "available": False,
        "base_url": DEFAULT_OLLAMA_URL,
        "default_model": DEFAULT_OLLAMA_MODEL,
        "models": [],
        "langchain_installed": OLLAMA_AVAILABLE,
    }

    if not OLLAMA_AVAILABLE:
        status["error"] = "langchain-ollama not installed"
        return status

    try:
        import httpx

        response = httpx.get(f"{DEFAULT_OLLAMA_URL}/api/tags", timeout=5.0)
        if response.status_code == 200:
            status["available"] = True
            data = response.json()
            status["models"] = [m["name"] for m in data.get("models", [])]
        else:
            status["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        status["error"] = str(e)

    return status


def check_provider_status(provider: str = None) -> Dict[str, Any]:
    """
    Check status for a specific provider or all providers.

    Args:
        provider: Specific provider to check, or None for all.

    Returns:
        Dict with provider status information.
    """
    if provider:
        provider = provider.lower()

    status = {
        "default_provider": DEFAULT_PROVIDER,
        "providers": {},
    }

    # Check Ollama
    if provider is None or provider == "ollama":
        ollama_status = check_ollama_status()
        status["providers"]["ollama"] = {
            "available": ollama_status["available"],
            "installed": OLLAMA_AVAILABLE,
            "default_model": DEFAULT_OLLAMA_MODEL,
            "models": ollama_status.get("models", []),
            "error": ollama_status.get("error"),
        }

    # Check Claude
    if provider is None or provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        status["providers"]["claude"] = {
            "available": ANTHROPIC_AVAILABLE and bool(api_key),
            "installed": ANTHROPIC_AVAILABLE,
            "default_model": DEFAULT_CLAUDE_MODEL,
            "api_key_set": bool(api_key),
            "error": None
            if ANTHROPIC_AVAILABLE
            else "langchain-anthropic not installed",
        }
        if ANTHROPIC_AVAILABLE and not api_key:
            status["providers"]["claude"]["error"] = "ANTHROPIC_API_KEY not set"

    # Check OpenAI
    if provider is None or provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        status["providers"]["openai"] = {
            "available": OPENAI_AVAILABLE and bool(api_key),
            "installed": OPENAI_AVAILABLE,
            "default_model": DEFAULT_OPENAI_MODEL,
            "api_key_set": bool(api_key),
            "error": None if OPENAI_AVAILABLE else "langchain-openai not installed",
        }
        if OPENAI_AVAILABLE and not api_key:
            status["providers"]["openai"]["error"] = "OPENAI_API_KEY not set"

    return status


if __name__ == "__main__":
    import json
    import sys

    # Parse args
    provider = sys.argv[1] if len(sys.argv) > 1 else None

    # Check status
    status = check_provider_status(provider)
    print("LLM Provider Status:")
    print(json.dumps(status, indent=2))

    # Find first available provider
    available_provider = None
    for p, info in status["providers"].items():
        if info["available"]:
            available_provider = p
            break

    if available_provider:
        print(f"\nTest query using {available_provider}:")
        answer = synthesize_answer(
            "What are the TDD requirements?",
            provider=available_provider,
            top_k=3,
            expand_graph=True,
        )
        print(answer)
    else:
        print("\nNo providers available. Set up one of:")
        print("  - Ollama: brew install ollama && ollama serve && ollama pull llama3.2")
        print("  - Claude: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("  - OpenAI: export OPENAI_API_KEY='sk-...'")
        print("\nAnd install the provider package:")
        print("  - pip install langchain-anthropic  # for Claude")
        print("  - pip install langchain-openai     # for OpenAI")
