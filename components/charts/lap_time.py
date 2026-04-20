import plotly.graph_objects as go
from components.core.constants import TYRE_COLORS, FONT
from components.core.formatting import hex_to_rgba
from components.ui.plot_theme import base_layout, axis_style


def build(laps: list, drivers: list, drv_colors: dict) -> go.Figure:
    fig = go.Figure()
    seen = set()

    for drv in drivers:
        drv_laps = sorted(
            [l for l in laps if l["Driver"] == drv and l.get("LapTimeSec")],
            key=lambda l: l["LapNumber"],
        )
        if not drv_laps:
            continue
        driver_color = drv_colors.get(drv, "#AAAAAA")
        segments = _split_segments(drv_laps)

        for compound, lap_numbers, lap_times in segments:
            comp_color = TYRE_COLORS.get(compound, "#555")
            show_leg = compound not in seen
            seen.add(compound)
            fig.add_trace(
                go.Scatter(
                    x=lap_numbers,
                    y=lap_times,
                    mode="markers+lines",
                    marker=dict(
                        size=6, color=comp_color, line=dict(width=1, color=driver_color)
                    ),
                    line=dict(color=comp_color, width=2.2),
                    name=compound,
                    legendgroup=compound,
                    showlegend=show_leg,
                    hovertemplate=(
                        f"<b>{drv}</b>  Lap %{{x}}<br>"
                        f"<span style='color:{comp_color}'>{compound}</span>"
                        "  %{y:.3f}s<extra></extra>"
                    ),
                )
            )

        last = drv_laps[-1]
        fig.add_annotation(
            x=last["LapNumber"],
            y=last["LapTimeSec"],
            text=f"<b>{drv}</b>",
            showarrow=False,
            font=dict(size=11, color=driver_color, family=FONT),
            xanchor="left",
            xshift=9,
        )

    _PLOT_BG = "#0a0c11"
    fig.update_layout(
        **base_layout(height=420, margin={"l": 58, "r": 80, "t": 28, "b": 52}),
        hovermode="x unified",
        xaxis=axis_style("Lap"),
        yaxis=axis_style("Lap time (s)"),
    )
    return fig


def _split_segments(drv_laps):
    segs, cur_comp, cur_laps, cur_times = [], None, [], []
    for lap in drv_laps:
        c = lap.get("Compound", "UNKNOWN")
        if c != cur_comp:
            if cur_laps:
                segs.append((cur_comp, cur_laps, cur_times))
            cur_comp, cur_laps, cur_times = c, [], []
        cur_laps.append(lap["LapNumber"])
        cur_times.append(lap["LapTimeSec"])
    if cur_laps:
        segs.append((cur_comp, cur_laps, cur_times))
    return segs
