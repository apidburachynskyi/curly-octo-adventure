import math
import pandas as pd


def safe_str(value, fallback="–"):
    s = str(value) if value is not None else ""
    return fallback if s in ("", "nan", "NaT", "None", "NaN", "<NA>") else s


def format_gap(value, is_leader=False):
    if is_leader:
        return "–"
    try:
        if pd.isna(value):
            return "–"
        seconds = value.total_seconds() if hasattr(value, "total_seconds") else float(value)
        if math.isnan(seconds) or seconds < 0:
            return "–"
        return f"+{seconds:.3f}s"
    except Exception:
        return "–"


def format_laptime(value):
    try:
        if pd.isna(value):
            return "–"
        seconds = value.total_seconds() if hasattr(value, "total_seconds") else float(value)
        if math.isnan(seconds) or seconds <= 0:
            return "–"
        minutes = int(seconds // 60)
        return f"{minutes}:{seconds % 60:06.3f}"
    except Exception:
        return "–"


def timedelta_to_seconds(value):
    try:
        if pd.isna(value):
            return None
        s = value.total_seconds() if hasattr(value, "total_seconds") else float(value)
        return None if math.isnan(s) else s
    except Exception:
        return None


def hex_to_rgba(hex_color, alpha=0.08):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"