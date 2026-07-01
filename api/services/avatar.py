"""Avatar generation via the existing LangGraph pipeline."""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATE_PATH = REPO_ROOT / "tools" / "avatar_gen" / "generate.py"
GENERATED_AVATAR_DIR = REPO_ROOT / "tools" / "avatar_gen" / "out"
GENERATED_AVATAR_ROUTE = "/generated/avatars"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_generate_module():
    name = "avatar_gen_generate"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, GENERATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load avatar generator from {GENERATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _public_api_base_url() -> str:
    explicit = os.getenv("PUBLIC_API_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")

    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway_domain:
        if railway_domain.startswith(("http://", "https://")):
            return railway_domain.rstrip("/")
        return f"https://{railway_domain}".rstrip("/")

    return "http://localhost:8000"


def _public_avatar_url(uri: str) -> str:
    if not uri.startswith("file:"):
        return uri

    parsed = urlparse(uri)
    path = Path(url2pathname(unquote(parsed.path))).resolve()
    try:
        path.relative_to(GENERATED_AVATAR_DIR)
    except ValueError:
        return uri

    return f"{_public_api_base_url()}{GENERATED_AVATAR_ROUTE}/{path.name}"


def run_avatar_pipeline(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full avatar pipeline and return updated user data."""
    gen = _load_generate_module()
    settings = gen.Settings()
    settings.host_images = False
    settings.out_dir = GENERATED_AVATAR_DIR
    gen.require(settings)
    llm = gen.make_llm(settings)
    app = gen.build_graph(settings, llm)
    final = app.invoke({"data": dict(user_data)})
    if final.get("errors"):
        raise RuntimeError("; ".join(final["errors"]))
    data = final["data"]
    avatar_picture = data.get("avatar_picture")
    if isinstance(avatar_picture, str):
        data["avatar_picture"] = _public_avatar_url(avatar_picture)
    return data


def mark_generating(user_data: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(user_data)
    data["avatar_status"] = "generating"
    data["avatar_generation_started_at"] = _now_iso()
    data["updated_at"] = _now_iso()
    return data


def mark_failed(user_data: Dict[str, Any], error: str) -> Dict[str, Any]:
    data = dict(user_data)
    data["avatar_status"] = "failed"
    data["updated_at"] = _now_iso()
    # Keep error out of schema — log server-side only
    return data
