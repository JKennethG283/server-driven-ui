// Types mirror the shape of the API response in sample.json.

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface Relationship {
  strengths: string[];
  weaknesses: string[];
}

export interface SignProfile {
  sign: string;
  values: string[];
  element?: string;
  strengths: string[];
  weaknesses: string[];
  relationship: Relationship;
  rules_to_live: string[];
  personality_traits: string[];
  living_happily_tips: string[];
  success_definitions: string[];
}

export interface CharacterProfile {
  zodiac: SignProfile;
  horoscope: SignProfile;
}

export interface Symbolism {
  archetype: string;
  theme_song: string;
  core_elements: string[];
  color_meanings: Record<string, string>;
  totemic_animals: string[];
}

export interface EyeDesign {
  color: string;
  shape: string;
  glow_intensity: number;
}

export interface SignatureMarkings {
  glow: boolean;
  color: string;
  pattern: string;
  location: string;
}

export interface VisualIdentity {
  pose: string;
  style: string;
  gender: string;
  base_form: string;
  eye_design: EyeDesign;
  accessories: string[];
  color_palette: string[];
  form_variants: string[];
  animation_effects: string[];
  signature_markings: SignatureMarkings;
}

export interface NarrativeWorld {
  name: string;
  type: string;
  terrain: string[];
  time_period: string;
}

export interface NarrativeContext {
  world: NarrativeWorld;
  nemesis: string;
  allegiance: string;
  origin_story: string;
  current_mission: string;
}

export interface Scale {
  scale: number;
  description: string;
}

export interface PersonalityProfile {
  fears: string[];
  quirks: string[];
  traits: string[];
  alignment: string;
  dominant_emotion: string;
  thinking_feeling: Scale;
  introversion_extroversion: Scale;
}

export interface RepresentationProfile {
  symbolism: Symbolism;
  visual_identity: VisualIdentity;
  narrative_context: NarrativeContext;
  personality_profile: PersonalityProfile;
}

export type MotionKind = "motes" | "ripples" | "dust" | "sparks" | "drift";

export interface ThemeColors {
  night: string;
  night2: string;
  night3: string;
  accent: string;
  accent2: string;
  sky: string;
  violet: string;
  violetSoft: string;
  cream: string;
  text: string;
  textDim: string;
  textFaint: string;
}

export interface ThemeFonts {
  display: string;
  body: string;
  mono: string;
}

export interface GeneratedTheme {
  colors: ThemeColors;
  fonts: ThemeFonts;
  motion: MotionKind;
  rationale: string;
}

export interface User {
  id: number;
  created_at: string;
  updated_at: string;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  has_completed_quiz: boolean;
  has_set_goal: boolean;
  daily_reveals_used: number;
  daily_reveals_reset: string | null;
  bonus_reveals: number;
  referral_code: string;
  is_active: boolean;
  is_admin: boolean;
  last_active_at: string;
  user_id: number;
  bio: string;
  dob_year: number;
  dob_month: number;
  dob_day: number;
  daily_inspiration: string | null;
  character_profile: CharacterProfile;
  representation_profile: RepresentationProfile;
  ui_theme?: GeneratedTheme;
  avatar_picture: string;
  avatar_description: string;
  avatar_status: string;
  avatar_generation_started_at: string;
  gender: string | null;
  place_of_birth: string | null;
  current_location: string | null;
  profile_created_at: string;
  profile_updated_at: string;
}

// A potential match. NOTE: sample.json is a single-user response with no
// matches array and no score, so this shape is a documented assumption
// (see Frontend Pages Plan.md sections 6 and 13) until the backend confirms it.
export interface Match {
  user: User;
  score: number;
  shared_values: string[];
  revealed: boolean;
}
