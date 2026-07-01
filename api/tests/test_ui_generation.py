from __future__ import annotations

import copy
import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

import api.main as main
from api.store import UIDesignStore, UserStore


REPO_ROOT = Path(__file__).resolve().parents[2]
USER_FIXTURE = REPO_ROOT / "data" / "test" / "marcus.test.json"
USER_SCHEMA = REPO_ROOT / "data" / "schema" / "user-response.schema.json"


def load_user_data() -> dict:
    raw = json.loads(USER_FIXTURE.read_text(encoding="utf-8"))
    return raw["data"]


def fake_ui_design(
    user_data: dict, user_id: int, character_profile: dict | None = None
) -> dict:
    profile = character_profile or user_data["character_profile"]
    traits = profile["zodiac"].get("personality_traits", [])
    energetic = "energetic" in [trait.lower() for trait in traits]
    palette = (
        ["#FF6B35", "#F7C59F", "#FDE74C", "#772F1A", "#1D1A05"]
        if energetic
        else ["#8EC5C1", "#DDEFE8", "#F7E8C9", "#5F7F8C", "#2F3E46"]
    )
    return {
        "user_id": user_id,
        "generated_at": "2026-06-30T00:00:00Z",
        "source_summary": {
            "zodiac": profile["zodiac"]["sign"],
            "horoscope": profile["horoscope"]["sign"],
            "avatar_description_used": bool(user_data.get("avatar_description")),
            "source": "test",
        },
        "ui_design": {
            "ui_theme": {
                "colors": {
                    "night": "#101820",
                    "night2": "#16232D",
                    "night3": "#20313C",
                    "accent": palette[0],
                    "accent2": palette[1],
                    "sky": palette[2],
                    "violet": palette[3],
                    "violetSoft": "#8EC5C1",
                    "cream": "#F8F9FA",
                    "text": "#F8F9FA",
                    "textDim": "#DDEFE8",
                    "textFaint": "#9DB2BF",
                },
                "fonts": {
                    "display": '"Fraunces Variable", Georgia, serif',
                    "body": '"Manrope Variable", system-ui, sans-serif',
                    "mono": '"Space Mono", ui-monospace, monospace',
                },
                "motion": "sparks" if energetic else "motes",
                "rationale": "Generated from the full user profile.",
            },
            "representation_profile": {
                "symbolism": {
                    "color_meanings": {
                        palette[0]: "primary personality tone",
                        palette[1]: "active accent and highlights",
                        palette[2]: "supporting emotional texture",
                    }
                },
                "visual_identity": {
                    "pose": "standing calmly with a focused expression",
                    "style": "kawaii plush with celestial details",
                    "gender": "ambiguous",
                    "base_form": "A rounded mascot with soft limbs.",
                    "color_palette": palette,
                    "eye_design": {
                        "color": palette[1],
                        "shape": "large rounded ovals",
                        "glow_intensity": 0.24,
                    },
                    "accessories": ["charm", "stitched star patch"],
                    "form_variants": ["Daily companion", "Profile showcase"],
                    "animation_effects": ["soft glow pulse"],
                    "signature_markings": {
                        "glow": True,
                        "color": palette[1],
                        "pattern": "constellation mark",
                        "location": "upper chest",
                    },
                },
            },
        },
    }


def client_with_user(tmp_path, monkeypatch, user_data: dict) -> TestClient:
    store = UserStore(tmp_path / "users")
    ui_design_store = UIDesignStore(tmp_path / "ui_designs")
    store.save(int(user_data["id"]), user_data)
    monkeypatch.setattr(main, "store", store)
    monkeypatch.setattr(main, "ui_design_store", ui_design_store)
    monkeypatch.setattr(main, "build_ui_design", fake_ui_design)
    return TestClient(main.app)


def user_path(user_data: dict, suffix: str = "") -> str:
    return f"/users/{user_data['id']}{suffix}"


def test_generate_ui_design_updates_the_user_response_palette(tmp_path, monkeypatch):
    user_data = load_user_data()
    updated_character_profile = copy.deepcopy(user_data["character_profile"])
    updated_character_profile["zodiac"]["personality_traits"] = [
        "calm",
        "patient",
        "grounded",
        "reflective",
    ]
    updated_character_profile["horoscope"]["personality_traits"] = [
        "nurturing",
        "sensitive",
        "protective",
        "intuitive",
    ]

    client = client_with_user(tmp_path, monkeypatch, user_data)

    generate_response = client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": updated_character_profile},
    )

    assert generate_response.status_code == 200
    generated_palette = generate_response.json()["data"]["ui_design"][
        "representation_profile"
    ]["visual_identity"]["color_palette"]
    assert generated_palette

    user_response = client.get(user_path(user_data))

    assert user_response.status_code == 200
    rendered_palette = user_response.json()["data"]["representation_profile"][
        "visual_identity"
    ]["color_palette"]
    assert rendered_palette == generated_palette


