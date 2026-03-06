import json
import os
import logging
from datetime import datetime
from typing import Optional

from config import DB_PATH, ADMIN_ID, DEFAULT_SETTINGS

logger = logging.getLogger(__name__)


def _load_db() -> dict:
    if not os.path.exists(DB_PATH):
        return {"admins": [ADMIN_ID], "users": {}, "allowed_users": [ADMIN_ID]}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.error("Failed to load database, creating new one")
        return {"admins": [ADMIN_ID], "users": {}, "allowed_users": [ADMIN_ID]}


def _save_db(db: dict) -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def is_admin(user_id: int) -> bool:
    db = _load_db()
    return user_id in db.get("admins", [ADMIN_ID])


def is_allowed(user_id: int) -> bool:
    db = _load_db()
    return user_id in db.get("allowed_users", [])


def add_user(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> bool:
    db = _load_db()
    uid = str(user_id)
    if user_id not in db["allowed_users"]:
        db["allowed_users"].append(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "added_at": datetime.now().isoformat(),
            "settings": DEFAULT_SETTINGS.copy(),
            "history": [],
        }
    _save_db(db)
    return True


def remove_user(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return False
    db = _load_db()
    if user_id in db["allowed_users"]:
        db["allowed_users"].remove(user_id)
    uid = str(user_id)
    if uid in db["users"]:
        del db["users"][uid]
    _save_db(db)
    return True


def get_allowed_users() -> list[dict]:
    db = _load_db()
    result = []
    for uid_str, info in db.get("users", {}).items():
        uid = int(uid_str)
        if uid in db.get("allowed_users", []):
            result.append(info)
    return result


def get_user_count() -> int:
    db = _load_db()
    return len(db.get("allowed_users", []))


def ensure_user_profile(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> None:
    db = _load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "added_at": datetime.now().isoformat(),
            "settings": DEFAULT_SETTINGS.copy(),
            "history": [],
        }
        _save_db(db)


def get_user_settings(user_id: int) -> dict:
    db = _load_db()
    uid = str(user_id)
    user = db["users"].get(uid)
    if not user:
        return DEFAULT_SETTINGS.copy()
    settings = user.get("settings", DEFAULT_SETTINGS.copy())
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value
    return settings


def update_user_settings(user_id: int, **kwargs) -> None:
    db = _load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        return
    if "settings" not in db["users"][uid]:
        db["users"][uid]["settings"] = DEFAULT_SETTINGS.copy()
    db["users"][uid]["settings"].update(kwargs)
    _save_db(db)


def get_user_history(user_id: int) -> list[dict]:
    db = _load_db()
    uid = str(user_id)
    user = db["users"].get(uid)
    if not user:
        return []
    return user.get("history", [])


def add_to_history(user_id: int, role: str, content) -> None:
    from config import MAX_HISTORY_MESSAGES
    db = _load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        return
    if "history" not in db["users"][uid]:
        db["users"][uid]["history"] = []
    db["users"][uid]["history"].append({"role": role, "content": content})
    if len(db["users"][uid]["history"]) > MAX_HISTORY_MESSAGES:
        db["users"][uid]["history"] = db["users"][uid]["history"][-MAX_HISTORY_MESSAGES:]
    _save_db(db)


def clear_history(user_id: int) -> None:
    db = _load_db()
    uid = str(user_id)
    if uid in db["users"]:
        db["users"][uid]["history"] = []
        _save_db(db)
