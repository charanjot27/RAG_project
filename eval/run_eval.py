"""RAGAS evaluation over eval/testset.json. Run: python -m eval.run_eval"""

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
