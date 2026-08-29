"""Dependency-light unit tests (no torch / transformers / qdrant needed).

These cover the pure logic so CI stays fast and green on every push.
Heavier integration tests (real retrieval/generation) need the full stack
and a running Qdrant, so they live outside CI.
"""

from src import web_source
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


def test_build_output_self_correction_drops_unverified():
    verified = [
        {"sentence": "Grounded fact.", "label": "grounded", "score": 0.9,
         "source": {"source": "x.pdf", "page": 1}},
        {"sentence": "Made up claim.", "label": "unverified", "score": 0.1, "source": None},
    ]
    out = build_output(verified)
    # grounded_answer keeps only the verified sentence
    assert out["grounded_answer"] == "Grounded fact."
    assert "Made up claim." not in out["grounded_answer"]


def test_build_output_abstains_below_threshold():
    verified = [
        {"sentence": "Unsupported.", "label": "unverified", "score": 0.1, "source": None},
    ]
    out = build_output(verified, abstain_threshold=0.5)
    assert out["abstained"] is True
    assert out["faithfulness_score"] == 0.0
    assert "can't confidently answer" in out["answer"].lower()


def test_build_output_no_abstain_when_disabled():
    verified = [
        {"sentence": "Unsupported.", "label": "unverified", "score": 0.1, "source": None},
    ]
    out = build_output(verified, abstain_threshold=0.0)
    assert out["abstained"] is False


def test_web_cache_point_id_is_deterministic():
    from src.web_cache import _point_id

    assert _point_id("https://x.com#c0") == _point_id("https://x.com#c0")
    assert _point_id("https://x.com#c0") != _point_id("https://x.com#c1")


def test_web_search_chunks_builds_url_cited_records(monkeypatch):
    # Mock search + fetch so the test needs no network.
    monkeypatch.setattr(
        web_source, "search_urls",
        lambda q, num_results=5: [{"title": "T", "url": "https://example.com/a"}],
    )
    monkeypatch.setattr(
        web_source, "fetch_main_text",
        lambda url: " ".join(f"word{i}" for i in range(900)),
    )
    chunks = web_source.web_search_chunks("anything")
    assert chunks, "should produce chunks"
    assert all(c["source"] == "https://example.com/a" for c in chunks)
    assert all(c["id"].startswith("https://example.com/a#c") for c in chunks)
    assert all(c["text"] for c in chunks)
