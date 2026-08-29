"""Hallucination benchmark — the number that proves the system works.

Runs a set of "trap" questions (eval/traps.json), some answerable from the
sources and some deliberately NOT, and compares two systems:

  * NAIVE  — retrieve + generate, then trust the answer (no verification).
  * VeriFin — the same, plus the NLI faithfulness check + abstention.

For each unanswerable question, a confident answer is a HALLUCINATION. VeriFin
should flag/abstain on those. The headline metric is the hallucination
**catch-rate**: of the unsupported questions, how many VeriFin refused to answer
confidently.

    python -m eval.hallucination_bench

Uses whatever RETRIEVAL_MODE / LLM you've configured. For a clean, offline demo,
use RETRIEVAL_MODE=local with the sample doc ingested (see README).
"""

from __future__ import annotations

import json
from pathlib import Path

from src.citations import build_output
from src.config import TOP_N
from src.generate import generate_answer, generate_answer_naive
from src.rerank import rerank
from src.verify import split_sentences, verify_answer

TRAPS = Path("eval/traps.json")
# For the benchmark we force an abstention floor so "confident answer" is well defined.
BENCH_ABSTAIN = 0.5


def _retrieve(query: str) -> list[dict]:
    from src.pipeline import _retrieve as retrieve

    return retrieve(query)


def _naive_answers_confidently(answer: str) -> bool:
    """Naive system 'answers' whenever it doesn't explicitly say it can't."""
    a = answer.strip().lower()
    return bool(a) and "do not cover" not in a and "cannot" not in a and "can't" not in a


def main() -> None:
    traps = json.loads(TRAPS.read_text())

    naive_hallucinations = 0
    verifin_hallucinations = 0
    unsupported = 0
    rows = []

    for t in traps:
        q = t["question"]
        supported = t["answerable_from_sources"]
        top = rerank(q, _retrieve(q), TOP_N)

        # NAIVE: unconstrained generator, then trust whatever it says.
        naive_draft = generate_answer_naive(q, top)
        naive_confident = _naive_answers_confidently(naive_draft)

        # VeriFin: grounded generator + verify + abstain.
        draft = generate_answer(q, top)
        verified = verify_answer(draft, top)
        out = build_output(verified, abstain_threshold=BENCH_ABSTAIN)
        verifin_confident = (not out["abstained"]) and bool(out["grounded_answer"])

        if not supported:
            unsupported += 1
            naive_hallucinations += int(naive_confident)
            verifin_hallucinations += int(verifin_confident)

        rows.append(
            {
                "question": q,
                "supported": supported,
                "naive_confident": naive_confident,
                "verifin_confident": verifin_confident,
                "faithfulness": out["faithfulness_score"],
                "sentences_checked": len(split_sentences(draft)),
            }
        )

    print("\n=== Hallucination benchmark ===")
    for r in rows:
        tag = "OK " if r["supported"] else "TRAP"
        print(
            f"[{tag}] naive={'ANSWER' if r['naive_confident'] else 'refuse':6} "
            f"verifin={'ANSWER' if r['verifin_confident'] else 'refuse':6} "
            f"faith={r['faithfulness']:.2f}  {r['question']}"
        )

    if unsupported:
        naive_rate = naive_hallucinations / unsupported
        verifin_rate = verifin_hallucinations / unsupported
        caught = (naive_hallucinations - verifin_hallucinations) / max(naive_hallucinations, 1)
        print("\n--- On unsupported (trap) questions ---")
        print(f"Naive hallucination rate:   {naive_rate:.0%} "
              f"({naive_hallucinations}/{unsupported})")
        print(f"VeriFin hallucination rate: {verifin_rate:.0%} "
              f"({verifin_hallucinations}/{unsupported})")
        print(f"Hallucinations caught by VeriFin: {caught:.0%}")


if __name__ == "__main__":
    main()
