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


def client_with_user(tmp_path, monkeypatch, user_data: dict) -> TestClient:
    store = UserStore(tmp_path / "users")
    ui_design_store = UIDesignStore(tmp_path / "ui_designs")
    store.save(int(user_data["id"]), user_data)
    monkeypatch.setattr(main, "store", store)
    monkeypatch.setattr(main, "ui_design_store", ui_design_store)
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
