from typing import Literal

ThemeMode = Literal["light", "dark"]

DARK_THEME = {
    "bg_color": "#0b1326",
    "text_color": "#dae2fd",
    "sub_color": "#bac9cc",
    "card_bg": "#1e293b",
    "card_border": "#3b494c",
    "tag_bg": "#1e293b",
    "tag_text": "#00e5ff",
    "assistance_bg": "#131b2e",
    "accent_primary": "#00e5ff",
    "accent_secondary": "#6366f1",
    "accent_tertiary": "#94a3b8",
    "accent_gold": "#fbbf24",
    "error": "#ffb4ab",
    "success": "#86efac",
    "surface_container": "#171f33",
    "surface_variant": "#2d3449",
    "outline_variant": "#3b494c",
    "on_surface_variant": "#bac9cc",
}

LIGHT_THEME = {
    "bg_color": "#f8fafc",
    "text_color": "#1e293b",
    "sub_color": "#64748b",
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "tag_bg": "#f1f5f9",
    "tag_text": "#00626e",
    "assistance_bg": "#f1f5f9",
    "accent_primary": "#00b4d8",
    "accent_secondary": "#4f46e5",
    "accent_tertiary": "#94a3b8",
    "accent_gold": "#f59e0b",
    "error": "#ef4444",
    "success": "#22c55e",
    "surface_container": "#f1f5f9",
    "surface_variant": "#e2e8f0",
    "outline_variant": "#cbd5e1",
    "on_surface_variant": "#64748b",
}

PREFIX_COLORS = {
    "Vesper": "#d8b4fe",
    "Atlas": "#7dd3fc",
    "Echo": "#fca5a5",
    "Sable": "#94a3b8",
    "Nova": "#fde047",
    "Zephyr": "#86efac",
}

CATEGORY_CONFIG = {
    "dance": {"border_color": "accent_secondary", "tag": "DANCE", "emoji": "💃"},
    "social": {"border_color": "accent_primary", "tag": "SOCIAL", "emoji": "💬"},
    "sensory": {"border_color": "accent_tertiary", "tag": "SENSORY", "emoji": "🎧"},
    "chaos": {"border_color": "accent_gold", "tag": "CHAOS", "emoji": "🪙"},
    "creative": {"border_color": "accent_gold", "tag": "CREATIVE", "emoji": "🎨"},
    "vocab": {"border_color": "accent_secondary", "tag": "VOCAB", "emoji": "🌐"},
    "mindfulness": {"border_color": "success", "tag": "MINDFULNESS", "emoji": "🧘"},
    "fitness": {"border_color": "error", "tag": "FITNESS", "emoji": "🏃"},
    "knowledge": {"border_color": "accent_secondary", "tag": "KNOWLEDGE", "emoji": "📚"},
}


def get_theme(mode: ThemeMode) -> dict:
    if mode == "dark":
        return DARK_THEME
    return LIGHT_THEME


