import { useEffect, useState } from "react";
import AskPanel from "./components/AskPanel";
import Pipeline from "./components/Pipeline";

const FEATURES = [
  { ic: "🛡️", title: "Sentence-level verification", body: "An NLI model checks every sentence against the sources. Grounded ones turn green; unsupported ones are flagged red." },
  { ic: "📊", title: "Measurable faithfulness", body: "Every answer carries a faithfulness score — the share of sentences the sources actually support. No vibes, a number." },
  { ic: "🙅", title: "Knows when it doesn’t know", body: "Below a confidence threshold, VeriFin abstains instead of guessing — the opposite of a confidently-wrong chatbot." },
  { ic: "🌐", title: "Your docs or the whole web", body: "Answer from a private document index or live web search — same verification, citations become real URLs." },
  { ic: "⚡", title: "Scalable by design", body: "Hybrid retrieval + a cross-encoder reranker + a self-building web cache keep it fast as the corpus grows." },
  { ic: "🔗", title: "Always cited", body: "Every grounded claim links back to its exact source and page, so answers are auditable, not opaque." },
];

function useTheme() {
  const [theme, setTheme] = useState<string>(() => {
    try {
      return localStorage.getItem("verifin-theme") || "dark";
    } catch {
      return "dark";
    }
  });
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("verifin-theme", theme);
    } catch {
      /* ignore */
    }
  }, [theme]);
  return { theme, toggle: () => setTheme((t) => (t === "dark" ? "light" : "dark")) };
}

export default function App() {
  const { theme, toggle } = useTheme();

  return (
    <>
      <nav className="nav">
        <div className="nav-inner">
          <div className="brand">
            <span className="logo">V</span> VeriFin
          </div>
          <div className="nav-links">
            <a href="#demo">Demo</a>
            <a href="#how">How it works</a>
            <a href="#benchmark">Results</a>
            <a href="#about">About</a>
          </div>
          <button className="icon-btn" onClick={toggle} title="Toggle theme" aria-label="Toggle theme">
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
        </div>
      </nav>

      {/* Hero */}
      <header className="hero container">
        <span className="pill">
          <span className="dot" /> Self-auditing RAG · every sentence verified
        </span>
        <h1>
          AI answers that <span className="grad">flag their own lies.</span>
        </h1>
        <p className="lead">
          VeriFin answers from real sources, cites every grounded sentence, and flags the
          unverified ones in red — with a measurable faithfulness score. Built for
          high-stakes domains where a confident wrong answer is unacceptable.
        </p>
        <div className="cta-row">
          <a className="btn btn-primary" href="#demo">Try the live demo</a>
          <a className="btn btn-ghost" href="#how">See how it works</a>
        </div>
      </header>

      {/* Demo */}
      <section className="section container" id="demo">
        <div className="section-head">
          <div className="eyebrow">Live demo</div>
          <h2>Ask it anything — then watch it check itself</h2>
          <p>
            Pick a source mode, ask a question, and every sentence comes back grounded (green,
            cited) or flagged (red). Try the “capital of France” sample to see it refuse to
            hallucinate.
          </p>
        </div>
        <AskPanel />
      </section>

      {/* How it works */}
      <section className="section container" id="how">
        <div className="section-head">
          <div className="eyebrow">The pipeline</div>
          <h2>Five stages, three of them deep learning</h2>
          <p>Retrieval finds it, the reranker sharpens it, the LLM writes it — and the verifier audits it.</p>
        </div>
        <Pipeline />
        <div className="grid" style={{ marginTop: 28 }}>
          {FEATURES.map((f) => (
            <div className="card pad feature" key={f.title}>
              <div className="ic">{f.ic}</div>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Benchmark */}
      <section className="section container" id="benchmark">
        <div className="section-head">
          <div className="eyebrow">Proof, not vibes</div>
          <h2>It catches hallucinations a normal RAG emits</h2>
          <p>
            On a benchmark of “trap” questions that sound answerable but aren’t in the sources,
            a naive system answers confidently every time. VeriFin refuses.
          </p>
        </div>
        <div className="card pad">
          <div className="bench">
            <div className="metric bad">
              <div className="big">100%</div>
              <small>Naive RAG hallucination rate on trap questions</small>
            </div>
            <div className="metric good">
              <div className="big">0%</div>
              <small>VeriFin hallucination rate — 100% of them caught</small>
            </div>
          </div>
          <p className="muted" style={{ textAlign: "center", marginTop: 16, fontSize: 13.5 }}>
            Reproduce it yourself: <code>python -m eval.hallucination_bench</code>
          </p>
        </div>
      </section>

      {/* About */}
      <section className="section container" id="about">
        <div className="section-head">
          <div className="eyebrow">About</div>
          <h2>What it is & why it matters</h2>
        </div>
        <div className="about-grid">
          <div className="card pad about">
            <h3>What it does</h3>
            <p>
              VeriFin is a question-answering system that only speaks from a trusted set of
              documents — or the live web — and then audits its own answer. It splits the
              response into sentences and checks each one against the retrieved evidence with a
              natural-language-inference model. Supported sentences are cited; unsupported ones
              are flagged, and if too much is unverifiable, it declines to answer.
            </p>
            <ul className="checklist">
              <li>Grounded answers with clickable, sentence-level citations</li>
              <li>A faithfulness score on every response</li>
              <li>Abstention when confidence is too low</li>
              <li>Works over private documents or the open internet</li>
            </ul>
          </div>
          <div className="card pad about">
            <h3>Why it’s used</h3>
            <p>
              Large language models hallucinate — they state made-up facts with total
              confidence — which makes them unsafe for finance, law, healthcare, and compliance,
              where a wrong answer has real consequences. The missing piece isn’t a smarter
              model; it’s a <b>trust layer</b> that proves, per sentence, what is and isn’t
              backed by evidence.
            </p>
            <ul className="checklist">
              <li>Turns an opaque chatbot into an auditable assistant</li>
              <li>Lets reviewers trust green and scrutinize red</li>
              <li>Scales from one PDF to the whole web without losing verification</li>
              <li>Measurable, reproducible, and demo-ready</li>
            </ul>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container footer-inner">
          <div>VeriFin — self-auditing RAG assistant.</div>
          <div>Green = backed by a source · Red = unverified, do not trust.</div>
        </div>
      </footer>
    </>
  );
}
