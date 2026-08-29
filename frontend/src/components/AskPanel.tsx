import { useState } from "react";
import type { AskResponse, Mode } from "../types";
import { ask } from "../api";
import Results from "./Results";

const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: "local", label: "My Docs", hint: "Answer from your indexed documents" },
  { id: "web", label: "Live Web", hint: "Search the internet, verify every sentence" },
  { id: "web_cached", label: "Web + Cache", hint: "Web search cached for instant repeats" },
];

const SAMPLES = [
  "What is the penalty for late tax filing?",
  "What is the standard deduction for a single filer?",
  "What is the capital of France?",
];

export default function AskPanel() {
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<Mode>("local");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AskResponse | null>(null);

  async function run(q: string) {
    const query = q.trim();
    if (!query || loading) return;
    setLoading(true);
    setError(null);
    try {
      setData(await ask(query, mode));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  const active = MODES.find((m) => m.id === mode)!;

  return (
    <div className="demo">
      <div className="card pad">
        <div className="ask-head">
          <h3>Ask a question</h3>
          <div className="modes" role="tablist" aria-label="Retrieval mode">
            {MODES.map((m) => (
              <button
                key={m.id}
                className={`mode-btn ${mode === m.id ? "active" : ""}`}
                onClick={() => setMode(m.id)}
                title={m.hint}
                role="tab"
                aria-selected={mode === m.id}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
        <p className="muted" style={{ margin: "4px 0 0", fontSize: 13.5 }}>
          {active.hint}
        </p>

        <div className="ask-row">
          <input
            className="ask-input"
            value={question}
            placeholder="e.g. What is the penalty for late tax filing?"
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run(question)}
          />
          <button className="btn btn-primary" onClick={() => run(question)} disabled={loading}>
            {loading ? "Verifying…" : "Ask"}
          </button>
        </div>

        <div className="samples">
          {SAMPLES.map((s) => (
            <button key={s} className="chip" onClick={() => { setQuestion(s); run(s); }}>
              {s}
            </button>
          ))}
        </div>

        {error && (
          <div className="error-box">
            <b>Couldn’t reach the API.</b> {error}
            <br />
            <span style={{ opacity: 0.85 }}>
              Make sure the backend is running: <code>uvicorn api.main:app --port 8000</code>
            </span>
          </div>
        )}
      </div>

      {data && <Results data={data} />}
    </div>
  );
}
