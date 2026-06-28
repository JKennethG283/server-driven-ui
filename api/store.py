"""JSON file stores for user profiles and generated UI designs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "api" / "data" / "users"
UI_DESIGN_DIR = REPO_ROOT / "api" / "data" / "ui_designs"
SEED_DIR = REPO_ROOT / "app" / "src" / "data" / "profiles"


def envelope(data: Dict[str, Any], message: str = "User retrieved") -> Dict[str, Any]:
    return {"code": 200, "message": message, "data": data}


def unwrap(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    if "data" in raw and isinstance(raw["data"], dict):
        return raw["data"], True
    return raw, False


class UserStore:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def seed_if_empty(self) -> None:
        if any(self.data_dir.glob("*.json")):
            return
        if not SEED_DIR.exists():
            return
        for path in sorted(SEED_DIR.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            data, _ = unwrap(raw)
            user_id = int(data["id"])
            self.save(user_id, data)

    def path_for(self, user_id: int) -> Path:
        return self.data_dir / f"{user_id}.json"

    def list_summaries(self) -> List[Dict[str, Any]]:
        summaries: List[Dict[str, Any]] = []
        for path in sorted(self.data_dir.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            data, _ = unwrap(raw)
            summaries.append(
                {
                    "id": str(data["id"]),
                    "user_id": data["id"],
                    "label": data.get("first_name") or path.stem,
                }
            )
        return summaries

    def get(self, user_id: int) -> Optional[Dict[str, Any]]:
        path = self.path_for(user_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def get_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        raw = self.get(user_id)
        if raw is None:
            return None
        data, _ = unwrap(raw)
        return data

    def save(self, user_id: int, data: Dict[str, Any], message: str = "User retrieved") -> Dict[str, Any]:
        payload = envelope(data, message)
        self.path_for(user_id).write_text(
            json.dumps(payload, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
        return payload

    def import_json(self, raw: Dict[str, Any], label: Optional[str] = None) -> Dict[str, Any]:
        data, _ = unwrap(raw)
        user_id = int(data["id"])
        return self.save(user_id, data, message="User imported")

    def patch(self, user_id: int, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self.get_data(user_id)
        if data is None:
            return None
        allowed = {
            "bio",
            "gender",
            "place_of_birth",
            "current_location",
            "dob_year",
            "dob_month",
            "dob_day",
        }
        for key, value in fields.items():
            if key in allowed:
                data[key] = value
        return self.save(user_id, data, message="User updated")


class UIDesignStore:
    def __init__(self, data_dir: Path = UI_DESIGN_DIR) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, user_id: int) -> Path:
        return self.data_dir / f"{user_id}.json"

    def get(self, user_id: int) -> Optional[Dict[str, Any]]:
        path = self.path_for(user_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, user_id: int, ui_design: Dict[str, Any]) -> Dict[str, Any]:
        self.path_for(user_id).write_text(
            json.dumps(ui_design, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
        return ui_design
