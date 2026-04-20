import plotly.graph_objects as go
import pandas as pd
from components.core.constants import TYRE_COLORS, FONT
from components.core.formatting import hex_to_rgba
from components.ui.plot_theme import base_layout, axis_style

_PLOT_BG = "#0a0c11"
_PAPER = "#0d0f14"
_GRID = "#161920"


def deg_rate_bar(stints_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    seen = set()

    for _, row in stints_df.iterrows():
        comp_color = TYRE_COLORS.get(row["Compound"], "#444")
        show_legend = row["Compound"] not in seen
        seen.add(row["Compound"])

        fig.add_trace(
            go.Bar(
                x=[f"{row['Driver']}  S{row['Stint']}"],
                y=[row["DegPerLap"]],
                marker=dict(
                    color=comp_color,
                    opacity=0.85,
                    line=dict(width=0),
                    pattern=dict(shape=""),
                ),
                name=row["Compound"],
                legendgroup=row["Compound"],
                showlegend=show_legend,
                hovertemplate=(
                    f"<b>{row['Driver']}</b>  Stint {row['Stint']}<br>"
                    f"Compound: <b>{row['Compound']}</b><br>"
                    f"Deg/lap: <b>{row['DegPerLap']:+.3f}s</b><br>"
                    f"Total: {row['TotalDeg']:+.3f}s  ·  {row['Laps']} laps"
                    "<extra></extra>"
                ),
            )
        )

    # Zero reference line
    fig.add_hline(y=0, line=dict(color="#2a2d35", width=1.5))

    fig.update_layout(
        **base_layout(height=400, margin={"l": 58, "r": 24, "t": 28, "b": 72}),
        xaxis={**axis_style(None), "tickangle": -30},
        yaxis=axis_style("s / lap  (+ = degrading)"),
    )
    return fig


def laptime_boxplot(clean_laps_df: pd.DataFrame, drivers: list) -> go.Figure:
    fig = go.Figure()
    seen = set()
    compound_order = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

    for drv in drivers:
        for compound in compound_order:
            subset = clean_laps_df[
                (clean_laps_df["Driver"] == drv)
                & (clean_laps_df["Compound"] == compound)
            ]
            if subset.empty:
                continue
            comp_color = TYRE_COLORS.get(compound, "#444")
            show_legend = compound not in seen
            seen.add(compound)

            fig.add_trace(
                go.Box(
                    y=subset["LapTime"],
                    name=f"{drv}  {compound}",
                    marker=dict(
                        color=comp_color,
                        size=4,
                        line=dict(outlierwidth=1, outliercolor=comp_color),
                    ),
                    line=dict(color=comp_color, width=2),
                    fillcolor=hex_to_rgba(comp_color, alpha=0.10),
                    boxpoints="outliers",
                    legendgroup=compound,
                    showlegend=show_legend,
                    hovertemplate=f"<b>{drv}</b>  {compound}<br>%{{y:.3f}}s<extra></extra>",
                )
            )

    fig.update_layout(
        **base_layout(height=420, margin={"l": 58, "r": 24, "t": 28, "b": 80}),
        hovermode="closest",
        xaxis={**axis_style(None), "tickangle": -35},
        yaxis=axis_style("Lap time (s)"),
    )
    return fig
