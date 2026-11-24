"""Shared look-and-feel for every Streamlit app in this portfolio.

Evergreen / Slate theme — dark, neon-accented, portfolio-grade styling
used by the Gym Member Segmentation project.

Public API:
    PALETTE            colour tokens (single source of truth for the whole app)
    CLUSTER_COLORS     neon categorical palette for cluster traces
    CRISP_DM_PHASES    the six CRISP-DM tabs, in order
    REPO_URL           link rendered in the footer
    apply()            page config + global CSS injection
    hero()             title block with badge chips
    style_fig()        apply the galaxy look to any Plotly figure (in place)
    section()          styled section heading with a neon underline
    insight()          call-out box for auto-generated findings
    persona_card()     HTML card used to render a discovered persona
    footer()           minimal portfolio footer
"""

import streamlit as st

# --- 🎨 Evergreen palette -------------------------------------------------
PALETTE = {
    "bg": "#0B1220",         # deep space (near-black blue)
    "panel": "#141F30",      # data panels (dark navy)
    "panel_alt": "#0F1929",  # sidebar / inset surfaces (darker)
    "border": "#304158",     # separators
    "text": "#F1F5F9",       # primary text (blue-white)
    "muted": "#ACBBD0",      # secondary text / captions
    "accent": "#5EE0B5",     # neon cyan (hot stars)
    "accent2": "#8AB4F8",    # galactic purple (nebula)
    "good": "#72D5AD",       # neon green
    "warn": "#F1C777",       # gold
    "bad": "#F38BA0",        # neon red
}

# Neon categorical palette — one colour per cluster, matching the theme.
CLUSTER_COLORS = [
    "#5EE0B5",  # cyan
    "#8AB4F8",  # purple
    "#72D5AD",  # green
    "#F1C777",  # gold
    "#F38BA0",  # red-pink
    "#E8A87C",  # orange
    "#A49BE8",  # blue
    "#DBA6CF",  # magenta
    "#B8D99A",  # lime
    "#78CED6",  # sky
]

CRISP_DM_PHASES = [
    ("1. Business Understanding", "🎯"),
    ("2. Data Understanding", "🔎"),
    ("3. Data Preparation", "🧹"),
    ("4. Modeling", "🧠"),
    ("5. Evaluation", "📏"),
    ("6. Deployment", "🚀"),
]

REPO_URL = "https://github.com/fotroslab/Gym-Member-Segmentation"


