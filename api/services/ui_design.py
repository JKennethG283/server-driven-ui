"""Rules-based UI design generation from a character profile."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List


TRAIT_PALETTES = {
    "calm": ["#8EC5C1", "#DDEFE8", "#F7E8C9", "#5F7F8C", "#2F3E46"],
    "patient": ["#8EC5C1", "#DDEFE8", "#F7E8C9", "#5F7F8C", "#2F3E46"],
    "grounded": ["#7A9E7E", "#D9C9A3", "#F5F0E1", "#5C6B4F", "#2E382E"],
    "reflective": ["#6C7A89", "#B7C9D6", "#F2E9DC", "#40566B", "#1F2A38"],
    "nurturing": ["#F6A6B2", "#FFE1D6", "#CDE7B0", "#7D9D9C", "#3B4A54"],
    "sensitive": ["#B8A1D9", "#D7ECF7", "#FFE5F1", "#7895B2", "#2D3250"],
    "protective": ["#53687E", "#9DB2BF", "#F5E9CF", "#DDA15E", "#283618"],
    "intuitive": ["#7E6BC4", "#A8DADC", "#F1FAEE", "#457B9D", "#1D3557"],
    "adventurous": ["#FFB74D", "#FFD54F", "#81D4FA", "#FFF8E7", "#8E44AD"],
    "optimistic": ["#FFB74D", "#FFD54F", "#81D4FA", "#FFF8E7", "#8E44AD"],
    "energetic": ["#FF6B35", "#F7C59F", "#EFEFD0", "#004E89", "#1A659E"],
    "independent": ["#5BC0EB", "#FDE74C", "#9BC53D", "#E55934", "#FAFAFA"],
}

ELEMENT_PALETTES = {
    "fire": ["#FF6B35", "#F7C59F", "#FDE74C", "#772F1A", "#1D1A05"],
    "water": ["#5DADEC", "#B8E0D2", "#EEF5DB", "#3A506B", "#0B132B"],
    "earth": ["#7A9E7E", "#D9C9A3", "#F5F0E1", "#5C6B4F", "#2E382E"],
    "wood": ["#7CB518", "#C7EFCF", "#F3E9D2", "#4F772D", "#132A13"],
    "metal": ["#BFC0C0", "#F4F4F9", "#A3CEF1", "#6096BA", "#274C77"],
}

DEFAULT_PALETTE = ["#8ECAE6", "#FFB703", "#FB8500", "#F8F9FA", "#023047"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _items(value: Any) -> Iterable[str]:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                yield item


def _traits(character_profile: Dict[str, Any]) -> List[str]:
    traits: List[str] = []
    for sign_key in ("zodiac", "horoscope"):
        sign = character_profile.get(sign_key, {})
        if isinstance(sign, dict):
            traits.extend(
                item.strip().lower()
                for item in _items(sign.get("personality_traits"))
            )
            traits.extend(item.strip().lower() for item in _items(sign.get("values")))
    return [trait for trait in traits if trait]


def _palette_for(character_profile: Dict[str, Any]) -> List[str]:
    for trait in _traits(character_profile):
        if trait in TRAIT_PALETTES:
            return TRAIT_PALETTES[trait]

    zodiac = character_profile.get("zodiac", {})
    if isinstance(zodiac, dict):
        element = str(zodiac.get("element", "")).strip().lower()
        if element in ELEMENT_PALETTES:
            return ELEMENT_PALETTES[element]

    return DEFAULT_PALETTE


def _style_for(character_profile: Dict[str, Any]) -> str:
    zodiac = character_profile.get("zodiac", {})
    element = ""
    if isinstance(zodiac, dict):
        element = str(zodiac.get("element", "")).strip().lower()
    styles = {
        "fire": "kawaii plush with bright celestial sparks",
        "water": "kawaii plush with soft wave and moonlit details",
        "earth": "kawaii plush with grounded botanical stitching",
        "wood": "kawaii plush with fresh leaf and growth motifs",
        "metal": "kawaii plush with clean metallic thread accents",
    }
    return styles.get(element, "kawaii minimalist plush with astrological details")


def generate_ui_design(character_profile: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """Generate UI design fields from a character profile."""
    palette = _palette_for(character_profile)
    traits = _traits(character_profile)
    motif = traits[0] if traits else "balanced"
    return {
        "user_id": user_id,
        "generated_at": _now_iso(),
        "source_summary": {
            "zodiac": character_profile.get("zodiac", {}).get("sign"),
            "horoscope": character_profile.get("horoscope", {}).get("sign"),
            "traits": traits[:12],
        },
        "ui_design": {
            "representation_profile": {
                "visual_identity": {
                    "pose": f"standing calmly with a {motif} expression",
                    "style": _style_for(character_profile),
                    "gender": "ambiguous",
                    "base_form": (
                        "A rounded, ultra-fluffy mascot with short soft limbs, "
                        "simple expressive features, and a huggable silhouette."
                    ),
                    "color_palette": palette,
                    "eye_design": {
                        "color": palette[1],
                        "shape": "large rounded ovals with a soft highlight",
                        "glow_intensity": 0.24,
                    },
                    "accessories": [
                        f"{motif} charm",
                        "stitched star patch",
                        "small woven keepsake pouch",
                    ],
                    "form_variants": [
                        "Daily companion",
                        "Profile showcase",
                        "Compact sticker",
                    ],
                    "animation_effects": [
                        "soft glow pulse",
                        "gentle idle float",
                        "subtle sparkle trail",
                    ],
                    "signature_markings": {
                        "glow": True,
                        "color": palette[1],
                        "pattern": f"{motif} constellation mark",
                        "location": "upper chest",
                    },
                },
                "symbolism": {
                    "color_meanings": {
                        palette[0]: "primary personality tone",
                        palette[1]: "active accent and highlights",
                        palette[2]: "supporting emotional texture",
                    }
                },
            }
        },
    }
