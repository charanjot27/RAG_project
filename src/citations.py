"""Component 7 — Citations, abstention & final output.

Assemble the verified sentences into the final, color-coded, cited answer,
compute the faithfulness score (share of sentences the sources support), and
act on that score:

  * abstention   — if faithfulness is below ABSTAIN_THRESHOLD, refuse rather
                   than serve an answer we can't stand behind ("knows when it
                   doesn't know").
  * self-correction — also return a `grounded_answer` containing ONLY the
                   verified sentences, so the unsupported ones are dropped.
"""

from __future__ import annotations

from src.config import ABSTAIN_THRESHOLD

ABSTAIN_MESSAGE = (
    "I can't confidently answer this from the available sources — too much of the "
    "draft answer could not be verified. (Try rephrasing, adding sources, or "
    "switching RETRIEVAL_MODE.)"
)


def build_output(verified: list[dict], abstain_threshold: float = ABSTAIN_THRESHOLD) -> dict:
    faithful = sum(1 for v in verified if v["label"] == "grounded")
    faithfulness = round(faithful / max(len(verified), 1), 3)

    rendered = []
    for v in verified:
        if v["label"] == "grounded" and v.get("source"):
            src = v["source"]
            rendered.append(
                {
                    "text": v["sentence"],
                    "status": "grounded",
                    "citation": f"{src['source']} p.{src['page']}",
                    "confidence": round(v["score"], 2),
                }
            )
        else:
            rendered.append(
                {
                    "text": v["sentence"],
                    "status": "unverified",
                    "citation": None,
                    "confidence": round(v["score"], 2),
                }
            )

    # Self-correction: the answer with only the verified sentences kept.
    grounded_answer = " ".join(s["text"] for s in rendered if s["status"] == "grounded")

    # Abstention: refuse when faithfulness is below the configured floor.
    abstained = bool(verified) and faithfulness < abstain_threshold

    return {
        "faithfulness_score": faithfulness,
        "abstained": abstained,
        "answer": ABSTAIN_MESSAGE if abstained else (grounded_answer or ABSTAIN_MESSAGE),
        "grounded_answer": grounded_answer,
        "sentences": rendered,
    }
