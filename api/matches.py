"""Match list builder — mirrors app/src/data/user.ts mock seeds."""

from __future__ import annotations

import copy
from typing import Any, Dict, List

MatchSeed = Dict[str, Any]

SEEDS: List[MatchSeed] = [
    {
        "id": 11,
        "first_name": "Mira",
        "username": "miraskies",
        "bio": "Cartographer of small joys",
        "current_location": "Lisbon",
        "zodiacSign": "Horse",
        "zodiacElement": "Wood",
        "horoscopeSign": "Aquarius",
        "archetype": "The Dreamer / The Visionary",
        "themeSong": "Tidal Lanterns (slow synths, warm and weightless)",
        "palette": ["#81D4FA", "#B39DDB", "#FFF8E7", "#4FC3F7", "#5E35B1"],
        "avatar": "https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=600&auto=format&fit=crop",
        "avatarDescription": "A soft lilac creature with star-flecked fur gazing upward beneath a drifting aurora.",
        "traits": ["curious", "gentle", "imaginative", "open-minded", "warm"],
        "values": ["freedom", "knowledge", "growth", "authenticity"],
        "score": 92,
        "shared_values": ["freedom", "knowledge", "growth"],
        "revealed": True,
        "thinking_feeling": 0.62,
        "introversion_extroversion": 0.55,
        "dominant_emotion": "quiet wonder",
        "alignment": "Neutral Good",
    },
    {
        "id": 12,
        "first_name": "Dax",
        "username": "daxwild",
        "bio": "Trail runner, terrible at standing still",
        "current_location": "Denver",
        "zodiacSign": "Tiger",
        "zodiacElement": "Fire",
        "horoscopeSign": "Aries",
        "archetype": "The Trailblazer / The Challenger",
        "themeSong": "Summit Engine (driving percussion, bright brass)",
        "palette": ["#FFB74D", "#FF7043", "#FFD54F", "#FFF8E7", "#8E44AD"],
        "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=600&auto=format&fit=crop",
        "avatarDescription": "A bold amber creature mid-stride, a streak of firelight trailing behind it.",
        "traits": ["energetic", "competitive", "bold", "spontaneous", "driven"],
        "values": ["action", "freedom", "achievement", "excitement"],
        "score": 84,
        "shared_values": ["action", "freedom", "achievement", "excitement"],
        "revealed": True,
        "thinking_feeling": 0.3,
        "introversion_extroversion": 0.9,
        "dominant_emotion": "restless drive",
        "alignment": "Chaotic Good",
    },
    {
        "id": 13,
        "first_name": "Sol",
        "username": "solunari",
        "bio": "Tea, philosophy, long walks",
        "current_location": "Kyoto",
        "zodiacSign": "Rabbit",
        "zodiacElement": "Earth",
        "horoscopeSign": "Libra",
        "archetype": "The Sage / The Harmonizer",
        "themeSong": "Paper Moon (gentle koto and rain)",
        "palette": ["#FFD54F", "#A1887F", "#FFF8E7", "#C5E1A5", "#6D4C41"],
        "avatar": "https://images.unsplash.com/photo-1517849845537-4d257902454a?q=80&w=600&auto=format&fit=crop",
        "avatarDescription": "A round, calm creature with half-closed eyes resting under a paper lantern.",
        "traits": ["thoughtful", "balanced", "diplomatic", "calm", "kind"],
        "values": ["truth", "knowledge", "growth", "authenticity"],
        "score": 78,
        "shared_values": ["truth", "knowledge", "growth"],
        "revealed": False,
        "thinking_feeling": 0.7,
        "introversion_extroversion": 0.3,
        "dominant_emotion": "serene curiosity",
        "alignment": "Lawful Good",
    },
    {
        "id": 14,
        "first_name": "Wren",
        "username": "wrenroams",
        "bio": "Collects maps, never folds them right",
        "current_location": "Reykjavik",
        "zodiacSign": "Monkey",
        "zodiacElement": "Metal",
        "horoscopeSign": "Gemini",
        "archetype": "The Trickster / The Inventor",
        "themeSong": "Static Carnival (playful glitch-pop)",
        "palette": ["#4DD0E1", "#FFD54F", "#FFF8E7", "#26A69A", "#7E57C2"],
        "avatar": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?q=80&w=600&auto=format&fit=crop",
        "avatarDescription": "A teal creature with bright eyes and a satchel overflowing with curious gadgets.",
        "traits": ["clever", "adaptable", "witty", "inventive", "social"],
        "values": ["knowledge", "adventure", "innovation", "freedom"],
        "score": 71,
        "shared_values": ["knowledge", "adventure", "freedom"],
        "revealed": False,
        "thinking_feeling": 0.45,
        "introversion_extroversion": 0.8,
        "dominant_emotion": "playful spark",
        "alignment": "Chaotic Neutral",
    },
]


def _build_match_user(base: Dict[str, Any], seed: MatchSeed) -> Dict[str, Any]:
    user = copy.deepcopy(base)
    cp = user["character_profile"]
    rep = user["representation_profile"]
    pp = rep["personality_profile"]

    user.update(
        {
            "id": seed["id"],
            "user_id": seed["id"],
            "first_name": seed["first_name"],
            "last_name": "",
            "username": seed["username"],
            "bio": seed["bio"],
            "current_location": seed["current_location"],
            "avatar_picture": seed["avatar"],
            "avatar_description": seed["avatarDescription"],
        }
    )
    user["character_profile"] = {
        **cp,
        "zodiac": {
            **cp["zodiac"],
            "sign": seed["zodiacSign"],
            "element": seed["zodiacElement"],
            "values": seed["values"],
            "personality_traits": seed["traits"],
        },
        "horoscope": {
            **cp["horoscope"],
            "sign": seed["horoscopeSign"],
            "values": seed["values"],
            "personality_traits": seed["traits"],
        },
    }
    user["representation_profile"] = {
        **rep,
        "symbolism": {
            **rep["symbolism"],
            "archetype": seed["archetype"],
            "theme_song": seed["themeSong"],
        },
        "visual_identity": {
            **rep["visual_identity"],
            "color_palette": seed["palette"],
        },
        "personality_profile": {
            **pp,
            "traits": seed["traits"],
            "dominant_emotion": seed["dominant_emotion"],
            "alignment": seed["alignment"],
            "thinking_feeling": {
                **pp["thinking_feeling"],
                "scale": seed["thinking_feeling"],
            },
            "introversion_extroversion": {
                **pp["introversion_extroversion"],
                "scale": seed["introversion_extroversion"],
            },
        },
    }
    return user


def build_matches(base_user: Dict[str, Any]) -> List[Dict[str, Any]]:
    matches = [
        {
            "user": _build_match_user(base_user, seed),
            "score": seed["score"],
            "shared_values": seed["shared_values"],
            "revealed": seed["revealed"],
        }
        for seed in SEEDS
    ]
    return sorted(matches, key=lambda m: m["score"], reverse=True)
