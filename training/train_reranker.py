"""Deep-learning component #2 — fine-tune the cross-encoder reranker.

Train on triples: a query, a passage that answers it (label 1), and
passages that don't (label 0).

Input: training/rerank_pairs.json — a list of {"query", "passage", "label"}.
Afterwards, set RERANKER_MODEL=models/finetuned-reranker and re-run eval.
"""

from __future__ import annotations

import json
from pathlib import Path

from sentence_transformers import CrossEncoder, InputExample
from torch.utils.data import DataLoader

PAIRS_PATH = Path("training/rerank_pairs.json")
OUTPUT_PATH = "models/finetuned-reranker"


def main() -> None:
    if not PAIRS_PATH.exists():
        raise SystemExit(f"{PAIRS_PATH} not found. Create query/passage/label triples first.")

    model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", num_labels=1)
    data = json.loads(PAIRS_PATH.read_text())
    examples = [
        InputExample(texts=[d["query"], d["passage"]], label=float(d["label"]))
        for d in data
    ]
    loader = DataLoader(examples, shuffle=True, batch_size=16)

    model.fit(
        train_dataloader=loader,
        epochs=2,
        warmup_steps=100,
        output_path=OUTPUT_PATH,
    )
    print(f"Saved fine-tuned reranker to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
