"""Fine-tune the embedding model on question/passage pairs."""

from __future__ import annotations

import json
from pathlib import Path

from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

PAIRS_PATH = Path("training/embed_pairs.json")
OUTPUT_PATH = "models/finetuned-embeddings"


def main() -> None:
    if not PAIRS_PATH.exists():
        raise SystemExit(f"{PAIRS_PATH} not found. Run: python -m scripts.gen_training_pairs")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    pairs = json.loads(PAIRS_PATH.read_text())
    examples = [InputExample(texts=[p["question"], p["positive"]]) for p in pairs]

    loader = DataLoader(examples, shuffle=True, batch_size=16)
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
