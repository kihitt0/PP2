"""Load / save leaderboard and settings from JSON files."""

import json
import os

_DIR = os.path.dirname(__file__)
LB_FILE  = os.path.join(_DIR, "leaderboard.json")
CFG_FILE = os.path.join(_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  [220, 60, 60],
    "difficulty": "Normal",
}

# ── Leaderboard ───────────────────────────────

def load_leaderboard() -> list:
    if os.path.exists(LB_FILE):
        try:
            with open(LB_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_leaderboard(entries: list):
    with open(LB_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def add_entry(name: str, score: int, distance: int):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score, "distance": distance})
    lb.sort(key=lambda e: e["score"], reverse=True)
    lb = lb[:10]
    save_leaderboard(lb)

# ── Settings ──────────────────────────────────

def load_settings() -> dict:
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE) as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(s: dict):
    with open(CFG_FILE, "w") as f:
        json.dump(s, f, indent=2)
