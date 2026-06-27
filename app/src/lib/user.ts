import type { User } from "../data/types";

const DAILY_REVEAL_LIMIT = 5;

export function fullName(user: User): string {
  return [user.first_name, user.last_name].filter(Boolean).join(" ").trim();
}

export function age(user: User): number {
  const today = new Date();
  let years = today.getFullYear() - user.dob_year;
  const beforeBirthday =
    today.getMonth() + 1 < user.dob_month ||
    (today.getMonth() + 1 === user.dob_month && today.getDate() < user.dob_day);
  if (beforeBirthday) years -= 1;
  return years;
}

export function revealsRemaining(user: User): number {
  const base = Math.max(0, DAILY_REVEAL_LIMIT - user.daily_reveals_used);
  return base + user.bonus_reveals;
}

export function revealsResetLabel(user: User): string {
  if (!user.daily_reveals_reset) return "Resets at midnight";
  const reset = new Date(user.daily_reveals_reset);
  return `Resets ${reset.toLocaleString([], {
    hour: "2-digit",
    minute: "2-digit",
    day: "numeric",
    month: "short",
  })}`;
}

// Returns a usable accent palette derived from the avatar's visual identity.
export function palette(user: User): string[] {
  return user.representation_profile.visual_identity.color_palette;
}

export function primaryAccent(user: User): string {
  return palette(user)[0] ?? "#FFD54F";
}

export function isAvatarReady(user: User): boolean {
  return user.avatar_status === "completed";
}

export function zodiacGlyph(sign: string): string {
  const glyphs: Record<string, string> = {
    Rat: "\u{1F400}",
    Ox: "\u{1F402}",
    Tiger: "\u{1F405}",
    Rabbit: "\u{1F407}",
    Dragon: "\u{1F409}",
    Snake: "\u{1F40D}",
    Horse: "\u{1F40E}",
    Goat: "\u{1F410}",
    Monkey: "\u{1F412}",
    Rooster: "\u{1F413}",
    Dog: "\u{1F415}",
    Pig: "\u{1F416}",
  };
  return glyphs[sign] ?? "\u2728";
}

export function horoscopeGlyph(sign: string): string {
  const glyphs: Record<string, string> = {
    Aries: "\u2648",
    Taurus: "\u2649",
    Gemini: "\u264A",
    Cancer: "\u264B",
    Leo: "\u264C",
    Virgo: "\u264D",
    Libra: "\u264E",
    Scorpio: "\u264F",
    Sagittarius: "\u2650",
    Capricorn: "\u2651",
    Aquarius: "\u2652",
    Pisces: "\u2653",
  };
  return glyphs[sign] ?? "\u2728";
}