def apply(icon: str, title: str, layout: str = "wide") -> None:
    """Set page config and inject the global galaxy CSS."""
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )

    st.markdown(
        f"""
        <style>
        /* --- Hide Streamlit chrome --- */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
        div[data-testid="stToolbar"] {{ visibility: hidden; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        div[data-testid="stStatusWidget"] {{ visibility: hidden; }}

        /* --- Base --- */
        .stApp {{
            background: {PALETTE['bg']};
            color: {PALETTE['text']};
        }}
        section[data-testid="stSidebar"] {{
            background: {PALETTE['panel_alt']};
            border-right: 1px solid {PALETTE['border']};
        }}
        h1, h2, h3, h4 {{ color: {PALETTE['text']} !important; font-weight: 700 !important; }}
        p, li, span, label {{ color: {PALETTE['text']}; }}
        .stCaption, .stCaption p {{ color: {PALETTE['muted']} !important; }}
        hr {{ border-color: {PALETTE['border']}; }}

        /* --- Hero (galaxy glow) --- */
        .ds-hero {{
            background: radial-gradient(circle at top right, #173C3C 0%, {PALETTE['panel']} 100%);
            border: 1px solid {PALETTE['border']};
            border-radius: 14px;
            padding: 1.6rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
        }}
        .ds-hero h1 {{ margin: 0 0 .5rem 0; font-size: 2rem; color: {PALETTE['accent']} !important; }}
        .ds-hero p {{ color: {PALETTE['muted']}; margin: 0; font-size: 1rem; }}
        .ds-badgebar {{ display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; }}
        .ds-badge {{
            background: rgba(94, 224, 181, 0.1);
            border: 1px solid {PALETTE['accent']};
            color: {PALETTE['accent']};
            border-radius: 999px;
            padding: .3rem .8rem;
            font-size: .8rem;
            white-space: nowrap;
            box-shadow: none;
        }}

        /* --- Section headings --- */
        .ds-section {{
            margin: 1.8rem 0 .8rem 0;
            padding-bottom: .4rem;
            border-bottom: 2px solid {PALETTE['accent2']};
            font-size: 1.25rem;
            font-weight: 700;
            color: {PALETTE['text']};
        }}
        .ds-section span {{ color: {PALETTE['accent']}; margin-right: .5rem; }}

        /* --- Metric cards --- */
        .ds-card {{
            background: {PALETTE['panel']};
            border: 1px solid {PALETTE['border']};
            border-radius: 12px;
            padding: 1rem 1.2rem;
            height: 100%;
            transition: border-color .3s ease, box-shadow .3s ease;
        }}
        .ds-card:hover {{
            border-color: {PALETTE['accent2']};
            box-shadow: 0 0 15px rgba(138, 180, 248, 0.15);
        }}
        .ds-metric-label {{
            color: {PALETTE['muted']};
            font-size: .8rem;
            text-transform: uppercase;
            letter-spacing: .05em;
        }}
        .ds-metric-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: {PALETTE['accent']};
            margin-top: .2rem;
        }}
        .ds-metric-sub {{ color: {PALETTE['muted']}; font-size: .8rem; margin-top: .2rem; }}

        /* --- Insight call-out --- */
        .ds-insight {{
            background: linear-gradient(90deg, rgba(94,224,181,.08), rgba(138,180,248,.06));
            border-left: 3px solid {PALETTE['accent']};
            border-radius: 0 10px 10px 0;
            padding: .8rem 1rem;
            margin: .6rem 0;
            color: {PALETTE['text']};
            font-size: .95rem;
        }}
        .ds-insight b {{ color: {PALETTE['accent']}; }}

        /* --- Persona cards --- */
        .ds-persona {{
            background: {PALETTE['panel']};
            border: 1px solid {PALETTE['border']};
            border-left: 4px solid var(--pc, {PALETTE['accent']});
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: .8rem;
        }}
        .ds-persona h4 {{ margin: 0 0 .3rem 0; color: var(--pc, {PALETTE['accent']}) !important; }}
        .ds-persona .ds-persona-meta {{
            color: {PALETTE['muted']}; font-size: .82rem; margin-bottom: .5rem;
        }}
        .ds-persona p {{ margin: 0; font-size: .92rem; color: {PALETTE['text']}; }}

        /* --- Native Streamlit widgets --- */
        div[data-testid="stMetric"] {{
            background: {PALETTE['panel']};
            border: 1px solid {PALETTE['border']};
            border-radius: 10px;
            padding: .8rem 1rem;
        }}
        div[data-testid="stMetric"]:hover {{ border-color: {PALETTE['accent']}; }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            border-bottom: 1px solid {PALETTE['border']};
        }}
        .stTabs [data-baseweb="tab"] {{
            background: {PALETTE['panel']};
            border-radius: 8px 8px 0 0;
            padding: .6rem 1.2rem;
            color: {PALETTE['muted']};
        }}
        .stTabs [aria-selected="true"] {{
            background: {PALETTE['panel_alt']};
            color: {PALETTE['accent']} !important;
            border-bottom: 2px solid {PALETTE['accent']};
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {PALETTE['border']};
            border-radius: 10px;
        }}
        code {{ color: {PALETTE['accent2']}; background: {PALETTE['panel_alt']}; }}

        .stButton button[kind="primary"], .stDownloadButton button[kind="primary"] {{
            background: {PALETTE['accent']}; color: #0B1220; border: none;
        }}
        .stButton button[kind="primary"] p, .stDownloadButton button[kind="primary"] p {{ color: #0B1220 !important; }}
        a {{ color: {PALETTE['accent2']}; }}
        button:focus-visible, a:focus-visible {{ outline: 3px solid {PALETTE['accent2']}; outline-offset: 3px; }}
        /* --- Footer --- */
        .ds-footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid {PALETTE['border']};
            color: {PALETTE['muted']};
            font-size: .85rem;
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(icon: str, title: str, subtitle: str, phase_labels=None) -> None:
    """Render the hero block with badge chips."""
    badges = "".join(f'<span class="ds-badge">{p}</span>' for p in (phase_labels or []))
    st.markdown(
        f"""
        <div class="ds-hero">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
            <div class="ds-badgebar">{badges}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(icon: str, title: str) -> None:
    """Styled section heading with a neon underline."""
    st.markdown(f'<div class="ds-section"><span>{icon}</span>{title}</div>', unsafe_allow_html=True)


def insight(html: str) -> None:
    """Render an auto-generated finding / call-out box."""
    st.markdown(f'<div class="ds-insight">{html}</div>', unsafe_allow_html=True)


def persona_card(name: str, meta: str, body: str, color: str) -> None:
    """Render one discovered persona as a coloured card."""
    st.markdown(
        f"""
        <div class="ds-persona" style="--pc: {color};">
            <h4>{name}</h4>
            <div class="ds-persona-meta">{meta}</div>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_fig(fig, height: int = 360):
    """Apply the galaxy theme to a Plotly figure in place and return it."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["panel"],
        font_color=PALETTE["text"],
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=PALETTE["panel_alt"], bordercolor=PALETTE["border"]),
    )
    fig.update_xaxes(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"])
    fig.update_yaxes(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"])
    return fig


def footer(project_name: str, author_name: str = "Your Name") -> None:
    """Minimal portfolio footer."""
    st.markdown(
        f"""
        <div class="ds-footer">
        Created by <b>{author_name}</b>  •
        <b>{project_name}</b>  •
        Check out my portfolio on
        <a href="{REPO_URL}" target="_blank"
           style="color: {PALETTE['accent']}; text-decoration: none; font-weight: bold;">
            GitHub
        </a>.
        </div>
        """,
        unsafe_allow_html=True,
    )
