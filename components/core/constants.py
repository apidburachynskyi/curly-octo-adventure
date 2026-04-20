import os
import fastf1
from pathlib import Path

CACHE_DIR = os.environ.get("FF1_CACHE_DIR", "./cache")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

_FALLBACK_RACES = {
    2026: ["Melbourne", "Shanghai", "Suzuka"],
    2025: [
        "Melbourne", "Shanghai", "Suzuka", "Sakhir", "Jeddah", "Miami Gardens",
        "Imola", "Monte Carlo", "Barcelona", "Montreal", "Spielberg",
        "Silverstone", "Spa-Francorchamps", "Budapest", "Zandvoort", "Monza",
        "Baku", "Marina Bay", "Austin", "Mexico City", "São Paulo",
        "Las Vegas", "Lusail", "Yas Marina",
    ],
    2024: [
        "Sakhir", "Jeddah", "Melbourne", "Suzuka", "Shanghai", "Miami Gardens",
        "Imola", "Monte Carlo", "Montreal", "Barcelona", "Spielberg",
        "Silverstone", "Budapest", "Spa-Francorchamps", "Zandvoort", "Monza",
        "Baku", "Marina Bay", "Austin", "Mexico City", "São Paulo",
        "Las Vegas", "Lusail", "Yas Marina",
    ],
}


def _load_races():
    races_json = Path(__file__).parent.parent.parent / "data" / "races.json"
    if races_json.exists():
        try:
            import json as _json
            raw = _json.loads(races_json.read_text())
            races, dates = {}, {}
            for k, entries in raw.items():
                year = int(k)
                if entries and isinstance(entries[0], dict):
                    races[year] = [e["name"] for e in entries]
                    dates[year] = {e["name"]: e["date"] for e in entries}
                else:
                    races[year] = entries
                    dates[year] = {}
            return races, dates
        except Exception:
            pass
    return _FALLBACK_RACES, {}


PRELOADED_RACES, RACE_DATES = _load_races()
AVAILABLE_YEARS = sorted(PRELOADED_RACES.keys(), reverse=True)
AVAILABLE_SESSIONS = [
    {"label": "Race", "value": "R"},
    {"label": "Qualifying", "value": "Q"},
]

BG = "#08090d"
BG2 = "#0d0f14"
BG3 = "#12151c"
GRID = "#1a1d24"
TEXT = "#e0e0e0"
MUTED = "#555555"
ACCENT = "#e8002d"
FONT = "Arial, sans-serif"

TYRE_COLORS = {
    "SOFT": "#e8002d",
    "MEDIUM": "#ffd700",
    "HARD": "#f0f0f0",
    "INTERMEDIATE": "#39b54a",
    "WET": "#0067ff",
    "UNKNOWN": "#888888",
}