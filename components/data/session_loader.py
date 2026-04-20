from dash import html, dcc
from components.core.constants import ACCENT, GRID
from components.core.sessions import session_to_store, get_cached_session


def load_store_pair(year, gp):
    try:
        store_race = session_to_store(get_cached_session(year, gp, "R"))
    except Exception:
        store_race = None

    try:
        store_quali = session_to_store(get_cached_session(year, gp, "Q"))
    except Exception:
        store_quali = None

    return store_race, store_quali


def build_driver_checklist(drivers_data):
    default_sel = [drivers_data[0]["drv"]] if drivers_data else []

    checklist_options = []
    for d in drivers_data:
        drv = d["drv"]
        color = d["color"]
        pos = str(d["pos"]) if d["pos"] < 99 else "–"
        checklist_options.append(
            {
                "label": html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "8px",
                        "padding": "4px 0",
                    },
                    children=[
                        html.Span(
                            pos,
                            style={
                                "fontSize": "10px",
                                "color": "#555",
                                "minWidth": "16px",
                                "fontWeight": "700",
                            },
                        ),
                        html.Div(
                            style={
                                "width": "3px",
                                "height": "18px",
                                "background": color,
                                "borderRadius": "2px",
                            }
                        ),
                        html.Span(
                            drv,
                            style={
                                "fontSize": "12px",
                                "fontWeight": "600",
                                "color": color,
                            },
                        ),
                    ],
                ),
                "value": drv,
            }
        )

    checklist = dcc.Checklist(
        id="driver-checklist",
        options=checklist_options,
        value=default_sel,
        style={"maxHeight": "420px", "overflowY": "auto"},
        inputStyle={"marginRight": "8px", "accentColor": ACCENT},
        labelStyle={
            "display": "flex",
            "alignItems": "center",
            "cursor": "pointer",
            "marginBottom": "4px",
            "padding": "4px 6px",
            "borderRadius": "4px",
            "background": "#12151c",
            "border": f"1px solid {GRID}",
        },
    )

    return checklist, default_sel


def build_load_status(gp, year, store_race, store_quali):
    quali_ok = "✓ Q" if store_quali else "✗ Q"
    race_ok = "✓ R" if store_race else "✗ R"
    return f"{gp} {year}  {race_ok}  {quali_ok}"
