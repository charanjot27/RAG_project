import { useEffect, useState } from "react";
import AskPanel from "./components/AskPanel";
import Pipeline from "./components/Pipeline";
import {
  ArrowRight,
  Bolt,
  Check,
  Gauge,
  GitHub,
  Globe,
  HandStop,
  Link,
  Moon,
  ShieldCheck,
  Sun,
} from "./components/Icons";

const FEATURES = [
  { icon: ShieldCheck, title: "Sentence-level verification", body: "A natural-language-inference model checks every sentence against the retrieved sources. Grounded sentences are cited; unsupported ones are flagged." },
  { icon: Gauge, title: "Measurable faithfulness", body: "Each answer carries a faithfulness score — the share of sentences the sources actually support. A number you can track, not a vibe." },
  { icon: HandStop, title: "Knows when to abstain", body: "Below a confidence threshold, VeriFin declines to answer rather than risk a fabricated response — the opposite of a confidently-wrong model." },
  { icon: Globe, title: "Documents or the open web", body: "Ground answers in a private document index or in live web search. The verification and citations work identically for both." },
  { icon: Bolt, title: "Built to scale", body: "Hybrid retrieval, a cross-encoder reranker, and a self-building web cache keep responses fast as the corpus grows." },
  { icon: Link, title: "Auditable by design", body: "Every grounded claim links back to its exact source, so answers can be checked line by line instead of taken on trust." },
];

const CHECKLIST_A = [
  "Grounded answers with sentence-level citations",
  "A faithfulness score on every response",
  "Abstention when confidence is too low",
  "Works over private documents or the open internet",
];
const CHECKLIST_B = [
  "Turns an opaque model into an auditable assistant",
  "Reviewers can trust green and scrutinise red",
  "Scales from one document to the whole web",
  "Measurable, reproducible, production-oriented",
];

const REPO_URL = "https://github.com/charanjot27/RAG_project";

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
          <a className="nav-cta" href={REPO_URL} target="_blank" rel="noreferrer">
            <GitHub /> GitHub
          </a>
          <button className="icon-btn" onClick={toggle} title="Toggle theme" aria-label="Toggle theme">
            {theme === "dark" ? <Sun /> : <Moon />}
          </button>
        </div>
      </nav>

      {/* Hero */}
      <header className="hero container">
        <span className="pill">
          <span className="dot" /> Self-auditing retrieval-augmented generation
        </span>
        <h1>
          Verifiable AI answers,
          <br />
          <span className="accent">grounded and cited.</span>
        </h1>
        <p className="lead">
          VeriFin answers from real sources, cites every grounded sentence, and flags the
          unverified ones — with a measurable faithfulness score. Built for domains where a
          confident wrong answer is unacceptable.
        </p>
        <div className="cta-row">
          <a className="btn btn-primary" href="#demo">
            Try the live demo <ArrowRight />
          </a>
          <a className="btn btn-ghost" href="#how">How it works</a>
        </div>
      </header>

      {/* Demo */}
      <section className="section container" id="demo">
        <div className="section-head">
          <div className="eyebrow">Live demo</div>
          <h2>Ask a question — watch it verify itself</h2>
          <p>
            Choose a source, ask a question, and every sentence returns grounded and cited, or
            flagged for review. Ask something outside the sources to see it decline rather than
            fabricate.
          </p>
        </div>
        <AskPanel />
      </section>

      {/* How it works */}
      <section className="section container" id="how">
        <div className="section-head">
          <div className="eyebrow">The pipeline</div>
          <h2>Five stages, three of them learned</h2>
          <p>Retrieval finds the evidence, the reranker sharpens it, the model drafts the answer — and the verifier audits every sentence.</p>
        </div>
        <Pipeline />
        <div className="grid" style={{ marginTop: 28 }}>
          {FEATURES.map((f) => {
            const Icon = f.icon;
            return (
              <div className="feature" key={f.title}>
                <div className="ic"><Icon /></div>
                <h3>{f.title}</h3>
                <p>{f.body}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Benchmark */}
      <section className="section container" id="benchmark">
        <div className="section-head">
          <div className="eyebrow">Measured, not claimed</div>
          <h2>It catches hallucinations a naive system emits</h2>
          <p>
            On a benchmark of questions that sound answerable but aren&rsquo;t in the sources, a
            naive pipeline answers confidently every time. VeriFin declines.
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
              <small>VeriFin hallucination rate — every one caught</small>
            </div>
          </div>
          <p className="mono-dim" style={{ textAlign: "center", marginTop: 18 }}>
            reproduce: python -m eval.hallucination_bench
          </p>
        </div>
      </section>

      {/* About */}
      <section className="section container" id="about">
        <div className="section-head">
          <div className="eyebrow">About</div>
          <h2>What it is, and why it matters</h2>
        </div>
        <div className="about-grid">
          <div className="card pad about">
            <h3>What it does</h3>
            <p>
              VeriFin is a question-answering system that speaks only from a trusted set of
              documents — or the live web — and then audits its own answer. It splits the
              response into sentences and checks each against the retrieved evidence with a
              natural-language-inference model. Supported sentences are cited; unsupported ones
              are flagged, and if too much is unverifiable, it declines to answer.
            </p>
            <ul className="checklist">
              {CHECKLIST_A.map((c) => (
                <li key={c}><Check /> {c}</li>
              ))}
            </ul>
          </div>
          <div className="card pad about">
            <h3>Why it&rsquo;s used</h3>
            <p>
              Language models hallucinate — they state incorrect facts with full confidence —
              which makes them risky for finance, law, healthcare, and compliance, where a wrong
              answer has real consequences. The missing piece isn&rsquo;t a larger model; it is a
              trust layer that proves, per sentence, what is and isn&rsquo;t backed by evidence.
            </p>
            <ul className="checklist">
              {CHECKLIST_B.map((c) => (
                <li key={c}><Check /> {c}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container footer-inner">
          <div className="brand"><span className="logo">V</span> VeriFin</div>
          <div>Green — backed by a source · Red — unverified. Grounded answers only.</div>
        </div>
      </footer>
    </>
  );
}