def get_css(theme: dict) -> str:
    primary = theme["accent_primary"]
    secondary = theme["accent_secondary"]
    tertiary = theme["accent_tertiary"]
    gold = theme["accent_gold"]
    bg = theme["bg_color"]
    text = theme["text_color"]
    sub = theme["sub_color"]
    card = theme["card_bg"]
    border = theme["card_border"]
    tag_bg = theme["tag_bg"]
    tag_text = theme["tag_text"]
    assist_bg = theme["assistance_bg"]

    return f"""
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"], .stApp {{ 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    background-color: {bg} !important; 
    color: {text}; 
}}
.drx-title {{ 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    font-weight: 600; 
    font-size: 2.25rem; 
    color: {text}; 
    margin-bottom: 0; 
    letter-spacing: -0.02em;
}}
.drx-sub {{ 
    color: {sub}; 
    font-size: 1rem; 
    font-weight: 300;
    line-height: 1.6;
    margin-bottom: 2rem; 
}}
.drx-card {{ 
    background: {card}; 
    border: 1px solid {border}; 
    border-radius: 8px; 
    padding: 24px; 
    margin-bottom: 16px; 
    box-shadow: none;
    position: relative;
}}
.drx-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 8px 8px 0 0;
    background: {primary};
    opacity: 0;
}}
.drx-card-active::before {{
    opacity: 1;
}}
.drx-card-legendary::before {{
    background: {gold};
    opacity: 1;
}}
.drx-tag {{ 
    display: inline-block; 
    padding: 4px 12px; 
    border-radius: 4px; 
    font-size: 0.7rem; 
    font-weight: 700; 
    text-transform: uppercase; 
    letter-spacing: 0.1em;
    margin-bottom: 12px; 
    background: {tag_bg}; 
    color: {tag_text}; 
    border: 1px solid {border};
}}
.drx-quest-title {{ 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    font-weight: 600; 
    font-size: 1.5rem; 
    color: {text}; 
    margin-bottom: 12px;
    line-height: 1.3;
}}
.drx-quest-desc {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 300;
    font-size: 1rem;
    line-height: 1.7;
    color: {sub};
    margin-bottom: 0;
}}
.drx-assistance {{ 
    background-color: {assist_bg}; 
    padding: 16px; 
    border-left: 3px solid {sub}; 
    border-radius: 4px; 
    font-size: 0.9rem; 
    margin-top: 16px; 
    color: {text};
    font-weight: 300;
}}
.profile-banner {{ 
    background: linear-gradient(135deg, {primary}, {secondary}); 
    padding: 16px; 
    border-radius: 8px; 
    color: {bg}; 
    font-weight: 600; 
    margin-bottom: 4px; 
}}
.stButton > button {{
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
    border: 1px solid {primary} !important;
    transition: all 0.2s ease !important;
}}
.stButton > button[kind="primary"] {{
    background: {primary} !important;
    color: {bg} !important;
    border-color: {primary} !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {secondary} !important;
    border-color: {secondary} !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.3) !important;
}}
.stButton > button[kind="secondary"] {{
    background: transparent !important;
    color: {primary} !important;
    border-color: {primary} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: rgba(0, 229, 255, 0.1) !important;
}}
.stTextInput > div > div > input {{
    background: {theme["surface_container"]} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
    color: {text} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {primary} !important;
    box-shadow: 0 0 0 1px {primary} !important;
}}
.stRadio > div {{
    gap: 12px !important;
}}
.stRadio label {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 400 !important;
}}
[data-testid="stSidebar"] {{
    background: {theme["surface_container"]} !important;
    border-right: 1px solid {border} !important;
}}
[data-testid="stSidebar"] .stMarkdown {{
    color: {text} !important;
}}
.progress-bar {{
    height: 4px;
    background: {theme["surface_variant"]};
    border-radius: 2px;
    overflow: hidden;
}}
.progress-bar-fill {{
    height: 100%;
    background: {primary};
    border-radius: 2px;
    transition: width 0.5s ease-out;
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
}}
.step-indicator {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    background: {tag_bg};
    border: 1px solid {border};
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {tag_text};
}}
.quest-locked {{
    background: {card};
    border: 2px dashed {border};
    border-radius: 8px;
    padding: 48px;
    text-align: center;
}}
.quest-locked-icon {{
    font-size: 4rem;
    margin-bottom: 16px;
}}
.quest-locked-title {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 1.25rem;
    color: {text};
    margin-bottom: 8px;
}}
.quest-locked-subtitle {{
    color: {sub};
    font-weight: 300;
}}
.milestone-banner {{
    background: linear-gradient(135deg, {gold}, {primary});
    padding: 20px;
    border-radius: 8px;
    color: {bg};
    text-align: center;
    margin: 16px 0;
}}
.milestone-banner h3 {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 1.5rem;
    margin: 0 0 8px 0;
}}
.milestone-banner p {{
    font-weight: 300;
    margin: 0;
}}
.vocab-card {{
    background: {card};
    border: 1px solid {border};
    border-left: 4px solid #ff9800;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
}}
.vocab-word {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 1.75rem;
    color: {text};
    margin-bottom: 4px;
}}
.vocab-meta {{
    color: {sub};
    font-size: 0.9rem;
    margin-bottom: 16px;
}}
.vocab-meaning {{
    font-weight: 300;
    line-height: 1.7;
    color: {text};
}}
.flip-container {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.flip-choice {{
    flex: 1;
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    transition: border-color 0.2s;
}}
.flip-choice:hover {{
    border-color: {primary};
}}
.flip-choice-icon {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: {theme["surface_container"]};
    color: {primary};
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
    font-size: 1.25rem;
}}
.flip-choice-label {{
    font-weight: 400;
    font-size: 0.875rem;
    color: {text};
    text-align: center;
}}
.flip-button {{
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: {primary};
    color: {bg};
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.flip-button:hover {{
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
}}
.archive-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
}}
.archive-item {{
    background: {card};
    border: 1px solid {border};
    border-left: 4px solid {border};
    border-radius: 8px;
    padding: 16px;
    transition: background-color 0.2s;
}}
.archive-item:hover {{
    background: {theme["surface_variant"]};
}}
.archive-item-legendary {{
    border-left-color: {gold};
}}
.archive-item-icon {{
    font-size: 1.5rem;
    color: {tertiary};
    margin-bottom: 8px;
}}
.archive-item-title {{
    font-weight: 500;
    font-size: 0.875rem;
    color: {text};
    margin-bottom: 4px;
}}
.archive-item-date {{
    font-size: 0.75rem;
    color: {sub};
}}
"""


def inject_theme(mode: ThemeMode = "dark"):
    import streamlit as st
    theme = get_theme(mode)
    css = get_css(theme)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_progress(step: int, total: int = 4):
    import streamlit as st
    theme = get_theme(st.session_state.get("theme_mode", "dark"))
    pct = int((step / total) * 100)
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-bar-fill" style="width: {pct}%"></div>
    </div>
    <div class="step-indicator" style="margin-top: 8px;">Step {step} of {total}</div>
    """, unsafe_allow_html=True)