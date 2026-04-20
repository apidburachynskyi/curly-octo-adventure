from components.core.constants import FONT, TEXT

PAPER_BG = "#0d0f14"
PLOT_BG = "#0a0c11"
GRID_COLOR = "#161920"
AXIS_LINE = "#1a1d24"
HOVER_BG = "#13161e"
HOVER_BORDER = "#252830"
LEGEND_BG = "rgba(13,15,20,0.92)"


def base_layout(height=420, margin=None, legend_y=1.06):
    return {
        "paper_bgcolor": PAPER_BG,
        "plot_bgcolor": PLOT_BG,
        "font": {"color": "#888", "family": FONT, "size": 10},
        "height": height,
        "margin": margin or {"l": 52, "r": 80, "t": 24, "b": 52},
        "hoverlabel": {
            "bgcolor": HOVER_BG,
            "bordercolor": HOVER_BORDER,
            "font": {"color": "#e0e0e0", "size": 11},
        },
        "legend": {
            "bgcolor": LEGEND_BG,
            "bordercolor": AXIS_LINE,
            "borderwidth": 1,
            "font": {"size": 11, "color": "#ccc"},
            "orientation": "h",
            "x": 0,
            "y": legend_y,
            "itemsizing": "constant",
        },
    }


def axis_style(
    title=None, tick_size=10, tick_color="#777", reversed_axis=False, dtick=None
):
    axis = {
        "gridcolor": GRID_COLOR,
        "zeroline": False,
        "tickfont": {"size": tick_size, "color": tick_color},
        "showline": True,
        "linecolor": AXIS_LINE,
    }
    if title is not None:
        axis["title"] = {"text": title, "font": {"size": 10, "color": "#666"}}
    if reversed_axis:
        axis["autorange"] = "reversed"
    if dtick is not None:
        axis["dtick"] = dtick
    return axis
