from dash import html, dcc
import pages.championship as pg_championship
from components.core.constants import BG2, GRID, TEXT, FONT
from components.ui.hidden_ids import hidden_callback_placeholders


def championship_view():
    return html.Div(
        style={"background": "#08090d", "minHeight": "100vh", "fontFamily": FONT},
        children=[
            *hidden_callback_placeholders(),
            html.Div(
                style={
                    "height": "3px",
                    "background": "linear-gradient(90deg,#e8002d,#ff4d6d)",
                }
            ),
            # Top bar with back button and year selector
            html.Div(
                style={
                    "background": BG2,
                    "borderBottom": f"1px solid {GRID}",
                    "padding": "12px 20px",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "16px",
                },
                children=[
                    html.Button(
                        "← BACK",
                        id="btn-back-from-champ",
                        n_clicks=0,
                        style={
                            "background": "transparent",
                            "border": f"1px solid {GRID}",
                            "color": "#888",
                            "padding": "6px 14px",
                            "borderRadius": "4px",
                            "fontSize": "11px",
                            "fontWeight": "700",
                            "letterSpacing": "1px",
                            "cursor": "pointer",
                        },
                    ),
                    html.Div(
                        "🏆 CHAMPIONSHIP",
                        style={
                            "fontSize": "14px",
                            "fontWeight": "700",
                            "letterSpacing": "2px",
                            "color": TEXT,
                        },
                    ),
                    html.Div(
                        style={
                            "marginLeft": "auto",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "10px",
                        },
                        children=[
                            html.Span(
                                "SEASON:",
                                style={
                                    "fontSize": "11px",
                                    "color": "#555",
                                    "fontWeight": "700",
                                },
                            ),
                            dcc.Dropdown(
                                id="champ-year-dd",
                                options=[
                                    {"label": str(y), "value": y}
                                    for y in [2026, 2025, 2024]
                                ],
                                value=2026,
                                clearable=False,
                                style={"width": "100px"},
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                style={"padding": "20px"},
                children=[pg_championship.layout],
            ),
        ],
    )
