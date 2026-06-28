"""FastAPI backend for the Astrana SDUI prototype."""

from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from api.matches import build_matches
from api.services.avatar import mark_failed, mark_generating, run_avatar_pipeline
from api.services.ui_design import generate_ui_design as build_ui_design
from api.store import UIDesignStore, UserStore, envelope, unwrap

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / "api" / ".env")
load_dotenv(REPO_ROOT / "tools" / "avatar_gen" / ".env")

store = UserStore()
ui_design_store = UIDesignStore()

DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://server-driven-ui-fawn.vercel.app",
]


def cors_origins() -> List[str]:
    extra = os.getenv("CORS_ORIGINS", "")
    origins = list(DEFAULT_ORIGINS)
    if extra:
        origins.extend(o.strip() for o in extra.split(",") if o.strip())
    return origins


app = FastAPI(title="Astrana API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    store.seed_if_empty()


class UserSummary(BaseModel):
    id: str
    user_id: int
    label: str


class UserPatch(BaseModel):
    bio: Optional[str] = None
    gender: Optional[str] = None
    place_of_birth: Optional[str] = None
    current_location: Optional[str] = None
    dob_year: Optional[int] = None
    dob_month: Optional[int] = None
    dob_day: Optional[int] = None


class ImportBody(BaseModel):
    json: Dict[str, Any] = Field(..., description="User envelope or raw data object")


class UIGenerateBody(BaseModel):
    character_profile: Optional[Dict[str, Any]] = Field(
        None, description="Updated character profile to generate UI design from"
    )


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _with_generated_ui(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    record = ui_design_store.get(user_id)
    if record is None:
        character_profile = data.get("character_profile")
        if isinstance(character_profile, dict) and _needs_generated_palette(data):
            generated = build_ui_design(character_profile, user_id)["ui_design"]
            return _deep_merge(data, generated)
        return data
    ui_design = record.get("ui_design")
    if not isinstance(ui_design, dict):
        return data
    return _deep_merge(data, ui_design)


def _needs_generated_palette(data: Dict[str, Any]) -> bool:
    representation = data.get("representation_profile")
    if not isinstance(representation, dict):
        return True
    visual_identity = representation.get("visual_identity")
    if not isinstance(visual_identity, dict):
        return True
    palette = visual_identity.get("color_palette")
    return not isinstance(palette, list) or not palette


def _has_required_signs(character_profile: Dict[str, Any]) -> bool:
    return isinstance(character_profile.get("zodiac"), dict) and isinstance(
        character_profile.get("horoscope"), dict
    )


def _avatar_job(user_id: int) -> None:
    data = store.get_data(user_id)
    if data is None:
        return
    try:
        updated = run_avatar_pipeline(data)
        store.save(user_id, updated, message="Avatar generated")
    except Exception:
        traceback.print_exc()
        failed = mark_failed(data, "generation failed")
        store.save(user_id, failed, message="Avatar generation failed")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/users")
def list_users() -> Dict[str, Any]:
    return envelope(store.list_summaries(), message="Users listed")


@app.get("/users/{user_id}")
def get_user(user_id: int) -> Dict[str, Any]:
    raw = store.get(user_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="User not found")
    data, wrapped = unwrap(raw)
    message = raw.get("message", "User retrieved") if wrapped else "User retrieved"
    return envelope(_with_generated_ui(user_id, data), message=message)


@app.patch("/users/{user_id}")
def patch_user(user_id: int, body: UserPatch) -> Dict[str, Any]:
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = store.patch(user_id, fields)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@app.post("/users/import")
def import_user(body: ImportBody) -> Dict[str, Any]:
    try:
        return store.import_json(body.json)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/users/{user_id}/matches")
def get_matches(user_id: int) -> Dict[str, Any]:
    data = store.get_data(user_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return envelope(build_matches(data), message="Matches listed")


@app.post("/users/{user_id}/ui/generate")
def generate_ui_design(user_id: int, body: UIGenerateBody) -> Dict[str, Any]:
    data = store.get_data(user_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    if body.character_profile is None:
        raise HTTPException(status_code=400, detail="character_profile is required")
    if not _has_required_signs(body.character_profile):
        raise HTTPException(
            status_code=400,
            detail="character_profile requires zodiac and horoscope",
        )

    design = build_ui_design(body.character_profile, user_id)
    ui_design_store.save(user_id, design)
    return envelope(design, message="UI design generated")


@app.post("/users/{user_id}/avatar/generate")
def generate_avatar(user_id: int, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    data = store.get_data(user_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    if "character_profile" not in data:
        raise HTTPException(status_code=400, detail="User has no character_profile")

    generating = mark_generating(data)
    result = store.save(user_id, generating, message="Avatar generation started")
    background_tasks.add_task(_avatar_job, user_id)
    return result
