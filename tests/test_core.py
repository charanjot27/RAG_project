"""Dependency-light unit tests (no torch / transformers / qdrant needed).

These cover the pure logic so CI stays fast and green on every push.
Heavier integration tests (real retrieval/generation) need the full stack
and a running Qdrant, so they live outside CI.
"""

from src.citations import build_output
from src.generate import format_context
from src.ingest import chunk_text
from src.verify import split_sentences


def test_chunk_text_overlap_and_no_infinite_loop():
    words = " ".join(f"w{i}" for i in range(1000))
    chunks = chunk_text(words, size=100, overlap=20)
    assert len(chunks) > 1
    # every chunk is non-empty and within the size bound
    assert all(0 < len(c.split()) <= 100 for c in chunks)


def test_chunk_text_handles_empty():
    assert chunk_text("") == []


def test_chunk_text_overlap_not_larger_than_size():
    # overlap >= size must not hang (step is clamped to >= 1)
    chunks = chunk_text("a b c d e f", size=2, overlap=5)
    assert isinstance(chunks, list) and chunks


def test_split_sentences():
    assert split_sentences("A first fact. A second one! And a third?") == [
        "A first fact.",
        "A second one!",
        "And a third?",
    ]


def test_build_output_faithfulness_score():
    verified = [
        {"sentence": "A.", "label": "grounded", "score": 0.9,
         "source": {"source": "x.pdf", "page": 1}},
        {"sentence": "B.", "label": "unverified", "score": 0.1, "source": None},
    ]
    out = build_output(verified)
    assert out["faithfulness_score"] == 0.5
    assert out["sentences"][0]["citation"] == "x.pdf p.1"
    assert out["sentences"][1]["citation"] is None


def test_build_output_empty():
    out = build_output([])
    assert out["faithfulness_score"] == 0.0
    assert out["sentences"] == []


def test_format_context_numbers_sources():
    ctx = format_context([{"source": "a.pdf", "page": 3, "text": "hello"}])
    assert "[1]" in ctx and "a.pdf p.3" in ctx and "hello" in ctx
