import time
import fastf1

from components.core.constants import CACHE_DIR
from components.core.formatting import (
    safe_str,
    format_laptime,
    timedelta_to_seconds,
)
from components.data.results_loader import (
    fetch_race_results,
    fetch_quali_results,
    build_results_from_laps,
)


def get_driver_meta(session, driver_code):
    try:
        info = session.get_driver(driver_code)
        return {
            "color": "#" + info.get("TeamColor", "AAAAAA"),
            "team": info.get("TeamName", ""),
            "first": info.get("FirstName", ""),
            "last": info.get("LastName", driver_code),
        }
    except Exception:
        return {"color": "#AAAAAA", "team": "", "first": "", "last": driver_code}


def _retry(func, retries=3, delay=2, fallback=None):
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == retries:
                print(f"[F1] Failed after {retries} attempts: {e}")
                return fallback
            print(f"[F1] Attempt {attempt} failed: {e} — retry in {delay}s")
            time.sleep(delay)


def load_session(year, gp, session_type):
    def _load():
        s = fastf1.get_session(int(year), gp, session_type)
        s.load()
        return s

    result = _retry(_load, retries=3, delay=3)
    if result is None:
        raise RuntimeError(f"Could not load {year} {gp} {session_type}")
    return result


def get_cached_session(year, gp, session_type):
    return load_session(year, gp, session_type)


def is_qualifying(session):
    try:
        return session.session_info.get("Type", "") in ("Q", "SQ", "SS")
    except Exception:
        return False


def session_to_store(session):
    store = {}
    store["session_type"] = session.name

    event = session.event
    store["event"] = {
        "name": safe_str(event.get("EventName", "")),
        "country": safe_str(event.get("Country", "")),
        "circuit": safe_str(event.get("Location", "")),
        "year": int(event["EventDate"].year) if hasattr(event.get("EventDate", ""), "year") else 0,
    }

    try:
        wd = _retry(lambda: session.weather_data, retries=2, fallback=None)
        if wd is not None and not wd.empty:
            w = wd.iloc[len(wd) // 2]

            def _wv(col):
                try:
                    return round(float(w[col]), 1)
                except Exception:
                    return None

            store["weather"] = {
                "air_temp": _wv("AirTemp"),
                "track_temp": _wv("TrackTemp"),
                "humidity": _wv("Humidity"),
                "wind": _wv("WindSpeed"),
            }
        else:
            store["weather"] = {}
    except Exception:
        store["weather"] = {}

    try:
        is_race = store["session_type"] == "Race"
        res = _retry(lambda: session.results, retries=2, fallback=None)

        meta_map = {}
        if res is not None and not res.empty:
            for _, r in res.iterrows():
                drv = safe_str(r.get("Abbreviation", ""), "")
                if not drv:
                    continue
                raw_color = safe_str(r.get("TeamColor", "AAAAAA"), "AAAAAA")
                color = "#" + raw_color.replace("#", "").strip()
                if len(color) != 7:
                    color = "#AAAAAA"
                meta_map[drv] = {
                    "color": color,
                    "first": safe_str(r.get("FirstName", "")),
                    "last": safe_str(r.get("LastName", drv), drv),
                    "team": safe_str(r.get("TeamName", "–")),
                    "status": safe_str(r.get("Status", "")),
                }

        ev = store["event"]
        year = ev.get("year", 0)
        gp = ev.get("name", "")

        if is_race:
            rows = fetch_race_results(year, gp)
            if rows:
                for row in rows:
                    row["color"] = meta_map.get(row["drv"], {}).get("color", "#AAAAAA")
                    row["q1"] = "–"
                    row["q2"] = "–"
                    row["q3"] = "–"
            else:
                rows = build_results_from_laps(session, meta_map)
        else:
            rows = fetch_quali_results(year, gp)
            if rows:
                for row in rows:
                    row["color"] = meta_map.get(row["drv"], {}).get("color", "#AAAAAA")
                    row["gap"] = row.get("q3") or row.get("q1", "–")
                    row["grid"] = None
                    row["status"] = ""
            else:
                rows = []
                if res is not None and not res.empty:
                    for _, r in res.iterrows():
                        drv = safe_str(r.get("Abbreviation", ""), "")
                        if not drv:
                            continue
                        try:
                            pos = int(float(str(r.get("ClassifiedPosition", 99))))
                        except Exception:
                            pos = 99
                        meta = meta_map.get(drv, {})
                        rows.append(
                            {
                                "pos": pos,
                                "drv": drv,
                                "first": meta.get("first", ""),
                                "last": meta.get("last", drv),
                                "team": meta.get("team", "–"),
                                "color": meta.get("color", "#AAAAAA"),
                                "grid": None,
                                "gap": "–",
                                "status": "",
                                "q1": format_laptime(r.get("Q1")),
                                "q2": format_laptime(r.get("Q2")),
                                "q3": format_laptime(r.get("Q3")),
                            }
                        )

        store["results"] = sorted(rows, key=lambda x: x.get("pos", 99))
    except Exception as e:
        print(f"[results] {e}")
        store["results"] = []

    try:
        laps = session.laps.copy()
        laps["LapTimeSec"] = laps["LapTime"].dt.total_seconds()
        laps["Compound"] = laps["Compound"].fillna("UNKNOWN").str.upper()
        laps["TyreLife"] = laps["TyreLife"].fillna(0).astype(int)
        laps["Stint"] = laps["Stint"].fillna(0).astype(int)

        time_cols = ["Sector1Time", "Sector2Time", "Sector3Time", "PitInTime", "PitOutTime"]
        for col in time_cols:
            if col in laps.columns:
                laps[col + "Sec"] = laps[col].apply(timedelta_to_seconds)

        keep = [
            "Driver", "Team", "LapNumber", "LapTimeSec", "Compound",
            "TyreLife", "Stint", "Position"
        ] + [c + "Sec" for c in time_cols if c in laps.columns]
        keep = [c for c in keep if c in laps.columns]

        float_cols = [c for c in keep if "Sec" in c or c == "LapTimeSec"]
        laps[float_cols] = laps[float_cols].round(3)
        store["laps"] = laps[keep].to_dict("records")
    except Exception:
        store["laps"] = []

    try:
        res = _retry(lambda: session.results, retries=2, fallback=None)
        drivers = []
        if res is not None and not res.empty:
            for _, r in res.iterrows():
                drv = safe_str(r.get("Abbreviation", ""), "")
                if not drv:
                    continue
                try:
                    pos = int(float(str(r.get("ClassifiedPosition", 99))))
                except Exception:
                    pos = 99
                raw_color = safe_str(r.get("TeamColor", "AAAAAA"), "AAAAAA")
                color = "#" + raw_color.replace("#", "").strip()
                if len(color) != 7:
                    color = "#AAAAAA"
                drivers.append(
                    {
                        "drv": drv,
                        "pos": pos,
                        "color": color,
                        "team": safe_str(r.get("TeamName", "–")),
                        "first": safe_str(r.get("FirstName", "")),
                        "last": safe_str(r.get("LastName", drv), drv),
                    }
                )
        store["drivers"] = sorted(drivers, key=lambda x: x["pos"])
    except Exception:
        store["drivers"] = []

    store["fastest_lap"] = {}
    store["race_control"] = {}
    store["compounds"] = {}
    return store