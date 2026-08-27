"""
style.py

Purely cosmetic. This file owns every bit of shared look-and-feel for the
app: global CSS, the color palette, and small reusable HTML components
(badges, KPI cards, section headers) that pages assemble with plain
Python — no model/business logic lives here, and nothing here reads or
changes any prediction, offer, or log data.
"""

import streamlit as st

# ------------------------------------------------------------------
# Palette — keep every page pulling from the same source so the app
# reads as one product instead of five separate scripts.
# ------------------------------------------------------------------
COLORS = {
    "primary": "#5B5FEF",
    "primary_dark": "#4145C7",
    "accent": "#00C2A8",
    "bg_card": "#FFFFFF",
    "bg_soft": "#F5F6FB",
    "border": "#E7E8F3",
    "text": "#1C1E29",
    "text_muted": "#6B6F86",
    "low": "#1FAE6E",
    "medium": "#F2A93B",
    "high": "#EF5B5B",
}

PLOTLY_SEQUENCE = ["#5B5FEF", "#00C2A8", "#F2A93B", "#EF5B5B", "#4145C7", "#8B8FF5"]


def inject_css():
    """Call once at the top of every page."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLORS['bg_soft']};
        }}
        h1, h2, h3 {{
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        [data-testid="stMetric"] {{
            background-color: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 14px;
            padding: 16px 18px 10px 18px;
            box-shadow: 0 1px 2px rgba(28,30,41,0.04);
        }}
        [data-testid="stMetricValue"] {{
            color: {COLORS['primary_dark']};
        }}
        div[data-testid="stForm"] {{
            background-color: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 24px 24px 8px 24px;
        }}
        .stButton > button, .stFormSubmitButton > button {{
            background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['primary_dark']});
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.55em 1.4em;
            font-weight: 600;
            transition: transform 0.05s ease-in-out;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            transform: translateY(-1px);
            opacity: 0.95;
        }}
        .hero {{
            background: linear-gradient(120deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
            border-radius: 20px;
            padding: 36px 40px;
            color: white;
            margin-bottom: 22px;
        }}
        .hero h1 {{
            color: white;
            margin-bottom: 6px;
        }}
        .hero p {{
            color: rgba(255,255,255,0.9);
            font-size: 1.05em;
            max-width: 720px;
        }}
        .nav-card {{
            background-color: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 18px 20px;
            height: 100%;
        }}
        .nav-card h4 {{
            margin: 0 0 4px 0;
        }}
        .nav-card p {{
            color: {COLORS['text_muted']};
            font-size: 0.92em;
            margin: 0;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .section-tag {{
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 2px;
        }}
        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str):
    st.markdown(
        f"""<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>""",
        unsafe_allow_html=True,
    )


def section_tag(text: str):
    st.markdown(f'<div class="section-tag">{text}</div>', unsafe_allow_html=True)


def risk_color(tier: str) -> str:
    return {
        "Low": COLORS["low"],
        "Medium": COLORS["medium"],
        "High": COLORS["high"],
    }.get(tier, COLORS["text_muted"])


def badge(text: str, color: str):
    st.markdown(
        f'<span class="badge" style="background-color:{color}22; color:{color};">{text}</span>',
        unsafe_allow_html=True,
    )


def nav_card(icon: str, title: str, description: str):
    st.markdown(
        f"""
        <div class="nav-card">
            <h4>{icon} {title}</h4>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
