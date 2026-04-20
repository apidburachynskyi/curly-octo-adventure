import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.core.constants import BG2, GRID, TEXT, FONT
from components.core.formatting import hex_to_rgba
from components.ui.plot_theme import base_layout, axis_style

_PLOT_BG = "#0a0c11"


def build(driver_telemetry: dict) -> go.Figure:
    fig = make_subplots(
        rows=5,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.28, 0.18, 0.18, 0.16, 0.20],
        vertical_spacing=0.025,
        subplot_titles=["SPEED  (km/h)", "THROTTLE  (%)", "BRAKE  (%)", "GEAR", "RPM"],
    )

    for drv, data in driver_telemetry.items():
        tel = data["tel"]
        color = data["color"]
        dist = tel["Distance"]

        fig.add_trace(
            go.Scatter(
                x=dist,
                y=tel["Speed"],
                mode="lines",
                line=dict(color=color, width=2.2),
                name=drv,
                legendgroup=drv,
                showlegend=True,
                hovertemplate=f"<b>{drv}</b>  %{{y:.0f}} km/h<extra></extra>",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=dist,
                y=tel["Throttle"],
                mode="lines",
                fill="tozeroy",
                fillcolor=hex_to_rgba(color, 0.13),
                line=dict(color=color, width=1.8),
                legendgroup=drv,
                showlegend=False,
                hovertemplate=f"<b>{drv}</b>  %{{y:.0f}}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

        brake_pct = tel["Brake"].astype(float) * 100
        fig.add_trace(
            go.Scatter(
                x=dist,
                y=brake_pct,
                mode="lines",
                fill="tozeroy",
                fillcolor=hex_to_rgba(color, 0.22),
                line=dict(color=color, width=1.6),
                legendgroup=drv,
                showlegend=False,
                hovertemplate=f"<b>{drv}</b>  %{{y:.0f}}%<extra></extra>",
            ),
            row=3,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=dist,
                y=tel["nGear"],
                mode="lines",
                line=dict(color=color, width=2.0, shape="hv"),
                legendgroup=drv,
                showlegend=False,
                hovertemplate=f"<b>{drv}</b>  G%{{y}}<extra></extra>",
            ),
            row=4,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=dist,
                y=tel["RPM"],
                mode="lines",
                line=dict(color=color, width=1.8),
                legendgroup=drv,
                showlegend=False,
                hovertemplate=f"<b>{drv}</b>  %{{y:.0f}} rpm<extra></extra>",
            ),
            row=5,
            col=1,
        )

    for row, (label, rng) in enumerate(
        [
            ("km/h", None),
            ("%", [0, 105]),
            ("%", [0, 105]),
            ("gear", None),
            ("rpm", None),
        ],
        start=1,
    ):
        kw = dict(
            gridcolor="#161920",
            zeroline=False,
            tickfont=dict(size=9, color="#777"),
            title_text=label,
            title_font=dict(size=9, color="#555"),
            showline=True,
            linecolor="#1a1d24",
        )
        if rng:
            kw["range"] = rng
        fig.update_yaxes(**kw, row=row, col=1)

    for row in range(1, 5):
        fig.update_xaxes(
            showticklabels=False,
            gridcolor="#161920",
            showline=True,
            linecolor="#1a1d24",
            row=row,
            col=1,
        )
    fig.update_xaxes(
        gridcolor="#161920",
        tickfont=dict(size=10, color="#777"),
        title_text="Distance (m)",
        title_font=dict(size=10, color="#666"),
        showline=True,
        linecolor="#1a1d24",
        row=5,
        col=1,
    )

    for ann in fig.layout.annotations:
        ann.update(font=dict(size=9, color="#555", family=FONT), x=0.01, xanchor="left")

    fig.update_layout(
        **base_layout(
            height=640, margin={"l": 60, "r": 28, "t": 40, "b": 52}, legend_y=1.02
        ),
        hovermode="x unified",
    )
    return fig
