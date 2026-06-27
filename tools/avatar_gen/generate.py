"""Fill in a user's avatar fields from their character data.

Pipeline (LangGraph): persona (Gemini) -> image prompt -> image (Cloudflare
FLUX/SDXL) -> host -> description (Gemini) -> assemble -> validate vs schema.

Usage:
    python tools/avatar_gen/generate.py data/test/luna.test.json            # writes *.filled.json
    python tools/avatar_gen/generate.py data/test/luna.test.json --in-place # overwrite input
    python tools/avatar_gen/generate.py data/test/luna.test.json --no-host  # local file:// URI
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, TypedDict

import requests
from dotenv import load_dotenv
from jsonschema import Draft202012Validator
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[2]
load_dotenv(HERE.parent / ".env")
load_dotenv()


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    cf_account_id: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    cf_api_token: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    cf_image_model: str = os.getenv("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")
    host_images: bool = _bool(os.getenv("HOST_IMAGES"), True)
    max_attempts: int = int(os.getenv("MAX_ATTEMPTS", "3"))
    out_dir: Path = REPO_ROOT / os.getenv("OUT_DIR", "tools/avatar_gen/out")
    schema_path: Path = REPO_ROOT / "data" / "schema" / "user-response.schema.json"

    @property
    def is_flux(self) -> bool:
        return "flux" in self.cf_image_model.lower()


def require(settings: Settings) -> None:
    missing = [
        name
        for name, value in (
            ("GOOGLE_API_KEY", settings.google_api_key),
            ("CLOUDFLARE_ACCOUNT_ID", settings.cf_account_id),
            ("CLOUDFLARE_API_TOKEN", settings.cf_api_token),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing env vars: " + ", ".join(missing)
            + ". Copy .env.example to .env and fill them in."
        )


# --------------------------------------------------------------------------- #
# Models (mirror representation_profile; color_meanings as a list for the LLM)
# --------------------------------------------------------------------------- #

HEX = r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"


class ColorMeaning(BaseModel):
    color: str = Field(pattern=HEX)
    meaning: str


class Symbolism(BaseModel):
    archetype: str
    theme_song: str
    core_elements: List[str]
    color_meanings: List[ColorMeaning] = Field(min_length=3)
    totemic_animals: List[str]


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


class NarrativeWorld(BaseModel):
    name: str
    type: str
    terrain: List[str]
    time_period: str


class NarrativeContext(BaseModel):
    world: NarrativeWorld
    nemesis: str
    allegiance: str
    origin_story: str
    current_mission: str


class Scale(BaseModel):
    scale: float = Field(ge=0, le=1)
    description: str


class PersonalityProfile(BaseModel):
    fears: List[str]
    quirks: List[str]
    traits: List[str]
    alignment: str
    dominant_emotion: str
    thinking_feeling: Scale
    introversion_extroversion: Scale


class RepresentationProfile(BaseModel):
    symbolism: Symbolism
    visual_identity: VisualIdentity
    narrative_context: NarrativeContext
    personality_profile: PersonalityProfile

    def to_schema_dict(self) -> Dict:
        data = self.model_dump()
        pairs = data["symbolism"].pop("color_meanings")
        data["symbolism"]["color_meanings"] = {p["color"]: p["meaning"] for p in pairs}
        data["personality_profile"]["thinking_feeling"]["description"] = (
            "0 = logical thinking dominant, 1 = emotional feeling dominant"
        )
        data["personality_profile"]["introversion_extroversion"]["description"] = (
            "0 = fully introverted, 1 = fully extroverted"
        )
        return data


# --------------------------------------------------------------------------- #
# Prompts
# --------------------------------------------------------------------------- #

def _join(items: List[str] | None) -> str:
    return ", ".join(items) if items else "n/a"


def _sign_block(label: str, sign: Dict) -> str:
    return (
        f"{label}: {sign.get('sign', '?')}"
        + (f" ({sign.get('element')})" if sign.get("element") else "")
        + f"\n  values: {_join(sign.get('values'))}"
        + f"\n  traits: {_join(sign.get('personality_traits'))}"
        + f"\n  strengths: {_join(sign.get('strengths'))}"
        + f"\n  weaknesses: {_join(sign.get('weaknesses'))}"
    )


def persona_prompt(data: Dict) -> str:
    cp = data.get("character_profile", {})
    return (
        "You are a character designer for a social app whose users each get a "
        "cute, plush-like mascot avatar that embodies their astrology.\n\n"
        f"Design a complete representation_profile for {data.get('first_name', 'the user')}.\n"
        f"Bio: {data.get('bio', '')}\n\n"
        f"{_sign_block('Chinese zodiac', cp.get('zodiac', {}))}\n"
        f"{_sign_block('Western horoscope', cp.get('horoscope', {}))}\n\n"
        "Requirements:\n"
        "- Kawaii / minimalist plush creature whose look, world, and personality "
        "clearly reflect the signs above.\n"
        "- color_palette: 4-6 hex colors suiting this character.\n"
        "- color_meanings: 3-5 entries, each a hex color (reuse palette) + short meaning.\n"
        "- eye_design.color and signature_markings.color must be hex.\n"
        "- glow_intensity is 0..1.\n"
        "- thinking_feeling.scale and introversion_extroversion.scale are 0..1 "
        "(0 = logical/introverted, 1 = emotional/extroverted), inferred from traits.\n"
        "- Distinctive archetype, named narrative world, origin story, current mission.\n"
    )


def description_prompt(rep: Dict) -> str:
    vis = rep.get("visual_identity", {})
    world = rep.get("narrative_context", {}).get("world", {})
    return (
        "Write a single vivid paragraph (2-3 sentences) describing this mascot "
        "avatar as it would appear in a generated illustration. No preamble.\n\n"
        f"Archetype: {rep.get('symbolism', {}).get('archetype')}\n"
        f"Base form: {vis.get('base_form')}\n"
        f"Pose: {vis.get('pose')}\n"
        f"Palette: {_join(vis.get('color_palette'))}\n"
        f"Accessories: {_join(vis.get('accessories'))}\n"
        f"World: {world.get('name')} - {world.get('type')}\n"
    )


def image_prompt(rep: Dict) -> str:
    vis = rep.get("visual_identity", {})
    world = rep.get("narrative_context", {}).get("world", {})
    marks = vis.get("signature_markings", {})
    parts = [
        vis.get("style", "kawaii minimalist plush"),
        f"a {vis.get('base_form', 'soft round plush creature')}",
        f"pose: {vis.get('pose', 'standing, friendly')}",
        f"color palette {_join(vis.get('color_palette'))}",
        f"accessories: {_join(vis.get('accessories'))}",
        f"signature marking: {marks.get('pattern', '')} on {marks.get('location', '')}",
        f"set in {world.get('name', '')}, {world.get('type', '')}",
        "centered character, soft studio lighting, high detail, adorable, "
        "merchandise sticker style, clean background",
    ]
    return ". ".join(p for p in parts if p and p.strip(". "))[:1500]


# --------------------------------------------------------------------------- #
# Gemini
# --------------------------------------------------------------------------- #

def make_llm(settings: Settings, temperature: float = 0.8) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
    )


def generate_representation(llm: ChatGoogleGenerativeAI, data: Dict) -> Dict:
    structured = llm.with_structured_output(RepresentationProfile)
    result = structured.invoke(persona_prompt(data))
    if not isinstance(result, RepresentationProfile):
        result = RepresentationProfile.model_validate(result)
    return result.to_schema_dict()


def generate_description(llm: ChatGoogleGenerativeAI, rep: Dict) -> str:
    message = llm.invoke(description_prompt(rep))
    return getattr(message, "content", str(message)).strip()


# --------------------------------------------------------------------------- #
# Cloudflare Workers AI image generation + hosting
# --------------------------------------------------------------------------- #

CF_RUN_URL = "https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
CATBOX_URL = "https://catbox.moe/user/api.php"


def generate_image_bytes(settings: Settings, prompt: str) -> bytes:
    """FLUX returns JSON with base64; SDXL returns binary PNG."""
    url = CF_RUN_URL.format(acct=settings.cf_account_id, model=settings.cf_image_model)
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {settings.cf_api_token}"},
        json={"prompt": prompt},
        timeout=180,
    )
    resp.raise_for_status()
    if "application/json" in resp.headers.get("content-type", ""):
        payload = resp.json()
        if not payload.get("success", True):
            raise RuntimeError(f"Cloudflare AI error: {payload.get('errors')}")
        image_b64 = (payload.get("result") or {}).get("image")
        if not image_b64:
            raise RuntimeError(f"No image in Cloudflare response: {payload}")
        return base64.b64decode(image_b64)
    return resp.content


def host_or_save(settings: Settings, raw: bytes, stem: str) -> str:
    settings.out_dir.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if settings.is_flux else "png"
    path = settings.out_dir / f"{stem}.{ext}"
    path.write_bytes(raw)
    if not settings.host_images:
        return path.resolve().as_uri()
    with path.open("rb") as handle:
        resp = requests.post(
            CATBOX_URL,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (path.name, handle)},
            timeout=180,
        )
    resp.raise_for_status()
    url = resp.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Unexpected catbox response: {url!r}")
    return url


# --------------------------------------------------------------------------- #
# LangGraph pipeline
# --------------------------------------------------------------------------- #

class GenState(TypedDict, total=False):
    data: Dict
    representation_profile: Dict
    image_prompt: str
    avatar_url: str
    avatar_description: str
    started_at: str
    attempts: int
    errors: List[str]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_graph(settings: Settings, llm: ChatGoogleGenerativeAI):
    validator = Draft202012Validator(
        json.loads(settings.schema_path.read_text(encoding="utf-8"))
    )

    def node_persona(state: GenState) -> GenState:
        return {
            "representation_profile": generate_representation(llm, state["data"]),
            "attempts": state.get("attempts", 0) + 1,
            "started_at": state.get("started_at") or _now_iso(),
        }

    def node_prompt(state: GenState) -> GenState:
        return {"image_prompt": image_prompt(state["representation_profile"])}

    def node_image(state: GenState) -> GenState:
        stem = str(state["data"].get("username") or state["data"].get("id") or "avatar")
        raw = generate_image_bytes(settings, state["image_prompt"])
        return {"avatar_url": host_or_save(settings, raw, stem)}

    def node_description(state: GenState) -> GenState:
        return {"avatar_description": generate_description(llm, state["representation_profile"])}

    def node_assemble(state: GenState) -> GenState:
        data = dict(state["data"])
        data["representation_profile"] = state["representation_profile"]
        data["avatar_picture"] = state["avatar_url"]
        data["avatar_description"] = state["avatar_description"]
        data["avatar_status"] = "completed"
        data["avatar_generation_started_at"] = state["started_at"]
        data["profile_updated_at"] = _now_iso()
        data["updated_at"] = _now_iso()
        return {"data": data}

    def node_validate(state: GenState) -> GenState:
        envelope = {"code": 200, "message": "User retrieved", "data": state["data"]}
        errors = [
            f"{list(e.absolute_path)}: {e.message}"
            for e in validator.iter_errors(envelope)
        ]
        return {"errors": errors[:8]}

    def route(state: GenState) -> str:
        if not state.get("errors"):
            return "end"
        return "retry" if state.get("attempts", 0) < settings.max_attempts else "end"

    graph = StateGraph(GenState)
    graph.add_node("persona", node_persona)
    graph.add_node("prompt", node_prompt)
    graph.add_node("image", node_image)
    graph.add_node("description", node_description)
    graph.add_node("assemble", node_assemble)
    graph.add_node("validate", node_validate)
    graph.set_entry_point("persona")
    graph.add_edge("persona", "prompt")
    graph.add_edge("prompt", "image")
    graph.add_edge("image", "description")
    graph.add_edge("description", "assemble")
    graph.add_edge("assemble", "validate")
    graph.add_conditional_edges("validate", route, {"retry": "persona", "end": END})
    return graph.compile()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _load(path: Path) -> Tuple[Dict, bool]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "data" in raw and isinstance(raw["data"], dict):
        return raw["data"], True
    return raw, False


def _app_stem(input_path: Path) -> str:
    """Profile id used by the web app (e.g. luna.test.json -> luna)."""
    name = input_path.name
    for suffix in (".filled.json", ".test.json", ".json"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return input_path.stem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate + fill avatar profile.")
    parser.add_argument("input", type=Path, help="Path to a user JSON file.")
    parser.add_argument(
        "--out",
        type=Path,
        help="Write the result to this path instead of overwriting the input.",
    )
    parser.add_argument(
        "--no-in-place",
        dest="in_place",
        action="store_false",
        help="Don't overwrite the input; write to <input>.filled.json instead.",
    )
    parser.add_argument("--no-host", action="store_true", help="Use a local file:// URI.")
    parser.add_argument(
        "--no-apply-to-app",
        dest="apply_to_app",
        action="store_false",
        help="Don't copy the profile into app/src/data/profiles/.",
    )
    parser.set_defaults(in_place=True, apply_to_app=True)
    args = parser.parse_args(argv)

    settings = Settings()
    if args.no_host:
        settings.host_images = False
    require(settings)

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 2

    data, was_envelope = _load(args.input)
    if "character_profile" not in data:
        print("Input has no character_profile; nothing to base the avatar on.", file=sys.stderr)
        return 2

    print(f"Generating avatar for {data.get('first_name', 'user')} using "
          f"{settings.gemini_model} + {settings.cf_image_model} ...")

    app = build_graph(settings, make_llm(settings))
    final = app.invoke({"data": data})

    if final.get("errors"):
        print("Schema validation failed after retries:", file=sys.stderr)
        for err in final["errors"]:
            print(f"  - {err}", file=sys.stderr)
        return 1

    result = (
        {"code": 200, "message": "User retrieved", "data": final["data"]}
        if was_envelope
        else final["data"]
    )
    if args.out:
        out_path = args.out
    elif args.in_place:
        out_path = args.input
    else:
        out_path = args.input.with_suffix(".filled.json")
    out_path.write_text(json.dumps(result, indent=4, ensure_ascii=False), encoding="utf-8")

    print(f"Done. Avatar: {final['data']['avatar_picture']}")
    print(f"Wrote: {out_path}")

    if args.apply_to_app:
        app_dir = REPO_ROOT / "app" / "src" / "data" / "profiles"
        app_dir.mkdir(parents=True, exist_ok=True)
        envelope = {"code": 200, "message": "User retrieved", "data": final["data"]}
        app_path = app_dir / f"{_app_stem(args.input)}.json"
        app_path.write_text(
            json.dumps(envelope, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Applied to app: {app_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
