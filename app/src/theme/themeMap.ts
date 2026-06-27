// Element -> typography + motion mapping. The schema has no font field, so the
// Chinese zodiac element drives the typographic mood. All display/body faces are
// installed as @fontsource variable fonts (see main.tsx).

export type MotionKind = "motes" | "ripples" | "dust" | "sparks" | "drift";

export interface FontPairing {
  display: string;
  body: string;
  motion: MotionKind;
}

const MONO = '"Space Mono", ui-monospace, monospace';

export const FONT_MONO = MONO;

export const ELEMENT_FONTS: Record<string, FontPairing> = {
  Fire: {
    display: '"Fraunces Variable", Georgia, serif',
    body: '"Manrope Variable", system-ui, sans-serif',
    motion: "motes",
  },
  Water: {
    display: '"Newsreader Variable", Georgia, serif',
    body: '"Mulish Variable", system-ui, sans-serif',
    motion: "ripples",
  },
  Earth: {
    display: '"Roboto Slab Variable", Georgia, serif',
    body: '"Work Sans Variable", system-ui, sans-serif',
    motion: "dust",
  },
  Metal: {
    display: '"Space Grotesk Variable", system-ui, sans-serif',
    body: '"Inter Variable", system-ui, sans-serif',
    motion: "sparks",
  },
  Wood: {
    display: '"Bitter Variable", Georgia, serif',
    body: '"Manrope Variable", system-ui, sans-serif',
    motion: "drift",
  },
};

export const DEFAULT_FONTS: FontPairing = ELEMENT_FONTS.Fire;

export function fontsForElement(element?: string | null): FontPairing {
  if (!element) return DEFAULT_FONTS;
  const key = element.trim();
  const normalized = key.charAt(0).toUpperCase() + key.slice(1).toLowerCase();
  return ELEMENT_FONTS[normalized] ?? DEFAULT_FONTS;
}

// Pull a motion hint from the avatar's animation_effects, falling back to the
// element default.
export function motionFromEffects(
  effects: string[],
  fallback: MotionKind,
): MotionKind {
  const text = effects.join(" ").toLowerCase();
  if (/ripple|bubble|wave|tide/.test(text)) return "ripples";
  if (/spark|electric|glitch|confetti|lightning/.test(text)) return "sparks";
  if (/dust|stone|shoot|sprout|root/.test(text)) return "dust";
  if (/leaf|breeze|paper|wind|drift/.test(text)) return "drift";
  if (/mote|star|sparkle|glow/.test(text)) return "motes";
  return fallback;
}

export interface Theme {
  // Base surfaces
  night: string;
  night2: string;
  night3: string;
  // Accents (map onto existing CSS slots)
  accent: string; // --gold
  accent2: string; // --amber
  sky: string; // --sky
  violet: string; // --violet
  violetSoft: string; // --violet-soft
  cream: string; // --cream
  // Text
  text: string;
  textDim: string;
  textFaint: string;
  // Lines + effects
  line: string;
  lineStrong: string;
  glow: string;
  raise: string;
  raise2: string;
  // Typography
  fontDisplay: string;
  fontBody: string;
  fontMono: string;
  // Atmosphere
  motion: MotionKind;
  backdrop: string | null;
}
