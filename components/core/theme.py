from dash import html

from components.core.constants import BG2, FONT, TEXT

TEAM_LOGO = {
    "mclaren": "mclaren",
    "ferrari": "ferrari",
    "scuderia ferrari": "ferrari",
    "red bull": "redbull",
    "red bull racing": "redbull",
    "oracle red bull": "redbull",
    "mercedes": "mercedes",
    "aston martin": "astonmartin",
    "aston martin f1": "astonmartin",
    "alpine": "alpine",
    "alpine f1": "alpine",
    "williams": "williams",
    "racing bulls": "racingbulls",
    "rb": "racingbulls",
    "visa cashapp rb": "racingbulls",
    "kick sauber": "sauber",
    "sauber": "sauber",
    "haas": "haas",
    "haas f1 team": "haas",
    "haas f1": "haas",
    "mclaren f1 team": "mclaren",
    "scuderia ferrari hp": "ferrari",
    "oracle red bull racing": "redbull",
    "mercedes-amg petronas": "mercedes",
    "mercedes amg petronas": "mercedes",
    "aston martin aramco": "astonmartin",
    "bt sport alpine f1": "alpine",
    "williams racing": "williams",
    "visa cash app rb": "racingbulls",
    "stake f1 team kick sauber": "sauber",
    "moneygramm haas f1": "haas",
    "moneygram haas f1": "haas",
}


def team_logo_img(team_name, height="16px"):
    slug = TEAM_LOGO.get((team_name or "").lower().strip())
    if not slug:
        return None
    return html.Img(
        src=f"/assets/logos/{slug}.svg",
        style={
            "height": height,
            "width": "auto",
            "opacity": "0.9",
            "verticalAlign": "middle",
            "marginRight": "5px",
        },
    )


def chart_theme(
    height=380, margin_left=56, margin_right=28, margin_top=24, margin_bottom=52
):
    return dict(
        paper_bgcolor=BG2,
        plot_bgcolor="#0a0c11",
        font=dict(color="#888", family=FONT, size=10),
        height=height,
        margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#13161e",
            bordercolor="#252830",
            font=dict(color=TEXT, size=11),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=10, color="#aaa"),
            orientation="h",
            x=0,
            y=1.10,
        ),
        xaxis=dict(
            gridcolor="#161920",
            zeroline=False,
            tickfont=dict(size=10, color="#666"),
            showline=True,
            linecolor="#1a1d24",
        ),
        yaxis=dict(
            gridcolor="#161920",
            zeroline=False,
            tickfont=dict(size=10, color="#666"),
            showline=True,
            linecolor="#1a1d24",
        ),
    )


def axis_label(text):
    return dict(text=text, font=dict(size=9, color="#444", family=FONT))