def test_generate_ui_design_passes_the_full_user_json(tmp_path, monkeypatch):
    user_data = load_user_data()
    calls = []

    def spy(user_data: dict, user_id: int, character_profile: dict | None = None):
        calls.append((copy.deepcopy(user_data), user_id, character_profile))
        return fake_ui_design(user_data, user_id, character_profile)

    client = client_with_user(tmp_path, monkeypatch, user_data)
    monkeypatch.setattr(main, "build_ui_design", spy)

    response = client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": user_data["character_profile"]},
    )

    assert response.status_code == 200
    sent_user_data, sent_user_id, sent_character_profile = calls[0]
    assert sent_user_id == user_data["id"]
    assert sent_user_data["first_name"] == user_data["first_name"]
    assert sent_user_data["avatar_description"] == user_data["avatar_description"]
    assert sent_user_data["representation_profile"]
    assert sent_character_profile == user_data["character_profile"]


def test_generate_ui_design_requires_character_profile(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)

    response = client.post(user_path(user_data, "/ui/generate"), json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "character_profile is required"


def test_generate_ui_design_requires_zodiac_and_horoscope(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)

    response = client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": {}},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "character_profile requires zodiac and horoscope"


def test_generate_ui_design_returns_404_for_unknown_user(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)

    response = client.post(
        "/users/999999/ui/generate",
        json={"character_profile": user_data["character_profile"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_generate_ui_design_returns_complete_visual_identity(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)

    response = client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": user_data["character_profile"]},
    )

    assert response.status_code == 200
    visual_identity = response.json()["data"]["ui_design"]["representation_profile"][
        "visual_identity"
    ]
    assert set(visual_identity) >= {
        "pose",
        "style",
        "gender",
        "base_form",
        "eye_design",
        "accessories",
        "color_palette",
        "form_variants",
        "animation_effects",
        "signature_markings",
    }


def test_get_user_falls_back_when_base_profile_has_no_palette(tmp_path, monkeypatch):
    user_data = load_user_data()
    del user_data["representation_profile"]["visual_identity"]["color_palette"]
    client = client_with_user(tmp_path, monkeypatch, user_data)

    response = client.get(user_path(user_data))

    assert response.status_code == 200
    palette = response.json()["data"]["representation_profile"]["visual_identity"][
        "color_palette"
    ]
    assert palette


def test_generate_ui_design_palette_changes_when_traits_change(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)

    first_response = client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": user_data["character_profile"]},
    )
    changed_character_profile = copy.deepcopy(user_data["character_profile"])
    changed_character_profile["zodiac"]["personality_traits"] = [
        "energetic",
        "adventurous",
        "independent",
    ]
    changed_response = client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": changed_character_profile},
    )

    assert first_response.status_code == 200
    assert changed_response.status_code == 200
    first_palette = first_response.json()["data"]["ui_design"]["representation_profile"][
        "visual_identity"
    ]["color_palette"]
    changed_palette = changed_response.json()["data"]["ui_design"][
        "representation_profile"
    ]["visual_identity"]["color_palette"]
    assert changed_palette != first_palette


def test_generated_ui_design_keeps_user_response_schema_valid(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)
    client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": user_data["character_profile"]},
    )

    response = client.get(user_path(user_data))

    assert response.status_code == 200
    schema = json.loads(USER_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(response.json())


def test_generated_ui_theme_is_merged_into_user_response(tmp_path, monkeypatch):
    user_data = load_user_data()
    client = client_with_user(tmp_path, monkeypatch, user_data)

    client.post(
        user_path(user_data, "/ui/generate"),
        json={"character_profile": user_data["character_profile"]},
    )

    response = client.get(user_path(user_data))

    assert response.status_code == 200
    ui_theme = response.json()["data"]["ui_theme"]
    assert ui_theme["fonts"]["display"] == '"Fraunces Variable", Georgia, serif'
    assert ui_theme["colors"]["accent"] == "#8EC5C1"


def test_avatar_generation_does_not_generate_ui_theme(tmp_path, monkeypatch):
    user_data = load_user_data()

    def avatar_pipeline(data: dict) -> dict:
        updated = copy.deepcopy(data)
        updated["avatar_status"] = "completed"
        updated["avatar_picture"] = "https://example.com/new-avatar.png"
        updated["avatar_description"] = "A newly generated moonlit mascot."
        return updated

    client = client_with_user(tmp_path, monkeypatch, user_data)
    monkeypatch.setattr(main, "run_avatar_pipeline", avatar_pipeline)
    monkeypatch.setattr(
        main,
        "build_ui_design",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("avatar generation should not generate UI design")
        ),
    )

    main._avatar_job(user_data["id"])

    response = client.get(user_path(user_data))

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["avatar_picture"] == "https://example.com/new-avatar.png"
    assert "ui_theme" not in body
    assert main.ui_design_store.get(user_data["id"]) is None
