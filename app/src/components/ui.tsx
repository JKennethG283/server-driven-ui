import type { ReactNode } from "react";

export function SectionLabel({ children }: { children: ReactNode }) {
  return <div className="section-label">{children}</div>;
}

export function Chips({ items, solid }: { items: string[]; solid?: boolean }) {
  return (
    <div className="chips">
      {items.map((item) => (
        <span key={item} className={solid ? "chip solid" : "chip"}>
          {item}
        </span>
      ))}
    </div>
  );
}

// A meter for the 0..1 personality scales in personality_profile.
export function Meter({
  leftLabel,
  rightLabel,
  value,
}: {
  leftLabel: string;
  rightLabel: string;
  value: number;
}) {
  const pct = Math.round(value * 100);
  return (
    <div className="meter">
      <div className="meter-head">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>
      <div className="meter-track">
        <span
          className="meter-dot"
          style={{ left: `${Math.min(96, Math.max(4, pct))}%` }}
        />
      </div>
    </div>
  );
}

export function ListCard({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div className="card">
      <h3 className="display h-md" style={{ marginBottom: 10 }}>
        {title}
      </h3>
      <ul className="trait-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
