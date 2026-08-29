"""Component 7 — Citations & final output.

Assemble the verified sentences into the final, color-coded, cited
answer, and compute the faithfulness score (share of sentences the
sources actually support).
"""

from __future__ import annotations


def build_output(verified: list[dict]) -> dict:
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
    return {"faithfulness_score": faithfulness, "sentences": rendered}
