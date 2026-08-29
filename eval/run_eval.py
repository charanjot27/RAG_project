"""Evaluation harness — the report card.

Once you can measure quality, you can remove any component, watch the
score change, and understand what that component does. That loop is the
whole reverse-engineering education (see DOCUMENTATION.md §23).

Metrics (via RAGAS): faithfulness, answer relevance, context precision,
context recall. Run it after every phase and write the numbers down.

    python -m eval.run_eval
"""

from __future__ import annotations

import json
from pathlib import Path

from src.config import RETRIEVE_K, TOP_N
from src.generate import generate_answer
from src.rerank import rerank
from src.retrieval import hybrid_search

TESTSET = Path("eval/testset.json")


def main() -> None:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    tests = json.loads(TESTSET.read_text())
    rows = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    for t in tests:
        top = rerank(t["question"], hybrid_search(t["question"], RETRIEVE_K), TOP_N)
        rows["question"].append(t["question"])
        rows["answer"].append(generate_answer(t["question"], top))
        rows["contexts"].append([c["text"] for c in top])
        rows["ground_truth"].append(t["ground_truth"])

    result = evaluate(
        Dataset.from_dict(rows),
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    print(result)


if __name__ == "__main__":
    main()
