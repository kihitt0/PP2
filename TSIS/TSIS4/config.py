import json
import os

_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.join(_DIR, "settings.json")

DEFAULT = {
    "snake_color": [0, 200, 0],
    "grid": True,
    "sound": True,
}

def load():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return {**DEFAULT, **json.load(f)}
        except Exception:
            pass
    return DEFAULT.copy()

def save(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
