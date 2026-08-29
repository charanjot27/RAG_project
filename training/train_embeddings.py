"""Deep-learning component #1 — fine-tune the embedding model.

Contrastive learning in plain English: show the model pairs that should
be close (a question and the passage that answers it). It nudges its
weights until similar things sit close on the "meaning map". That nudging
of weights based on examples *is* deep learning.

Input: training/embed_pairs.json — a list of {"question", "positive"}.
Generate it cheaply with scripts/gen_training_pairs.py.

Run on a GPU (Google Colab's free tier is fine) if your laptop is slow.
Afterwards, set EMBEDDING_MODEL=models/finetuned-embeddings and re-run eval.
"""

from __future__ import annotations

import json
from pathlib import Path

from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

PAIRS_PATH = Path("training/embed_pairs.json")
OUTPUT_PATH = "models/finetuned-embeddings"


def main() -> None:
    if not PAIRS_PATH.exists():
        raise SystemExit(
            f"{PAIRS_PATH} not found. Generate pairs first: "
            "python -m scripts.gen_training_pairs"
        )

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    pairs = json.loads(PAIRS_PATH.read_text())
    examples = [InputExample(texts=[p["question"], p["positive"]]) for p in pairs]

    loader = DataLoader(examples, shuffle=True, batch_size=16)
    # MultipleNegativesRankingLoss is the standard choice for Q/passage pairs:
    # other rows in the batch act as negatives automatically.
    loss = losses.MultipleNegativesRankingLoss(model)

    model.fit(
        train_objectives=[(loader, loss)],
        epochs=3,
        warmup_steps=100,
        output_path=OUTPUT_PATH,
    )
    print(f"Saved fine-tuned model to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
