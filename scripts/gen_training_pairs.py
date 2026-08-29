"""Generate embedding training pairs semi-automatically.

For each chunk, ask the LLM to write a couple of questions the passage
answers. That yields hundreds of {question, positive} pairs cheaply — the
training data for training/train_embeddings.py.

    python -m scripts.gen_training_pairs --limit 200

Uses the configured LLM backend (LLM_PROVIDER — Groq by default, so it's free).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from src.generate import complete
from src.ingest import load_chunks

OUTPUT = Path("training/embed_pairs.json")
PROMPT = (
    "Read the passage below and write exactly 2 natural questions that this "
    "passage directly answers. Return ONLY the questions, one per line, no numbering.\n\n"
    "Passage:\n{text}"
)


def questions_for(text: str) -> list[str]:
    answer = complete(
        PROMPT.format(text=text[:2000]),
        system="You write concise, natural questions. Output only the questions.",
        max_tokens=200,
    )
    lines = answer.splitlines()
    out = []
    for line in lines:
        q = re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
        if q.endswith("?"):
            out.append(q)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200, help="max chunks to use")
    args = ap.parse_args()

    chunks = load_chunks()[: args.limit]
    if not chunks:
        raise SystemExit("No chunks. Add PDFs to data/raw/ and run: python -m src.ingest")

    pairs = []
    for i, c in enumerate(chunks, 1):
        for q in questions_for(c["text"]):
            pairs.append({"question": q, "positive": c["text"]})
        if i % 10 == 0:
            print(f"  processed {i}/{len(chunks)} chunks, {len(pairs)} pairs so far")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(pairs, ensure_ascii=False, indent=2))
    print(f"Wrote {len(pairs)} pairs -> {OUTPUT}")


if __name__ == "__main__":
    main()
