from dash import html

from components.core.constants import BG3, GRID, TEXT, ACCENT


def section_title(text, accent=ACCENT, margin_bottom="16px", height="18px"):
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "gap": "8px",
            "marginBottom": margin_bottom,
            "paddingBottom": "10px",
            "borderBottom": f"1px solid {GRID}",
        },
        children=[
            html.Div(
                style={
                    "width": "3px",
                    "height": height,
                    "background": accent,
                    "borderRadius": "2px",
                    "flexShrink": "0",
                }
            ),
            html.Div(
                text,
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": "2.5px",
                    "color": TEXT if accent == ACCENT else accent,
                },
            ),
        ],
    )


def table_th(text):
    return html.Th(
        text,
        style={
            "fontSize": "9px",
            "fontWeight": "700",
            "letterSpacing": "1.8px",
            "color": "#444",
            "padding": "8px 12px",
            "textAlign": "left",
            "borderBottom": f"1px solid {GRID}",
            "textTransform": "uppercase",
            "whiteSpace": "nowrap",
        },
    )


def table_td(content, bold=False, color=None, size="12px", padding="7px 10px"):
    return html.Td(
        content,
        style={
            "padding": padding,
            "fontSize": size,
            "color": color or TEXT,
            "borderBottom": f"1px solid {BG3}",
            "fontWeight": "700" if bold else "400",
        },
    )


def position_badge(pos, elim=False):
    podium = {1: "#ffd700", 2: "#c0c0c0", 3: "#cd7f32"}
    if elim:
        bg, tc = "#1a0508", ACCENT
    elif pos in podium:
        bg, tc = podium[pos], "#000"
    else:
        bg, tc = BG3, TEXT

    border = (
        f"1px solid {ACCENT}"
        if elim
        else ("none" if pos in podium else f"1px solid {GRID}")
    )

    return html.Div(
        str(pos),
        style={
            "width": "28px",
            "height": "28px",
            "borderRadius": "5px",
            "background": bg,
            "color": tc,
            "fontWeight": "700",
            "fontSize": "12px",
            "display": "flex",
            "border": border,
            "alignItems": "center",
            "justifyContent": "center",
        },
    )
