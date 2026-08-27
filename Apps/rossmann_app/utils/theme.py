"""
theme.py — shared visual system for the app. Dark mode only.

Signal-color language: this app makes go/caution/stop decisions (store
open/closed, eligible/declined, risk tier), so the whole UI is built
around a traffic-light glow system — green/yellow/red — used consistently
everywhere a state is shown, from the sidebar to the risk dashboard.

Nothing in this file touches prediction, feature engineering, or business
logic — it only renders what those layers already produce.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG_VOID = "#0A0F0D"
BG_SURFACE = "#121917"
BG_ELEVATED = "#182420"
BORDER = "#22322C"
TEXT_PRIMARY = "#EAF6EF"
TEXT_MUTED = "#7E948C"

GREEN = "#39E67A"
GREEN_DIM = "#1F7A46"
YELLOW = "#F4C542"
RED = "#FF5C5C"

SIGNAL = {"green": GREEN, "yellow": YELLOW, "red": RED}


def apply_theme():
    """Call once at the top of every page, right after st.set_page_config()."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

    /* ---------- base / dark-mode lock ---------- */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {BG_VOID} !important;
        color: {TEXT_PRIMARY};
        font-family: 'Inter', sans-serif;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    #MainMenu, footer {{ visibility: hidden; }}

    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }}
    code, .stCodeBlock, [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* ---------- sidebar shell ---------- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BG_SURFACE} 0%, {BG_VOID} 100%) !important;
        border-right: 1px solid {BORDER};
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 0.5rem; }}

    /* ---------- 3D glowing sidebar nav buttons ---------- */
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNavLink"] {{
        background: linear-gradient(180deg, {BG_ELEVATED} 0%, {BG_SURFACE} 100%) !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        margin: 4px 12px !important;
        padding: 10px 14px !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.04) inset,
            0 -2px 6px rgba(0,0,0,0.35) inset,
            0 3px 6px rgba(0,0,0,0.45) !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
        color: {TEXT_MUTED} !important;
        font-weight: 500 !important;
    }}
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNavLink"]:hover {{
        transform: translateY(-1px);
        border-color: {GREEN_DIM} !important;
        color: {TEXT_PRIMARY} !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.06) inset,
            0 -2px 6px rgba(0,0,0,0.35) inset,
            0 4px 10px rgba(0,0,0,0.5),
            0 0 14px rgba(57,230,122,0.18) !important;
    }}
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNavLink"][aria-current="page"] {{
        background: linear-gradient(180deg, #16321F 0%, #0F2417 100%) !important;
        border-color: {GREEN} !important;
        color: {GREEN} !important;
        font-weight: 600 !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.08) inset,
            0 -2px 6px rgba(0,0,0,0.4) inset,
            0 0 0 1px rgba(57,230,122,0.25),
            0 0 18px rgba(57,230,122,0.35) !important;
    }}

    /* ---------- 3D buttons in main content ---------- */
    .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {{
        background: linear-gradient(180deg, {BG_ELEVATED} 0%, {BG_SURFACE} 100%) !important;
        border: 1px solid {GREEN_DIM} !important;
        border-radius: 10px !important;
        color: {GREEN} !important;
        font-weight: 600 !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.05) inset,
            0 -2px 5px rgba(0,0,0,0.35) inset,
            0 3px 8px rgba(0,0,0,0.4) !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {{
        transform: translateY(-1px);
        border-color: {GREEN} !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.08) inset,
            0 -2px 5px rgba(0,0,0,0.35) inset,
            0 5px 14px rgba(0,0,0,0.5),
            0 0 20px rgba(57,230,122,0.3) !important;
    }}
    .stButton > button:active, [data-testid="stFormSubmitButton"] button:active {{
        transform: translateY(0px);
    }}

    /* ---------- inputs ---------- */
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    .stSelectbox > div > div, .stDateInput input {{
        background-color: {BG_ELEVATED} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 8px !important;
    }}

    /* ---------- metric cards ---------- */
    [data-testid="stMetric"] {{
        background: linear-gradient(160deg, {BG_ELEVATED} 0%, {BG_SURFACE} 100%);
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 14px 16px 10px 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }}

    /* ---------- dataframes ---------- */
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ---------- expander / containers ---------- */
    [data-testid="stExpander"] {{
        background-color: {BG_SURFACE};
        border: 1px solid {BORDER} !important;
        border-radius: 10px;
    }}

    /* ---------- scrollbar, small polish ---------- */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {BG_VOID}; }}
    ::-webkit-scrollbar-thumb {{ background: {BG_ELEVATED}; border-radius: 6px; border: 1px solid {BORDER}; }}

    /* ---------- custom component classes (used by helpers below) ---------- */
    .glow-pill {{
        display: inline-flex; align-items: center; gap: 7px;
        padding: 5px 13px; border-radius: 999px; font-weight: 600;
        font-size: 0.85rem; font-family: 'Inter', sans-serif;
        border: 1px solid var(--pill-color);
        color: var(--pill-color);
        background: color-mix(in srgb, var(--pill-color) 12%, {BG_SURFACE});
        box-shadow: 0 0 12px color-mix(in srgb, var(--pill-color) 45%, transparent);
    }}
    .glow-dot {{
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--pill-color);
        box-shadow: 0 0 8px 2px var(--pill-color);
        animation: pulse 1.8s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.45; }}
    }}

    .kpi-card {{
        background: linear-gradient(160deg, {BG_ELEVATED} 0%, {BG_SURFACE} 100%);
        border: 1px solid {BORDER};
        border-left: 3px solid var(--kpi-color, {GREEN});
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35), 0 0 16px color-mix(in srgb, var(--kpi-color, {GREEN}) 22%, transparent);
    }}
    .kpi-label {{ color: {TEXT_MUTED}; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }}
    .kpi-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 600; color: {TEXT_PRIMARY}; margin-top: 4px; }}
    .kpi-sub {{ color: var(--kpi-color, {GREEN}); font-size: 0.8rem; margin-top: 2px; }}

    .sidebar-brand {{
        display: flex; align-items: center; gap: 10px;
        padding: 14px 16px; margin: 8px 12px 14px 12px;
        background: linear-gradient(135deg, #14251C 0%, {BG_SURFACE} 100%);
        border: 1px solid {BORDER}; border-radius: 12px;
    }}
    .sidebar-brand-badge {{
        width: 34px; height: 34px; border-radius: 9px;
        background: linear-gradient(160deg, {GREEN} 0%, {GREEN_DIM} 100%);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #06140D;
        box-shadow: 0 0 14px rgba(57,230,122,0.45);
        flex-shrink: 0;
    }}
    .sidebar-brand-name {{ font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.95rem; color: {TEXT_PRIMARY}; }}
    .sidebar-brand-sub {{ font-size: 0.72rem; color: {TEXT_MUTED}; }}
    </style>
    """, unsafe_allow_html=True)


def sidebar_brand(name="Rossmann Finance", subtitle="AI Sales & Lending", initials="RS"):
    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="sidebar-brand-badge">{initials}</div>
        <div>
            <div class="sidebar-brand-name">{name}</div>
            <div class="sidebar-brand-sub">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_mode_lock():
    """Static 'dark mode only' indicator — replaces a toggle, since the app
    intentionally supports only one theme."""
    st.sidebar.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin:6px 16px 14px 16px;
                padding:8px 12px; background:{BG_SURFACE}; border:1px solid {BORDER};
                border-radius:10px; font-size:0.78rem; color:{TEXT_MUTED};">
        <span class="glow-dot" style="--pill-color:{GREEN};"></span>
        Dark mode — always on
    </div>
    """, unsafe_allow_html=True)


