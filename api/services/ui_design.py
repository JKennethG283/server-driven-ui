"""Gemini-backed UI design generation from a full user profile JSON."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


HEX = r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
MOTION_KINDS = {"motes", "ripples", "dust", "sparks", "drift"}

FONT_STACKS = {
    "Fraunces": '"Fraunces Variable", Georgia, serif',
    "Newsreader": '"Newsreader Variable", Georgia, serif',
    "Roboto Slab": '"Roboto Slab Variable", Georgia, serif',
    "Space Grotesk": '"Space Grotesk Variable", system-ui, sans-serif',
    "Bitter": '"Bitter Variable", Georgia, serif',
    "Manrope": '"Manrope Variable", system-ui, sans-serif',
    "Mulish": '"Mulish Variable", system-ui, sans-serif',
    "Work Sans": '"Work Sans Variable", system-ui, sans-serif',
    "Inter": '"Inter Variable", system-ui, sans-serif',
    "Space Mono": '"Space Mono", ui-monospace, monospace',
}

DISPLAY_FONTS = [
    "Fraunces",
    "Newsreader",
    "Roboto Slab",
    "Space Grotesk",
    "Bitter",
]
BODY_FONTS = ["Manrope", "Mulish", "Work Sans", "Inter"]
MONO_FONT = "Space Mono"


@dataclass
class Settings:
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    )


def require(settings: Settings) -> None:
    if not settings.google_api_key:
        raise RuntimeError(
            "Missing env var: GOOGLE_API_KEY. Copy .env.example to .env and fill it in."
        )


class ColorMeaning(BaseModel):
    color: str = Field(pattern=HEX)
    meaning: str


class EyeDesign(BaseModel):
    color: str = Field(pattern=HEX)
    shape: str
    glow_intensity: float = Field(ge=0, le=1)


class SignatureMarkings(BaseModel):
    glow: bool
    color: str = Field(pattern=HEX)
    pattern: str
    location: str


class VisualIdentity(BaseModel):
    pose: str
    style: str
    gender: str
    base_form: str
    eye_design: EyeDesign
    accessories: List[str]
    color_palette: List[str] = Field(min_length=4, max_length=6)
    form_variants: List[str]
    animation_effects: List[str]
    signature_markings: SignatureMarkings


class ThemeColors(BaseModel):
    night: str = Field(pattern=HEX)
    night2: str = Field(pattern=HEX)
    night3: str = Field(pattern=HEX)
    accent: str = Field(pattern=HEX)
    accent2: str = Field(pattern=HEX)
    sky: str = Field(pattern=HEX)
    violet: str = Field(pattern=HEX)
    violetSoft: str = Field(pattern=HEX)
    cream: str = Field(pattern=HEX)
    text: str = Field(pattern=HEX)
    textDim: str = Field(pattern=HEX)
    textFaint: str = Field(pattern=HEX)


class ThemeFonts(BaseModel):
    display: str
    body: str
    mono: str = MONO_FONT


class UITheme(BaseModel):
    colors: ThemeColors
    fonts: ThemeFonts
    motion: str
    rationale: str


class SymbolismPatch(BaseModel):
    color_meanings: List[ColorMeaning] = Field(min_length=3, max_length=6)


class RepresentationPatch(BaseModel):
    symbolism: SymbolismPatch
    visual_identity: VisualIdentity


class GeneratedUIDesign(BaseModel):
    ui_theme: UITheme
    representation_profile: RepresentationPatch

    def to_schema_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        color_pairs = data["representation_profile"]["symbolism"].pop(
            "color_meanings"
        )
        data["representation_profile"]["symbolism"]["color_meanings"] = {
            pair["color"]: pair["meaning"] for pair in color_pairs
        }

        fonts = data["ui_theme"]["fonts"]
        fonts["display"] = FONT_STACKS.get(fonts["display"], fonts["display"])
        fonts["body"] = FONT_STACKS.get(fonts["body"], fonts["body"])
        fonts["mono"] = FONT_STACKS[MONO_FONT]

        motion = str(data["ui_theme"].get("motion", "")).strip().lower()
        data["ui_theme"]["motion"] = motion if motion in MOTION_KINDS else "motes"
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_llm(settings: Settings, temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
    )


def _with_character_profile(
    user_data: Dict[str, Any], character_profile: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    if character_profile is None:
        return dict(user_data)
    data = dict(user_data)
    data["character_profile"] = character_profile
    return data


def _prompt(user_data: Dict[str, Any]) -> str:
    profile_json = json.dumps(user_data, indent=2, ensure_ascii=False)
    return (
        "You are the visual system designer for Astrana, a social app where each "
        "user has a generated mascot avatar and a personalized interface theme.\n\n"
        "Generate a UI design patch from the entire user JSON below. Use the full "
        "profile, including bio, character_profile, representation_profile, and "
        "avatar_description. If avatar_description is present, treat it as the "
        "primary visual brief for the theme; otherwise infer from the rest of the "
        "profile. Do not use a fixed trait-to-palette mapping. Infer a cohesive, "
        "specific theme from the whole profile.\n\n"
        "Return values for:\n"
        "- ui_theme.colors: hex colors for the existing app CSS slots. night, "
        "night2, and night3 should be dark surfaces; text, textDim, textFaint, "
        "and cream must remain readable on those surfaces.\n"
        "- ui_theme.fonts.display: choose exactly one of "
        f"{', '.join(DISPLAY_FONTS)}.\n"
        "- ui_theme.fonts.body: choose exactly one of "
        f"{', '.join(BODY_FONTS)}.\n"
        f"- ui_theme.fonts.mono: use {MONO_FONT}.\n"
        "- ui_theme.motion: choose exactly one of motes, ripples, dust, sparks, drift.\n"
        "- representation_profile.visual_identity: complete avatar visual fields "
        "that align with the theme and avatar description.\n"
        "- representation_profile.symbolism.color_meanings: 3-6 palette colors "
        "with short meanings.\n\n"
        "Keep color_palette to 4-6 hex colors and make eye_design.color and "
        "signature_markings.color reuse or harmonize with that palette.\n\n"
        "Entire user JSON:\n"
        f"{profile_json}"
    )


def _source_summary(user_data: Dict[str, Any]) -> Dict[str, Any]:
    character_profile = user_data.get("character_profile", {})
    zodiac = character_profile.get("zodiac", {})
    horoscope = character_profile.get("horoscope", {})
    return {
        "zodiac": zodiac.get("sign") if isinstance(zodiac, dict) else None,
        "horoscope": horoscope.get("sign") if isinstance(horoscope, dict) else None,
        "avatar_description_used": bool(user_data.get("avatar_description")),
        "source": "gemini",
    }


def generate_ui_design(
    user_data: Dict[str, Any],
    user_id: int,
    character_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate UI design fields from the full user JSON using Gemini."""
    data = _with_character_profile(user_data, character_profile)
    settings = Settings()
    require(settings)

    structured = _make_llm(settings).with_structured_output(GeneratedUIDesign)
    result = structured.invoke(_prompt(data))
    if not isinstance(result, GeneratedUIDesign):
        result = GeneratedUIDesign.model_validate(result)

    return {
        "user_id": user_id,
        "generated_at": _now_iso(),
        "source_summary": _source_summary(data),
        "ui_design": result.to_schema_dict(),
    }
