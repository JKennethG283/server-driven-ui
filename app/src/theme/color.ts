import chroma from "chroma-js";

const HEX = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/;

export function isHex(value: string): boolean {
  return HEX.test(value);
}

export function validHexes(values: string[]): string[] {
  return values.filter(isHex);
}

export function safe(value: string, fallback: string): chroma.Color {
  try {
    return chroma(isHex(value) ? value : fallback);
  } catch {
    return chroma(fallback);
  }
}

// The most "vivid" color: high saturation in a usable lightness band.
export function mostVivid(colors: string[], fallback: string): string {
  const usable = validHexes(colors)
    .map((c) => chroma(c))
    .filter((c) => {
      const l = c.get("hsl.l");
      return l >= 0.32 && l <= 0.82;
    });
  const pool = usable.length ? usable : validHexes(colors).map((c) => chroma(c));
  if (!pool.length) return fallback;
  return pool
    .slice()
    .sort((a, b) => (b.get("hsl.s") || 0) - (a.get("hsl.s") || 0))[0]
    .hex();
}

// A second vivid color whose hue is meaningfully different from `from`.
export function secondAccent(
  colors: string[],
  from: string,
  fallback: string,
): string {
  const fromHue = safe(from, fallback).get("hsl.h") || 0;
  const candidates = validHexes(colors)
    .map((c) => chroma(c))
    .filter((c) => {
      const l = c.get("hsl.l");
      const hue = c.get("hsl.h") || 0;
      const diff = Math.min(Math.abs(hue - fromHue), 360 - Math.abs(hue - fromHue));
      return l >= 0.3 && l <= 0.85 && diff > 18;
    })
    .sort((a, b) => (b.get("hsl.s") || 0) - (a.get("hsl.s") || 0));
  return candidates.length ? candidates[0].hex() : from;
}

// Pick the coolest (bluest) palette color for the "sky" slot.
export function coolest(colors: string[], fallback: string): string {
  const candidates = validHexes(colors)
    .map((c) => chroma(c))
    .filter((c) => {
      const h = c.get("hsl.h") || 0;
      return h >= 170 && h <= 280;
    })
    .sort((a, b) => (b.get("hsl.l") || 0) - (a.get("hsl.l") || 0));
  return candidates.length ? candidates[0].hex() : fallback;
}

// Pick a purple/violet-ish color for the violet slot.
export function purplish(colors: string[], fallback: string): string {
  const candidates = validHexes(colors)
    .map((c) => chroma(c))
    .filter((c) => {
      const h = c.get("hsl.h") || 0;
      return h >= 250 && h <= 320;
    })
    .sort((a, b) => (b.get("hsl.s") || 0) - (a.get("hsl.s") || 0));
  return candidates.length ? candidates[0].hex() : fallback;
}

// Build a dark, slightly saturated base from the palette's deepest hue.
export function deriveNight(colors: string[], accent: string): {
  night: string;
  night2: string;
  night3: string;
} {
  const valid = validHexes(colors).map((c) => chroma(c));
  const base = valid.length
    ? valid.slice().sort((a, b) => a.luminance() - b.luminance())[0]
    : chroma(accent);

  const hue = base.get("hsl.h") || chroma(accent).get("hsl.h") || 265;
  const sat = Math.max(base.get("hsl.s") || 0.4, 0.38);

  const shade = (l: number) => chroma.hsl(hue, Math.min(sat, 0.6), l).hex();
  return {
    night: shade(0.07),
    night2: shade(0.11),
    night3: shade(0.17),
  };
}

// Near-white text, faintly tinted by the accent hue for cohesion.
export function deriveText(accent: string, night: string): {
  text: string;
  textDim: string;
  textFaint: string;
} {
  const text = chroma.mix("#ffffff", accent, 0.05, "rgb").hex();
  return {
    text,
    textDim: chroma.mix(text, night, 0.34, "rgb").hex(),
    textFaint: chroma.mix(text, night, 0.56, "rgb").hex(),
  };
}

export function rgba(value: string, alpha: number): string {
  const [r, g, b] = chroma(value).rgb();
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function glowFor(accent: string): string {
  return `0 0 0 1px ${rgba(accent, 0.35)}, 0 12px 40px -12px ${rgba(accent, 0.4)}`;
}

// Ensure an accent reads on a dark base; lighten if it is too dim.
export function ensureReadable(accent: string, night: string): string {
  let c = chroma(accent);
  let guard = 0;
  while (chroma.contrast(c, night) < 3 && guard < 8) {
    c = c.brighten(0.4);
    guard += 1;
  }
  return c.hex();
}