def glow_pill(label: str, signal: str = "green", dot: bool = True):
    """signal is one of 'green' | 'yellow' | 'red'."""
    color = SIGNAL.get(signal, GREEN)
    dot_html = f'<span class="glow-dot" style="--pill-color:{color};"></span>' if dot else ""
    st.markdown(
        f'<span class="glow-pill" style="--pill-color:{color};">{dot_html}{label}</span>',
        unsafe_allow_html=True,
    )
    return f'<span class="glow-pill" style="--pill-color:{color};">{dot_html}{label}</span>'


def glow_pill_html(label: str, signal: str = "green", dot: bool = True) -> str:
    """Same as glow_pill but returns the HTML string instead of rendering,
    for embedding inside other markdown/tables."""
    color = SIGNAL.get(signal, GREEN)
    dot_html = f'<span class="glow-dot" style="--pill-color:{color};"></span>' if dot else ""
    return f'<span class="glow-pill" style="--pill-color:{color};">{dot_html}{label}</span>'


def risk_signal(risk_tier: str) -> str:
    return {"Low": "green", "Medium": "yellow", "High": "red"}.get(risk_tier, "yellow")


def kpi_card(label: str, value: str, sub: str = "", signal: str = "green"):
    color = SIGNAL.get(signal, GREEN)
    st.markdown(f"""
    <div class="kpi-card" style="--kpi-color:{color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
    </div>
    """, unsafe_allow_html=True)


