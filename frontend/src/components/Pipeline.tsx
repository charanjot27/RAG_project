import { Fragment } from "react";
import { ArrowRight } from "./Icons";

const STEPS = [
  { n: "01", title: "Find", desc: "Searches your documents or the web for passages that might hold the answer.", dl: false },
  { n: "02", title: "Shortlist", desc: "Re-reads each passage against your question and keeps only the most relevant ones.", dl: true },
  { n: "03", title: "Draft", desc: "Writes an answer using only those passages — nothing from memory.", dl: false },
  { n: "04", title: "Check", desc: "Compares every sentence back to the sources: is this actually supported?", dl: true },
  { n: "05", title: "Show", desc: "Cites what holds up, flags what doesn't, and stays quiet when it's unsure.", dl: false },
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
