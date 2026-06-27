import type { User } from "../data/types";
import type { Theme } from "./themeMap";
import { fontsForElement, motionFromEffects, FONT_MONO } from "./themeMap";
import {
  mostVivid,
  secondAccent,
  coolest,
  purplish,
  deriveNight,
  deriveText,
  ensureReadable,
  glowFor,
  rgba,
} from "./color";

const FALLBACK_ACCENT = "#FFD54F";

// Deterministically turn a schema-conforming User into a full Theme.
export function deriveTheme(user: User): Theme {
  const vis = user.representation_profile.visual_identity;
  const marks = vis.signature_markings;
  const element = user.character_profile.zodiac.element;

  const palette = vis.color_palette ?? [];

  // Accent: prefer the glowing signature marking, else the most vivid palette hue.
  const rawAccent =
    marks.glow && marks.color ? marks.color : mostVivid(palette, FALLBACK_ACCENT);

  const night = deriveNight(palette, rawAccent);
  const accent = ensureReadable(rawAccent, night.night);
  const accent2 = secondAccent(palette, accent, vis.eye_design.color);
  const sky = coolest(palette, accent2);
  const violet = purplish(palette, night.night3);
  const violetSoft = secondAccent(palette, violet, sky);
  const text = deriveText(accent, night.night);
  const cream = text.text;

  const fonts = fontsForElement(element);
  const motion = motionFromEffects(vis.animation_effects ?? [], fonts.motion);

  const avatarReady = user.avatar_status === "completed";

  return {
    night: night.night,
    night2: night.night2,
    night3: night.night3,
    accent,
    accent2,
    sky,
    violet,
    violetSoft,
    cream,
    text: text.text,
    textDim: text.textDim,
    textFaint: text.textFaint,
    line: rgba(cream, 0.1),
    lineStrong: rgba(cream, 0.18),
    glow: glowFor(accent),
    raise: rgba(cream, 0.04),
    raise2: rgba(cream, 0.07),
    fontDisplay: fonts.display,
    fontBody: fonts.body,
    fontMono: FONT_MONO,
    motion,
    backdrop: avatarReady ? user.avatar_picture : null,
  };
}

// A short, human-readable summary used by the switcher UI.
export function themeSummary(user: User): string {
  const element = user.character_profile.zodiac.element ?? "Fire";
  return `${user.character_profile.zodiac.sign} · ${element}`;
}
