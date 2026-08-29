import type { AskResponse } from "../types";
import FaithfulnessGauge from "./FaithfulnessGauge";
import { Check, HandStop } from "./Icons";

const STAGE_LABELS: Record<string, string> = {
  retrieval: "Retrieval",
  rerank: "Rerank",
  generation: "Generation",
  verification: "Verify",
};

function citationNode(citation: string) {
  const url = citation.split(" ")[0];
  if (url.startsWith("http")) {
    return (
      <a href={url} target="_blank" rel="noreferrer">
        {citation}
      </a>
    );
  }
  return <span>{citation}</span>;
}

export default function Results({ data }: { data: AskResponse }) {
  const grounded = data.sentences.filter((s) => s.status === "grounded").length;
  return (
    <div className="card pad" style={{ animation: "rise .4s ease both" }}>
      <div className="result-top">
        <FaithfulnessGauge score={data.faithfulness_score} />
        <div className="result-meta">
          {data.abstained ? (
            <span className="badge warn">
              <HandStop style={{ width: 15, height: 15 }} /> Abstained — not confident enough
            </span>
          ) : (
            <span className="badge ok">
              <Check style={{ width: 15, height: 15 }} /> {grounded}/{data.sentences.length} sentences verified
            </span>
          )}
          <div className="timings">
            <span className="timing">
              mode <b>{data.mode}</b>
            </span>
            {Object.entries(data.timings).map(([k, v]) => (
              <span className="timing" key={k}>
                {STAGE_LABELS[k] ?? k} <b>{v.toFixed(2)}s</b>
              </span>
            ))}
          </div>
        </div>
      </div>

      {data.abstained && (
        <div className="abstain-banner">
          <b>Holding back on this one.</b> Not enough of the answer could be backed up by the
          sources, so it chose to stay quiet rather than guess.
        </div>
      )}

      <div className="sentences">
        {data.sentences.map((s, i) => (
          <div
            className={`sentence ${s.status}`}
            key={i}
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="txt">{s.text}</div>
            <div className="meta">
              <span className={`tag ${s.status === "grounded" ? "g" : "u"}`}>
                {s.status === "grounded" ? "grounded" : "unverified"}
              </span>
              {s.citation ? (
                <span>Source: {citationNode(s.citation)}</span>
              ) : (
                <span>Not found in sources — do not trust</span>
              )}
              <span className="conf">confidence {s.confidence.toFixed(2)}</span>
            </div>
          </div>
        ))}
      </div>

      {data.sources_used.length > 0 && (
        <div className="sources">
          <h4>Sources consulted</h4>
          {data.sources_used.map((src) => {
            const isUrl = src.source.startsWith("http");
            return (
              <div className="source-item" key={src.id}>
                {isUrl ? (
                  <a href={src.source} target="_blank" rel="noreferrer">
                    {src.title || src.source}
                  </a>
                ) : (
                  <>
                    {src.source} · p.{src.page}
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
