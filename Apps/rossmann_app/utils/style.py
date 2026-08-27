"""
style.py

The entire visual system for the app, built from scratch in raw CSS/HTML —
no st.metric, no config.toml [theme], no default widget skins. Every
component here (cards, badges, hero, sidebar nav, buttons, inputs, charts)
is styled by hand.

Look: fixed dark theme (no light mode), neon-green glow accents, and a
green / yellow / red status palette carried through the main content —
metric icons, badges, and chart colors all draw from the same three-color
system used for risk tiers (Low=green, Medium=yellow, High=red).

The sidebar nav is restyled into raised, glowing 3D buttons (gradient
face, inset bevel, drop shadow, pressed state on click) instead of flat
links.

No logic lives here — this file only ever emits CSS/HTML strings.
"""

import streamlit as st

FA_CDN = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
FONT_CDN = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap"

# Fixed dark palette — no light-mode variant, no reliance on Streamlit's
# own theme tokens.
BG = "#0A0F0B"
SURFACE = "#121815"
SURFACE_RAISED = "#182019"
BORDER = "#243026"
TEXT = "#E8F3EA"
TEXT_MUTED = "#8CA394"

GREEN = "#2BFF88"        # glow primary
GREEN_SOFT = "#2ECC71"   # low / positive
YELLOW = "#FFD23B"       # medium / caution
RED = "#FF4757"          # high / negative

COLORS = {
    "primary": GREEN,
    "primary_dark": "#16C86A",
    "accent": YELLOW,
    "low": GREEN_SOFT,
    "medium": YELLOW,
    "high": RED,
    "muted": TEXT_MUTED,
}

PLOTLY_SEQUENCE = [GREEN_SOFT, YELLOW, RED, GREEN, "#7CFFB2", "#FFB347"]

ICONS = {
    "home": "fa-house",
    "single": "fa-bullseye",
    "batch": "fa-table-list",
    "performance": "fa-chart-line",
    "advance": "fa-sack-dollar",
    "risk": "fa-shield-halved",
    "check": "fa-circle-check",
    "warn": "fa-triangle-exclamation",
    "flask": "fa-flask",
    "bolt": "fa-bolt",
    "store": "fa-store",
    "calendar": "fa-calendar-days",
    "layers": "fa-layer-group",
    "download": "fa-download",
    "trend-up": "fa-arrow-trend-up",
    "gauge": "fa-gauge-high",
    "coins": "fa-coins",
    "percent": "fa-percent",
}


