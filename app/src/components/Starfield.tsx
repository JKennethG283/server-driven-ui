import { useMemo } from "react";

// Ambient starfield + drifting golden motes.
// Motif taken from sample.json visual_identity.animation_effects:
// "floating golden star motes that drift off when it exhales".

interface Props {
  stars?: number;
  motes?: number;
}

export default function Starfield({ stars = 46, motes = 10 }: Props) {
  const starNodes = useMemo(
    () =>
      Array.from({ length: stars }, (_, i) => {
        const size = 1 + Math.random() * 2.2;
        return {
          key: `s${i}`,
          left: Math.random() * 100,
          top: Math.random() * 100,
          size,
          dur: 3 + Math.random() * 5,
          delay: Math.random() * 5,
        };
      }),
    [stars],
  );

  const moteNodes = useMemo(
    () =>
      Array.from({ length: motes }, (_, i) => ({
        key: `m${i}`,
        left: Math.random() * 100,
        scale: 0.6 + Math.random() * 1.8,
        dur: 11 + Math.random() * 12,
        delay: Math.random() * 12,
        sway: `${Math.random() * 60 - 30}px`,
      })),
    [motes],
  );

  return (
    <div className="starfield" aria-hidden="true">
      {starNodes.map((s) => (
        <span
          key={s.key}
          className="star"
          style={{
            left: `${s.left}%`,
            top: `${s.top}%`,
            width: `${s.size}px`,
            height: `${s.size}px`,
            ["--dur" as string]: `${s.dur}s`,
            ["--delay" as string]: `${s.delay}s`,
          }}
        />
      ))}
      {moteNodes.map((m) => (
        <span
          key={m.key}
          className="mote"
          style={{
            left: `${m.left}%`,
            transform: `scale(${m.scale})`,
            ["--dur" as string]: `${m.dur}s`,
            ["--delay" as string]: `${m.delay}s`,
            ["--sway" as string]: m.sway,
          }}
        />
      ))}
    </div>
  );
}
