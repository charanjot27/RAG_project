interface Props {
  score: number; // 0..1
}

export default function FaithfulnessGauge({ score }: Props) {
  const pct = Math.round(score * 100);
  const color = pct >= 80 ? "var(--green)" : pct >= 50 ? "var(--amber)" : "var(--red)";
  return (
    <div
      className="gauge"
      style={{ ["--p" as string]: pct, ["--gcolor" as string]: color }}
      role="img"
      aria-label={`Faithfulness score ${pct} percent`}
    >
      <div style={{ textAlign: "center" }}>
        <div className="val" style={{ color }}>
          {pct}%
        </div>
        <div className="lbl">Faithful</div>
      </div>
    </div>
  );
}