def inject_css():
    """Call once, first thing, on every page."""
    st.markdown(f'<link rel="stylesheet" href="{FA_CDN}">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <style>
        @import url('{FONT_CDN}');

        :root {{
            --bg: {BG};
            --surface: {SURFACE};
            --surface-raised: {SURFACE_RAISED};
            --text: {TEXT};
            --text-muted: {TEXT_MUTED};
            --border: {BORDER};
            --primary: {COLORS['primary']};
            --primary-dark: {COLORS['primary_dark']};
            --accent: {COLORS['accent']};
            --low: {COLORS['low']};
            --medium: {COLORS['medium']};
            --high: {COLORS['high']};
            --glow: 0 0 14px rgba(43,255,136,0.45), 0 0 34px rgba(43,255,136,0.16);
            --glow-strong: 0 0 20px rgba(43,255,136,0.7), 0 0 46px rgba(43,255,136,0.28);
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.5);
            --shadow-md: 0 8px 24px rgba(0,0,0,0.55);
            --radius: 16px;
        }}

        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}

        html, body, .stApp {{
            background:
                radial-gradient(ellipse 900px 500px at 15% -10%, rgba(43,255,136,0.07), transparent 60%),
                var(--bg) !important;
            color: var(--text) !important;
            color-scheme: dark;
        }}

        /* ---- strip default chrome / whitespace ---- */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 2.2rem;
        }}
        #MainMenu, footer {{ visibility: hidden; height: 0; }}
        .block-container {{
            padding-top: 1.1rem !important;
            padding-bottom: 2rem !important;
            max-width: 1180px;
        }}
        div[data-testid="stVerticalBlock"] {{ gap: 0.55rem; }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{ gap: 0; }}
        hr {{ margin: 0.6rem 0; border-color: var(--border); }}

        /* ---- headings ---- */
        h1, h2, h3, h4, h5 {{
            color: var(--text) !important;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}
        p, span, label, .stMarkdown, .stCaption {{ color: var(--text) !important; }}
        .stCaption, [data-testid="stCaptionContainer"] {{ color: var(--text-muted) !important; }}

        /* ---- sidebar: dark, glowing, 3D buttons ---- */
        [data-testid="stSidebar"] {{
            background:
                radial-gradient(ellipse 500px 300px at 50% 0%, rgba(43,255,136,0.10), transparent 65%),
                linear-gradient(180deg, #0D1310 0%, #090C0A 100%) !important;
            border-right: 1px solid rgba(43,255,136,0.18);
        }}
        [data-testid="stSidebar"] * {{ color: var(--text) !important; }}
        [data-testid="stSidebarContent"] {{ padding-top: 0.5rem; }}

        [data-testid="stSidebarNav"] {{ padding: 0.6rem 0.7rem; }}
        [data-testid="stSidebarNav"] ul {{ padding: 0; }}
        [data-testid="stSidebarNav"] li {{
            margin-bottom: 10px;
            list-style: none;
        }}
        [data-testid="stSidebarNav"] a {{
            display: block;
            border-radius: 12px;
            padding: 0.75rem 1rem 0.75rem 2.7rem !important;
            position: relative;
            font-weight: 700;
            font-size: 0.92rem;
            color: var(--text-muted) !important;
            background: linear-gradient(180deg, #1B241C 0%, #10150F 100%);
            border: 1px solid rgba(43,255,136,0.16);
            border-top-color: rgba(255,255,255,0.06);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.05),
                inset 0 -3px 6px rgba(0,0,0,0.55),
                0 3px 8px rgba(0,0,0,0.5);
            transition: transform 0.1s ease, box-shadow 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }}
        [data-testid="stSidebarNav"] a:hover {{
            color: var(--primary) !important;
            border-color: rgba(43,255,136,0.55);
            transform: translateY(-2px);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                inset 0 -3px 6px rgba(0,0,0,0.55),
                var(--glow),
                0 6px 14px rgba(0,0,0,0.55);
        }}
        [data-testid="stSidebarNav"] a:active {{
            transform: translateY(1px);
            box-shadow:
                inset 0 3px 8px rgba(0,0,0,0.7),
                0 0 8px rgba(43,255,136,0.3);
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            color: #06120A !important;
            background: linear-gradient(180deg, #4CFFA0 0%, #1FCB6E 100%);
            border-color: rgba(43,255,136,0.9);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.35),
                inset 0 -3px 6px rgba(0,0,0,0.25),
                var(--glow-strong);
            font-weight: 800;
        }}
        [data-testid="stSidebarNav"] a span {{ display: none !important; }}
        [data-testid="stSidebarNav"] a::before {{
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            position: absolute;
            left: 1.05rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.95rem;
        }}
        [data-testid="stSidebarNav"] li:nth-child(1) a::before {{ content: "\\f015"; }}
        [data-testid="stSidebarNav"] li:nth-child(2) a::before {{ content: "\\f140"; }}
        [data-testid="stSidebarNav"] li:nth-child(3) a::before {{ content: "\\f0ce"; }}
        [data-testid="stSidebarNav"] li:nth-child(4) a::before {{ content: "\\f201"; }}
        [data-testid="stSidebarNav"] li:nth-child(5) a::before {{ content: "\\f81d"; }}
        [data-testid="stSidebarNav"] li:nth-child(6) a::before {{ content: "\\f3ed"; }}

        /* ---- inputs ---- */
        .stTextInput input, .stNumberInput input, .stDateInput input,
        [data-baseweb="select"] > div, [data-baseweb="base-input"] {{
            background: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
        }}
        [data-baseweb="popover"] * {{
            background: var(--surface-raised) !important;
            color: var(--text) !important;
        }}
        .stSlider [data-baseweb="slider"] div {{ background: var(--primary); }}

        /* ---- form container ---- */
        div[data-testid="stForm"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 22px 22px 6px 22px;
            box-shadow: var(--shadow-sm);
        }}

        /* ---- buttons ---- */
        .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
            background: linear-gradient(180deg, #3CFF95 0%, #16C86A 100%);
            color: #06120A !important;
            border: 1px solid rgba(43,255,136,0.6);
            border-radius: 10px;
            padding: 0.6em 1.5em;
            font-weight: 800;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.4), 0 3px 10px rgba(0,0,0,0.4);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.4), var(--glow), 0 6px 14px rgba(0,0,0,0.45);
        }}
        .stButton > button:active, .stFormSubmitButton > button:active {{ transform: translateY(1px); }}

        /* ---- expander ---- */
        [data-testid="stExpander"] {{
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            background: var(--surface) !important;
            overflow: hidden;
        }}

        /* ---- alerts ---- */
        [data-testid="stAlert"] {{
            border-radius: 12px !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            animation: fadeInUp 0.35s ease both;
        }}

        /* ---- dataframe ---- */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        /* ---- file uploader ---- */
        [data-testid="stFileUploaderDropzone"] {{
            background: var(--surface) !important;
            border: 1.5px dashed var(--border) !important;
            border-radius: 12px !important;
        }}

        /* ---- progress bar ---- */
        .stProgress div[role="progressbar"] > div {{
            background: linear-gradient(90deg, var(--low), var(--medium), var(--high)) !important;
            box-shadow: var(--glow);
        }}

        /* ================= custom components ================= */

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: var(--glow); }}
            50% {{ box-shadow: var(--glow-strong); }}
        }}
        .fade-in {{ animation: fadeInUp 0.45s cubic-bezier(.2,.8,.2,1) both; }}

        .hero {{
            background: linear-gradient(135deg, #0F1E14 0%, #0A130D 100%);
            border: 1px solid rgba(43,255,136,0.35);
            border-radius: 20px;
            padding: 34px 38px;
            color: var(--text);
            margin-bottom: 18px;
            box-shadow: var(--glow), var(--shadow-md);
            animation: fadeInUp 0.5s cubic-bezier(.2,.8,.2,1) both;
        }}
        .hero .hero-icon {{
            font-size: 1.5rem;
            width: 52px; height: 52px;
            border-radius: 14px;
            background: rgba(43,255,136,0.12);
            border: 1px solid rgba(43,255,136,0.4);
            color: var(--primary);
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 14px;
            text-shadow: 0 0 12px rgba(43,255,136,0.8);
        }}
        .hero h1 {{ color: var(--text) !important; margin: 0 0 8px 0; font-size: 1.7rem; }}
        .hero p {{ color: var(--text-muted) !important; font-size: 1.0rem; max-width: 760px; margin: 0; }}

        .section-tag {{
            color: var(--primary);
            text-transform: uppercase;
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            margin: 14px 0 6px 0;
            display: flex; align-items: center; gap: 6px;
            text-shadow: 0 0 8px rgba(43,255,136,0.4);
        }}

        .metric-card {{
            background: linear-gradient(180deg, var(--surface-raised) 0%, var(--surface) 100%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: var(--shadow-sm);
            transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
            height: 100%;
        }}
        .metric-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent-color, var(--primary));
            box-shadow: 0 0 16px color-mix(in srgb, var(--accent-color, var(--primary)) 45%, transparent), var(--shadow-md);
        }}
        .metric-icon {{
            width: 34px; height: 34px;
            border-radius: 9px;
            background: color-mix(in srgb, var(--accent-color, var(--primary)) 16%, transparent);
            color: var(--accent-color, var(--primary));
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 10px;
            font-size: 0.95rem;
            text-shadow: 0 0 10px color-mix(in srgb, var(--accent-color, var(--primary)) 70%, transparent);
        }}
        .metric-label {{
            font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.06em;
            color: var(--text-muted); font-weight: 700;
        }}
        .metric-value {{
            font-size: 1.5rem; font-weight: 800; color: var(--text);
            margin-top: 2px; line-height: 1.2;
        }}
        .metric-sub {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }}

        .badge-pill {{
            display: inline-flex; align-items: center; gap: 6px;
            padding: 5px 14px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 800;
            border: 1px solid currentColor;
            animation: fadeInUp 0.35s ease both;
        }}

        .nav-card {{
            background: linear-gradient(180deg, var(--surface-raised) 0%, var(--surface) 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 18px 20px;
            height: 100%;
            transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
        }}
        .nav-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--glow), var(--shadow-md);
            border-color: var(--primary);
        }}
        .nav-card .nav-icon {{
            width: 38px; height: 38px;
            border-radius: 10px;
            background: rgba(43,255,136,0.12);
            color: var(--primary);
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 10px;
            font-size: 1rem;
            text-shadow: 0 0 10px rgba(43,255,136,0.6);
        }}
        .nav-card h4 {{ margin: 0 0 4px 0; font-size: 1.02rem; color: var(--text) !important; }}
        .nav-card p {{ color: var(--text-muted) !important; font-size: 0.86rem; margin: 0; line-height: 1.4; }}

        .app-footer {{
            color: var(--text-muted);
            font-size: 0.82rem;
            text-align: center;
            padding: 14px 0 4px 0;
        }}
        .app-footer a {{ color: var(--primary); text-decoration: none; font-weight: 700; text-shadow: 0 0 6px rgba(43,255,136,0.5); }}

        /* responsiveness */
        @media (max-width: 768px) {{
            .hero {{ padding: 24px 22px; }}
            .hero h1 {{ font-size: 1.32rem; }}
            .metric-value {{ font-size: 1.2rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _icon(name: str) -> str:
    return ICONS.get(name, "fa-circle")


def hero(icon: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-icon"><i class="fa-solid {_icon(icon)}"></i></div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_tag(text: str, icon: str = None):
    icon_html = f'<i class="fa-solid {_icon(icon)}"></i>' if icon else ""
    st.markdown(f'<div class="section-tag">{icon_html}{text}</div>', unsafe_allow_html=True)


def metric_card(icon: str, label: str, value: str, sub: str = None, color: str = None):
    accent = f'style="--accent-color:{color}"' if color else ""
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="metric-card fade-in">
            <div class="metric-icon" {accent}><i class="fa-solid {_icon(icon)}"></i></div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_color(tier: str) -> str:
    return {
        "Low": COLORS["low"],
        "Medium": COLORS["medium"],
        "High": COLORS["high"],
    }.get(tier, COLORS["muted"])


def badge(text: str, color: str, icon: str = None):
    icon_html = f'<i class="fa-solid {_icon(icon)}"></i>' if icon else ""
    st.markdown(
        f'<span class="badge-pill" style="background:{color}22; color:{color}; box-shadow:0 0 10px {color}55;">{icon_html}{text}</span>',
        unsafe_allow_html=True,
    )


def nav_card(icon: str, title: str, description: str):
    st.markdown(
        f"""
        <div class="nav-card fade-in">
            <div class="nav-icon"><i class="fa-solid {_icon(icon)}"></i></div>
            <h4>{title}</h4>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer(text_html: str):
    st.markdown(f'<div class="app-footer">{text_html}</div>', unsafe_allow_html=True)


def style_chart(fig, height=320):
    """Transparent background + palette drawn from the green/yellow/red
    status system, so charts read as part of the same dark, glowing UI."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED, family="Inter, sans-serif"),
        colorway=PLOTLY_SEQUENCE,
        transition=dict(duration=400, easing="cubic-in-out"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED)),
    )
    fig.update_xaxes(gridcolor="rgba(140,163,148,0.15)", zerolinecolor="rgba(140,163,148,0.15)", color=TEXT_MUTED)
    fig.update_yaxes(gridcolor="rgba(140,163,148,0.15)", zerolinecolor="rgba(140,163,148,0.15)", color=TEXT_MUTED)
    return fig


def plotly_chart(fig, height=320):
    """Drop-in for st.plotly_chart: applies our styling, disables Streamlit's
    own auto-theme override (theme=None), and keeps it responsive."""
    style_chart(fig, height=height)
    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None,
        config={"responsive": True, "displaylogo": False, "displayModeBar": "hover"},
    )
