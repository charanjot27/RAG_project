# VeriFin as the knowledge layer of FinTrace

[FinTrace](https://github.com/charanjot27/Fintrace) fuses three sources into one behavioural
dataset: a survey (stated preference), FinSim gameplay (revealed behaviour), and **VeriFin**
(verified knowledge). VeriFin's job in that system is to answer the questions a player asks
mid-game and, crucially, to report **how faithful** each answer is — that faithfulness score
becomes a feature (quality of guidance the player was exposed to) and a data-quality metric.

No code changes are needed here beyond CORS: VeriFin already exposes everything FinTrace needs.

## What FinSim calls

FinSim's in-game "Ask Mira" panel calls the existing endpoint:

```
POST /ask
{ "question": "Is a guaranteed 20% a week real?", "mode": "web" }
```

and reads two fields from the response:

| Field | Meaning | Used by FinTrace as |
|---|---|---|
| `faithfulness_score` | fraction of the answer's sentences that are grounded in sources (0–1) | `avg_guidance_faithfulness` feature |
| `sentences[].status` | per-sentence `grounded` / `unverified` | a `hallucinated` flag when any sentence is unverified |

The full response also carries `answer`, `grounded_answer`, `abstained`, `sources_used` and
stage `timings` — the "Ask Mira" panel shows the grounded answer and the faithfulness gauge.

## Running it alongside FinTrace and FinSim

Give VeriFin its own port so it doesn't collide with FinTrace (port 8000):

```bash
uvicorn api.main:app --port 8100
```

Allow the FinSim dev origin so the browser can call `/ask` (default `ALLOWED_ORIGINS=*`
already permits it; set it explicitly for a locked-down setup):

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

FinSim's bridge is pointed here with `window.VERIFIN_URL = "http://localhost:8100"`. See the
FinTrace repo's `docs/INTEGRATION.md` for the end-to-end contract.
