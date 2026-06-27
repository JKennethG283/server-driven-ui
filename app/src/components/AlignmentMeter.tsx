// Signature element: the matching score drawn as a constellation whose stars
// light up in proportion to alignment. This is the visual home for the app's
// core "matching score" concept.

interface Props {
  score: number;
  size?: number;
}

const POINTS = [
  { x: 12, y: 70 },
  { x: 30, y: 40 },
  { x: 46, y: 58 },
  { x: 62, y: 26 },
  { x: 78, y: 48 },
  { x: 90, y: 20 },
];

export default function AlignmentMeter({ score, size = 120 }: Props) {
  const lit = Math.round((score / 100) * POINTS.length);

  return (
    <div className="alignment" style={{ width: size }}>
      <svg viewBox="0 0 100 90" className="alignment-svg" aria-hidden="true">
        {POINTS.slice(0, -1).map((p, i) => {
          const next = POINTS[i + 1];
          const active = i + 1 < lit;
          return (
            <line
              key={`l${i}`}
              x1={p.x}
              y1={p.y}
              x2={next.x}
              y2={next.y}
              className={active ? "edge on" : "edge"}
            />
          );
        })}
        {POINTS.map((p, i) => (
          <circle
            key={`p${i}`}
            cx={p.x}
            cy={p.y}
            r={i < lit ? 3.4 : 2}
            className={i < lit ? "node on" : "node"}
          />
        ))}
      </svg>
      <div className="alignment-score">
        <span className="display">{score}</span>
        <span className="mono">% aligned</span>
      </div>
    </div>
  );
}