def section_divider():
    st.markdown(f"<hr style='border-color:{BORDER}; opacity:0.5; margin: 1.6rem 0;'>", unsafe_allow_html=True)


def gauge_chart(value: float, min_val: float, max_val: float, title: str,
                 good_is_low: bool = True, suffix: str = ""):
    """Plotly gauge using the green/yellow/red signal language. If good_is_low
    (e.g. error metrics), low values read green; otherwise high values read green."""
    import plotly.graph_objects as go

    span = max_val - min_val
    if good_is_low:
        steps = [
            {"range": [min_val, min_val + span * 0.33], "color": "rgba(57,230,122,0.25)"},
            {"range": [min_val + span * 0.33, min_val + span * 0.66], "color": "rgba(244,197,66,0.22)"},
            {"range": [min_val + span * 0.66, max_val], "color": "rgba(255,92,92,0.22)"},
        ]
    else:
        steps = [
            {"range": [min_val, min_val + span * 0.33], "color": "rgba(255,92,92,0.22)"},
            {"range": [min_val + span * 0.33, min_val + span * 0.66], "color": "rgba(244,197,66,0.22)"},
            {"range": [min_val + span * 0.66, max_val], "color": "rgba(57,230,122,0.25)"},
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"color": TEXT_PRIMARY, "family": "JetBrains Mono"}},
        title={"text": title, "font": {"color": TEXT_MUTED, "family": "Inter", "size": 14}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": TEXT_MUTED, "tickfont": {"color": TEXT_MUTED}},
            "bar": {"color": GREEN, "thickness": 0.28},
            "bgcolor": BG_ELEVATED,
            "borderwidth": 1,
            "bordercolor": BORDER,
            "steps": steps,
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


def donut_chart(labels, values, colors_map=None, title=""):
    import plotly.graph_objects as go
    default_colors = {"Low": GREEN, "Medium": YELLOW, "High": RED}
    colors_map = colors_map or default_colors
    colors = [colors_map.get(l, GREEN) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(color=BG_VOID, width=2)),
        textfont=dict(color=TEXT_PRIMARY, family="Inter"),
    ))
    fig.update_layout(
        title={"text": title, "font": {"color": TEXT_PRIMARY, "family": "Space Grotesk", "size": 15}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_PRIMARY),
        legend=dict(font=dict(color=TEXT_MUTED)),
        height=280,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def styled_bar_chart(df, x_col, y_col, title="", color=GREEN):
    import plotly.graph_objects as go
    fig = go.Figure(go.Bar(
        x=df[y_col], y=df[x_col], orientation="h",
        marker=dict(color=color, line=dict(color=GREEN_DIM, width=1)),
    ))
    fig.update_layout(
        title={"text": title, "font": {"color": TEXT_PRIMARY, "family": "Space Grotesk", "size": 15}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, autorange="reversed"),
        height=380,
        margin=dict(l=10, r=20, t=40, b=20),
    )
    return fig


def line_area_chart(df, x_col, y_col, title="", color=GREEN):
    import plotly.graph_objects as go
    fig = go.Figure(go.Scatter(
        x=df[x_col], y=df[y_col], mode="lines",
        line=dict(color=color, width=2.5),
        fill="tozeroy", fillcolor="rgba(57,230,122,0.12)",
    ))
    fig.update_layout(
        title={"text": title, "font": {"color": TEXT_PRIMARY, "family": "Space Grotesk", "size": 15}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER),
        height=320,
        margin=dict(l=10, r=20, t=40, b=20),
    )
    return fig
