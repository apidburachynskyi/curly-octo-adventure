import os
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx
from flask_caching import Cache
from flask import request, Response
from functools import wraps
import fastf1
from pathlib import Path

from views.landing import landing_page
from views.championship import championship_view
from views.telemetry import telemetry_view, TABS, _tab_style
from views.root_layout import build_root_layout

from components.core.constants import PRELOADED_RACES, RACE_DATES, GRID, TEXT, ACCENT
from components.core.sessions import session_to_store
import components.core.sessions as _shared

from components.data.session_loader import (
    load_store_pair,
    build_driver_checklist,
    build_load_status,
)

from components.monitoring import (
    configure_monitoring,
    require_monitoring_auth,
    render_monitoring_page,
)


# FastF1 cache
CACHE_DIR = os.environ.get("FF1_CACHE_DIR", "./cache")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


# App
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="F1 Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server


@server.route("/health")
def health():
    return {"status": "ok"}, 200


_MONITORING_USER = os.environ.get("MONITORING_USER", "admin")
_MONITORING_PASSWORD = os.environ.get("MONITORING_PASSWORD", "f1admin2026")

configure_monitoring(_MONITORING_USER, _MONITORING_PASSWORD)


@server.route("/monitoring")
@require_monitoring_auth
def monitoring_page():
    return render_monitoring_page(), 200, {"Content-Type": "text/html"}


# Server-side session cache
_server_cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 7200,
    },
)


def get_cached_session(year, gp, session_type):
    """Load FastF1 session returns from RAM on subsequent calls."""
    key = f"ff1_{year}_{gp}_{session_type}".replace(" ", "_")
    session = _server_cache.get(key)
    if session is None:
        session = fastf1.get_session(int(year), gp, session_type)
        session.load()
        _server_cache.set(key, session)
    return session


_shared.get_cached_session = get_cached_session


# Main layout
app.layout = build_root_layout()


# Navigation callbacks
@app.callback(
    Output("app-root", "children"),
    Input("btn-go-telemetry", "n_clicks"),
    Input("btn-go-championship", "n_clicks"),
    Input("btn-back-from-champ", "n_clicks"),
    Input("btn-back-from-dash", "n_clicks"),
    prevent_initial_call=True,
)
def navigate(*_):
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    if btn == "btn-go-telemetry":
        return telemetry_view()
    if btn == "btn-go-championship":
        return championship_view()
    # Both back buttons → landing
    return landing_page()


# GP list
@app.callback(
    Output("dd-gp", "options"),
    Output("dd-gp", "value"),
    Input("dd-year", "value"),
)
def update_gp_options(year):
    from datetime import date

    today = str(date.today())
    races = PRELOADED_RACES.get(int(year), [])
    dates = RACE_DATES.get(int(year), {})
    options = []
    first_available = None
    for r in races:
        race_date = dates.get(r, "")
        past = not race_date or race_date <= today
        if past and first_available is None:
            first_available = r
        options.append(
            {
                "label": r if past else f"{r} — {race_date}",
                "value": r,
                "disabled": not past,
            }
        )
    return options, first_available


def build_tab_state(active_tab="overview"):
    page_styles = [
        {"display": "block"} if tid == active_tab else {"display": "none"}
        for tid, _, _ in TABS
    ]
    btn_styles = [_tab_style(tid == active_tab) for tid, _, _ in TABS]
    return active_tab, page_styles, btn_styles


# Load session
@app.callback(
    Output("store-race", "data"),
    Output("store-quali", "data"),
    Output("store-session-key", "data"),
    Output("load-status", "children"),
    Output("driver-checklist-wrap", "children"),
    Output("driver-count", "children", allow_duplicate=True),
    Output("store-selected-drivers", "data", allow_duplicate=True),
    Output("active-tab", "data", allow_duplicate=True),
    *[Output(f"page-{tid}", "style", allow_duplicate=True) for tid, _, _ in TABS],
    *[Output(f"tab-btn-{tid}", "style", allow_duplicate=True) for tid, _, _ in TABS],
    Input("btn-load", "n_clicks"),
    State("dd-year", "value"),
    State("dd-gp", "value"),
    prevent_initial_call=True,
)
def load_session(_, year, gp):
    n_outputs = 7 + 1 + len(TABS) + len(TABS)  # 2 stores + key + 4 ui + tab outputs
    no_change = [dash.no_update] * n_outputs

    if not all([year, gp]):
        no_change[3] = "Select year and GP."
        return no_change
    store_race, store_quali = load_store_pair(year, gp)

    if store_race is None and store_quali is None:
        no_change[3] = "Could not load Race or Qualifying for this event."
        return no_change

    primary = store_race or store_quali
    drivers_data = primary.get("drivers", [])

    checklist, default_sel = build_driver_checklist(drivers_data)

    key = f"{year}|{gp}|R"
    status = build_load_status(gp, year, store_race, store_quali)
    count = f"{len(default_sel)}/{len(drivers_data)}"

    active_tab, page_styles, btn_styles = build_tab_state("overview")

    return (
        [
            store_race,
            store_quali,
            key,
            status,
            checklist,
            count,
            default_sel,
            active_tab,
        ]
        + page_styles
        + btn_styles
    )


# Sync checklist
# This is the single source of truth: every tick/untick insta
@app.callback(
    Output("store-selected-drivers", "data", allow_duplicate=True),
    Input("driver-checklist", "value"),
    prevent_initial_call=True,
)
def sync_driver_selection(selected):
    return selected or []


TAB_IDS = [tid for tid, _, _ in TABS]

# Tab switch — clientside so nginx never blocks it
app.clientside_callback(
    """
    function() {
        var args = Array.prototype.slice.call(arguments);
        var n_clicks = args.slice(0, args.length - 1);
        var active = args[args.length - 1];
        var tab_ids = """
    + str(TAB_IDS)
    + """;

        var triggered = window.dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0) {
            return window.dash_clientside.no_update;
        }

        var prop_id = triggered[0].prop_id;
        var new_tab = prop_id.replace('tab-btn-', '').replace('.n_clicks', '');

        var page_styles = tab_ids.map(function(tid) {
            return tid === new_tab ? {display: 'block'} : {display: 'none'};
        });

        var accent = '"""
    + ACCENT
    + """';
        var text = '"""
    + TEXT
    + """';
        var btn_styles = tab_ids.map(function(tid) {
            var active = tid === new_tab;
            return {
                padding: '12px 14px',
                fontSize: '11px', fontWeight: '700', letterSpacing: '1px',
                color: active ? text : '#555',
                background: 'transparent', border: 'none',
                borderBottom: active ? '2px solid ' + accent : '2px solid transparent',
                cursor: 'pointer', whiteSpace: 'nowrap'
            };
        });

        return [new_tab].concat(page_styles).concat(btn_styles);
    }
    """,
    Output("active-tab", "data"),
    *[Output(f"page-{tid}", "style") for tid, _, _ in TABS],
    *[Output(f"tab-btn-{tid}", "style") for tid, _, _ in TABS],
    *[Input(f"tab-btn-{tid}", "n_clicks") for tid, _, _ in TABS],
    State("active-tab", "data"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=True, port=8050)
