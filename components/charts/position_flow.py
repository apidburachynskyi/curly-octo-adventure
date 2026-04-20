import plotly.graph_objects as go
from components.core.constants import FONT
from components.ui.plot_theme import base_layout, axis_style


def build(laps: list, drivers: list, drv_colors: dict) -> go.Figure:
    fig = go.Figure()

    for drv in drivers:
        drv_laps = sorted(
            [l for l in laps if l["Driver"] == drv and l.get("Position")],
            key=lambda l: l["LapNumber"],
        )
        if not drv_laps:
            continue
        color = drv_colors.get(drv, "#AAAAAA")
        xs = [l["LapNumber"] for l in drv_laps]
        ys = [l["Position"] for l in drv_laps]

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line=dict(color=color, width=2.4, shape="hv"),
                name=drv,
                hovertemplate=f"<b>{drv}</b>  Lap %{{x}}  P%{{y}}<extra></extra>",
            )
        )

        fig.add_annotation(
            x=xs[-1],
            y=ys[-1],
            text=f"<b>{drv}</b>",
            showarrow=False,
            font=dict(size=11, color=color, family=FONT),
            xanchor="left",
            xshift=9,
        )

        fig.update_layout(
            **base_layout(height=420, margin={"l": 52, "r": 80, "t": 24, "b": 52}),
            hovermode="x unified",
            xaxis=axis_style("Lap"),
            yaxis=axis_style("Position", reversed_axis=True, dtick=1),
        ),
    return fig
