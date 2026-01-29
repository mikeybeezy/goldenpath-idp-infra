"""
Unit tests for RAGAS baseline harness.
"""

from pathlib import Path

from scripts.rag.ragas_baseline import write_baseline


def test_write_baseline_outputs_json(tmp_path: Path):
    out = tmp_path / "ragas.json"
    write_baseline(out, question_count=20)
    content = out.read_text()
    assert "question_count" in content
    assert "context_precision" in content
