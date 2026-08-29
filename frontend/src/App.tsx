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
  { icon: ShieldCheck, title: "It checks every sentence", body: "Before you ever see an answer, each line is compared against the sources it came from. The ones that hold up get a citation; the rest get flagged." },
  { icon: Gauge, title: "One honest number", body: "Every answer shows how much of it is actually backed by the sources — a score you can point to, not a gut feeling." },
  { icon: HandStop, title: "It admits when it's unsure", body: "If it can't back up enough of an answer, it says so instead of inventing something. That's really the whole idea." },
  { icon: Globe, title: "Your files or the web", body: "Point it at your own documents, or let it search the live web. Either way, every claim still gets checked and linked." },
  { icon: Bolt, title: "It keeps up as it grows", body: "Smart search, a shortlisting step, and a cache keep answers quick whether you have ten documents or ten thousand." },
  { icon: Link, title: "Nothing to take on faith", body: "Every backed-up sentence links to exactly where it came from, so anyone can double-check it in a few seconds." },
];

const CHECKLIST_A = [
  "Every claim has a source you can open",
  "One clear score for how grounded it is",
  "Stays quiet when it isn't sure",
  "Works on your files or the open web",
];
const CHECKLIST_B = [
  "Turns a black box into something you can check",
  "Trust the green, question the red",
  "Handles one document or the whole web",
  "Simple to run, easy to show people",
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
            <a href="#demo">Try it</a>
            <a href="#how">How it works</a>
            <a href="#benchmark">Does it work?</a>
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
          <span className="dot" /> It would rather stay quiet than make something up
        </span>
        <h1>
          Answers you can check,
          <br />
          <span className="accent">line by line.</span>
        </h1>
        <p className="lead">
          Most chatbots sound just as confident when they&rsquo;re wrong as when they&rsquo;re
          right. VeriFin answers only from real sources, shows you where each sentence came
          from, and clearly marks anything it couldn&rsquo;t back up — so you always know what to
          trust.
        </p>
        <div className="cta-row">
          <a className="btn btn-primary" href="#demo">
            Try it now <ArrowRight />
          </a>
          <a className="btn btn-ghost" href="#how">See how it works</a>
        </div>
      </header>

      {/* Demo */}
      <section className="section container" id="demo">
        <div className="section-head">
          <div className="eyebrow">Try it</div>
          <h2>Ask something — then watch it check its own work</h2>
          <p>
            Choose where it should look, ask a question, and every sentence comes back either
            backed by a source or marked unverified. Ask about something it doesn&rsquo;t have,
            and it&rsquo;ll tell you — instead of guessing.
          </p>
        </div>
        <AskPanel />
      </section>

      {/* How it works */}
      <section className="section container" id="how">
        <div className="section-head">
          <div className="eyebrow">Under the hood</div>
          <h2>How an answer gets built</h2>
          <p>Five steps: find the right material, keep the best of it, write only from that, then check every line before it reaches you.</p>
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
          <div className="eyebrow">Does it actually work?</div>
          <h2>It catches the made-up answers</h2>
          <p>
            We gave it a set of questions that sound answerable but aren&rsquo;t in the sources.
            A normal setup confidently answered every single one. This one didn&rsquo;t.
          </p>
        </div>
        <div className="card pad">
          <div className="bench">
            <div className="metric bad">
              <div className="big">100%</div>
              <small>of the trick questions a normal setup answered anyway</small>
            </div>
            <div className="metric good">
              <div className="big">0%</div>
              <small>slipped past VeriFin — it caught every one</small>
            </div>
          </div>
          <p className="mono-dim" style={{ textAlign: "center", marginTop: 18 }}>
            check it yourself: python -m eval.hallucination_bench
          </p>
        </div>
      </section>

      {/* About */}
      <section className="section container" id="about">
        <div className="section-head">
          <div className="eyebrow">About</div>
          <h2>What it is, and why I built it</h2>
        </div>
        <div className="about-grid">
          <div className="card pad about">
            <h3>What it does</h3>
            <p>
              VeriFin only answers from material it can actually point to — your own documents,
              or pages it finds on the web. It breaks its own answer into sentences and checks
              each one against that material. Sentences it can back up get a citation; the ones
              it can&rsquo;t get flagged. And if too little holds up, it would rather stay quiet
              than take a guess.
            </p>
            <ul className="checklist">
              {CHECKLIST_A.map((c) => (
                <li key={c}><Check /> {c}</li>
              ))}
            </ul>
          </div>
          <div className="card pad about">
            <h3>Why it matters</h3>
            <p>
              AI is great at sounding sure — even when it&rsquo;s wrong. That&rsquo;s fine for
              brainstorming, but risky for anything that actually matters, like money, law, or
              health. The fix isn&rsquo;t a bigger model. It&rsquo;s being able to see, line by
              line, what&rsquo;s genuinely backed by evidence and what isn&rsquo;t — and that&rsquo;s
              exactly what this shows you.
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
          <div>Green means a source backs it up. Red means don&rsquo;t trust it yet.</div>
        </div>
      </footer>
    </>
  );
}
