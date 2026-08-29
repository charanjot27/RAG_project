import { Fragment } from "react";
import { ArrowRight } from "./Icons";

const STEPS = [
  { n: "01", title: "Retrieve", desc: "Hybrid search (meaning + keywords) or live web finds candidate passages.", dl: false },
  { n: "02", title: "Rerank", desc: "A cross-encoder re-reads each candidate with the question and keeps the best.", dl: true },
  { n: "03", title: "Generate", desc: "The LLM writes an answer using only the retrieved sources.", dl: false },
  { n: "04", title: "Verify", desc: "An NLI model checks every sentence: is it entailed by the sources?", dl: true },
  { n: "05", title: "Cite & flag", desc: "Green = cited to a source. Red = unverified. Below threshold = abstain.", dl: false },
];

export default function Pipeline() {
  return (
    <div className="pipe">
      {STEPS.map((s, i) => (
        <Fragment key={s.n}>
          <div className="pstep">
            <div className="n">{s.n}</div>
            <h4>{s.title}</h4>
            <p>{s.desc}</p>
            {s.dl && <span className="dl">deep learning</span>}
          </div>
          {i < STEPS.length - 1 && (
            <div className="parrow" aria-hidden>
              <ArrowRight />
            </div>
          )}
        </Fragment>
      ))}
    </div>
  );
}
