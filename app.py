import streamlit as st
import time
from datetime import date
from core.db import init_db, get_session
from core.models import User, DailySession, Quest, Preference
from core.auth import (
    create_user, authenticate_user, get_user_preferences, update_user_preferences,
    update_user_spice_level, update_user_theme, username_exists
)
from core.quests import (
    select_quest_for_user, get_vibe_check_questions, compute_vibe_weights,
    suggest_spice_level, get_spice_levels, can_reroll, increment_reroll,
    complete_quest, get_reroll_cap
)
from core.vocab import (
    get_unquizzed_vocab_seen, build_recall_quiz, record_quiz_attempt,
    mark_vocab_quizzed, get_new_vocab_for_user, log_vocab_seen
)
from core.streaks import calculate_streak, get_streak_milestone, get_milestone_message
from core.theme import inject_theme, render_progress
from core.seed_data import run_seed
from sqlalchemy import select


st.set_page_config(
    page_title="DayRise Adventures",
    page_icon="💫",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_app():
    init_db()
    run_seed()


def get_or_create_daily_session(user_id: int) -> DailySession:
    today = date.today()
    with get_session() as session:
        ds = session.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today
            )
        ).scalar_one_or_none()
        if not ds:
            ds = DailySession(user_id=user_id, session_date=today)
            session.add(ds)
            session.flush()
            session.refresh(ds)
        session.expunge(ds)
        return ds


def reset_daily_session(user_id: int):
    today = date.today()
    with get_session() as session:
        ds = session.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today
            )
        ).scalar_one_or_none()
        if ds:
            session.delete(ds)


def login_page():
    inject_theme("dark")
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔮</div>
        <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 600; font-size: 2.5rem; margin-bottom: 0.5rem;">DayRise Adventures</h1>
        <p style="color: #bac9cc; font-weight: 300; font-size: 1.1rem;">Your daily quest awaits.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Log In", "✨ Create Adventurer"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Adventurer Name", placeholder="e.g. Hero_123").strip()
            pin = st.text_input("Secret Rune (4-Digit)", type="password", max_chars=4, placeholder="****")
            submitted = st.form_submit_button("Enter the Realm →", use_container_width=True, type="primary")
            if submitted:
                if not username or not pin:
                    st.error("Please enter both your name and PIN.")
                elif len(pin) != 4 or not pin.isdigit():
                    st.error("PIN must be 4 digits.")
                else:
                    auth_result = authenticate_user(username, pin)
                    if auth_result:
                        user_id, username, adventurer_name, theme_mode = auth_result
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.session_state.adventurer_name = adventurer_name
                        st.session_state.theme_mode = theme_mode
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Check your name and PIN.")

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Choose Adventurer Name", placeholder="e.g. Hero_123").strip()
            new_pin = st.text_input("Create Secret Rune (4-Digit)", type="password", max_chars=4, placeholder="****")
            confirm_pin = st.text_input("Confirm Secret Rune", type="password", max_chars=4, placeholder="****")
            submitted = st.form_submit_button("Begin Journey →", use_container_width=True, type="primary")
            if submitted:
                if not new_username or not new_pin or not confirm_pin:
                    st.error("Please fill in all fields.")
                elif len(new_pin) != 4 or not new_pin.isdigit():
                    st.error("PIN must be 4 digits.")
                elif new_pin != confirm_pin:
                    st.error("PINs do not match.")
                elif username_exists(new_username):
                    st.error("That adventurer name is already taken.")
                else:
                    user_id, adventurer_name = create_user(new_username, new_pin)
                    st.success(f"Adventurer created! Your code name: **{adventurer_name}**")
                    st.info("You can now log in with your name and PIN.")
                    time.sleep(1)
                    st.rerun()


def sidebar_user_panel():
    with st.sidebar:
        st.markdown(f"""
        <div class="profile-banner">
            🚀 {st.session_state.adventurer_name}
        </div>
        """, unsafe_allow_html=True)

        with get_session() as session:
            user = session.get(User, st.session_state.user_id)
            if user:
                streak = calculate_streak(user.id)
                st.caption(f"🔥 Current Streak: **{streak}** days")

        theme_options = {"Light Mode ☀️": "light", "Dark Mode 🌙": "dark"}
        current_theme = st.session_state.get("theme_mode", "dark")
        theme_label = [k for k, v in theme_options.items() if v == current_theme][0]
        new_theme_label = st.radio("Theme", list(theme_options.keys()), index=list(theme_options.keys()).index(theme_label))
        new_theme = theme_options[new_theme_label]
        if new_theme != current_theme:
            update_user_theme(st.session_state.user_id, new_theme)
            st.session_state.theme_mode = new_theme
            st.rerun()

        st.markdown("---")
        st.subheader("🎨 Preference Matrix")

        prefs = get_user_preferences(st.session_state.user_id)
        p1_this = st.text_input("Dilemma 1 — This", value=prefs[0][0] if prefs else "Go Out 🏃‍♂️", key="p1_this")
        p1_that = st.text_input("Dilemma 1 — That", value=prefs[0][1] if prefs else "Stay In 🏠", key="p1_that")
        p2_this = st.text_input("Dilemma 2 — This", value=prefs[1][0] if len(prefs) > 1 else "Run Quick ⚡", key="p2_this")
        p2_that = st.text_input("Dilemma 2 — That", value=prefs[1][1] if len(prefs) > 1 else "Walk Slow 🚶‍♂️", key="p2_that")

        if st.button("Save Preferences", use_container_width=True):
            update_user_preferences(st.session_state.user_id, [(p1_this, p1_that), (p2_this, p2_that)])
            st.toast("Preferences saved!")

        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_vibe_check(ds: DailySession):
    render_progress(1)
    st.markdown('<h1 class="drx-title">💫 Vibe Check</h1>', unsafe_allow_html=True)
    st.markdown('<p class="drx-sub">Three quick taps to calibrate today\'s quest.</p>', unsafe_allow_html=True)

    questions = get_vibe_check_questions()
    answers = {}

    for i, q in enumerate(questions):
        st.markdown(f"### {q['question']}")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(q["option_a"], key=f"vibe_{q['key']}_a", use_container_width=True, type="secondary"):
                answers[q["key"]] = "a"
        with col_b:
            if st.button(q["option_b"], key=f"vibe_{q['key']}_b", use_container_width=True, type="secondary"):
                answers[q["key"]] = "b"

        if q["key"] in answers:
            st.session_state[f"vibe_{q['key']}"] = answers[q["key"]]

    all_answered = all(f"vibe_{q['key']}" in st.session_state for q in questions)

    if all_answered:
        vibe_answers = {q["key"]: st.session_state[f"vibe_{q['key']}"] for q in questions}
        weights = compute_vibe_weights(vibe_answers)
        suggested_spice = suggest_spice_level(vibe_answers)

        ds.vibe_check_done = True
        ds.spice_level_selected = suggested_spice

        with get_session() as session:
            session.merge(ds)

        st.session_state.vibe_weights = weights
        st.session_state.suggested_spice = suggested_spice
        st.session_state.vibe_answers = vibe_answers
        st.rerun()


def render_vocab_recall(ds: DailySession):
    render_progress(2)
    st.markdown('<h1 class="drx-title">📜 Memory Forge</h1>', unsafe_allow_html=True)

    unquizzed = get_unquizzed_vocab_seen(st.session_state.user_id)

    if unquizzed and not st.session_state.get("vocab_quiz_done"):
        quiz = build_recall_quiz(unquizzed)
        if quiz:
            st.markdown(f'<p class="drx-sub">Recall yesterday\'s knowledge.</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="drx-card">
                <span class="drx-tag">{quiz['language']}</span>
                <div class="drx-quest-title">{quiz['flag']} {quiz['word']}</div>
                <p style="color: #bac9cc; font-style: italic; margin-bottom: 1.5rem;">({quiz['pronunciation']})</p>
                <p style="font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; color: #bac9cc; margin-bottom: 1rem;">What does it mean?</p>
            </div>
            """, unsafe_allow_html=True)

            for idx, option in enumerate(quiz["options"]):
                if st.button(option, key=f"vocab_opt_{idx}", use_container_width=True):
                    is_correct = option == quiz["correct_meaning"]
                    record_quiz_attempt(st.session_state.user_id, "vocab_recall", quiz["word"], is_correct)
                    mark_vocab_quizzed(quiz["vocab_seen_id"])
                    st.session_state.vocab_quiz_result = {"correct": is_correct, "answer": quiz["correct_meaning"]}
                    st.session_state.vocab_quiz_done = True
                    st.rerun()

            if st.session_state.get("vocab_quiz_done"):
                result = st.session_state.vocab_quiz_result
                if result["correct"]:
                    st.success("✨ Correct! The memory holds.")
                else:
                    st.error(f"❌ Not quite. It means: *{result['answer']}*")
                if st.button("Continue →", type="primary", use_container_width=True):
                    st.session_state.vocab_quiz_done = False
                    ds.vocab_recall_done = True
                    with get_session() as session:
                        session.merge(ds)
                    st.rerun()
        else:
            ds.vocab_recall_done = True
            with get_session() as session:
                session.merge(ds)
            st.rerun()
    else:
        new_vocab = get_new_vocab_for_user(st.session_state.user_id)
        if new_vocab:
            log_vocab_seen(st.session_state.user_id, new_vocab.id)
            st.markdown(f'<p class="drx-sub">Today\'s new discovery.</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="drx-card" style="border-left: 4px solid #ff9800;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <span class="drx-tag">NEW DISCOVERY</span>
                    <span style="font-size: 2rem;">{new_vocab.flag}</span>
                </div>
                <div class="drx-quest-title" style="color: #ff9800;">{new_vocab.word}</div>
                <p style="color: #bac9cc; font-style: italic; margin-bottom: 1rem;">[{new_vocab.pronunciation}]</p>
                <p class="drx-quest-desc"><strong>Meaning:</strong> {new_vocab.meaning}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Continue to Quest →", type="primary", use_container_width=True):
                ds.vocab_recall_done = True
                with get_session() as session:
                    session.merge(ds)
                st.rerun()
        else:
            ds.vocab_recall_done = True
            with get_session() as session:
                session.merge(ds)
            st.rerun()


def render_quest_reveal(ds: DailySession):
    render_progress(3)
    st.markdown('<h1 class="drx-title">🎲 Quest Reveal</h1>', unsafe_allow_html=True)

    if not ds.quest_id:
        vibe_weights = st.session_state.get("vibe_weights")
        spice = ds.spice_level_selected
        quest = select_quest_for_user(st.session_state.user_id, spice, vibe_weights)
        if quest:
            ds.quest_id = quest.id
            with get_session() as session:
                session.merge(ds)
            st.session_state.quest_reveal_anim = True
            st.rerun()
        else:
            st.error("No quests available. Please contact admin.")
            return

    with get_session() as session:
        quest = session.get(Quest, ds.quest_id)
        if quest:
            # Eagerly load attributes before leaving session to avoid DetachedInstanceError
            _ = quest.id, quest.title, quest.category, quest.rarity, quest.spice_level, quest.emoji, quest.desc, quest.assistance_text
            session.expunge(quest)

    if not quest:
        st.error("Quest not found.")
        return

    if st.session_state.get("quest_reveal_anim"):
        st.markdown("""
        <div class="quest-locked">
            <div class="quest-locked-icon">🎲</div>
            <div class="quest-locked-title">Unlocking Today's Quest...</div>
            <div class="quest-locked-subtitle">Calibrating challenge parameters...</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.quest_reveal_anim = False
        st.rerun()

    rarity_class = "drx-card-legendary" if quest.rarity == "legendary" else "drx-card-active"
    cat_config = {
        "dance": {"border": "accent_secondary", "tag": "DANCE"},
        "social": {"border": "accent_primary", "tag": "SOCIAL"},
        "sensory": {"border": "accent_tertiary", "tag": "SENSORY"},
        "chaos": {"border": "accent_gold", "tag": "CHAOS"},
        "creative": {"border": "accent_gold", "tag": "CREATIVE"},
        "vocab": {"border": "accent_secondary", "tag": "VOCAB"},
    }.get(quest.category, {"border": "accent_primary", "tag": "QUEST"})

    theme = {"accent_primary": "#00e5ff", "accent_secondary": "#6366f1", "accent_tertiary": "#94a3b8", "accent_gold": "#fbbf24"}
    border_color = theme[cat_config["border"]]

    st.markdown(f"""
    <div class="drx-card {rarity_class}" style="border-top-color: {border_color};">
        <span class="drx-tag">{cat_config['tag']} {'• ' + quest.rarity.upper() if quest.rarity != 'common' else ''}</span>
        <div class="drx-quest-title">{quest.emoji} {quest.title}</div>
        <p class="drx-quest-desc">{quest.desc}</p>
    </div>
    """, unsafe_allow_html=True)

    if quest.assistance_text:
        st.markdown(f'<div class="drx-assistance">{quest.assistance_text}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏁 Log Quest as Finished", use_container_width=True, type="primary"):
            complete_quest(st.session_state.user_id, quest.id)
            with get_session() as session:
                completion = QuestCompletion(
                    user_id=st.session_state.user_id,
                    quest_id=quest.id,
                    completion_date=date.today()
                )
                session.add(completion)
                ds.quest_completed = True
                session.merge(ds)
            st.session_state.quest_just_completed = True
            st.session_state.completed_quest_title = quest.title
            st.rerun()

    with col2:
        reroll_remaining = get_reroll_cap() - ds.reroll_count
        if reroll_remaining > 0:
            if st.button(f"🔀 Reroll ({reroll_remaining} left)", use_container_width=True, type="secondary"):
                increment_reroll(st.session_state.user_id)
                ds.quest_id = None
                ds.reroll_count += 1
                with get_session() as session:
                    session.merge(ds)
                st.session_state.quest_reveal_anim = True
                st.rerun()
        else:
            st.button(f"🔀 Reroll (0 left)", use_container_width=True, disabled=True)
            st.caption("Reroll cap reached. Embrace the challenge.")


def render_ritual_complete(ds: DailySession):
    render_progress(4)
    streak = calculate_streak(st.session_state.user_id)
    milestone = get_streak_milestone(streak)

    st.markdown('<h1 class="drx-title">✨ Ritual Complete</h1>', unsafe_allow_html=True)

    if milestone:
        msg = get_milestone_message(milestone)
        st.markdown(f"""
        <div class="milestone-banner">
            <h3>🏆 MILESTONE: {milestone} DAYS</h3>
            <p>{msg}</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.success(f"🔥 Current streak: **{streak}** days")

    with get_session() as session:
        quest = session.get(Quest, ds.quest_id)
        if quest:
            st.markdown(f"""
            <div class="drx-card">
                <span class="drx-tag">COMPLETED</span>
                <div class="drx-quest-title">{quest.emoji} {quest.title}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛠️ Toolbox")
    st.caption("Utilities for the rest of your day.")

    render_destiny_flip()
    render_archive()


def render_destiny_flip():
    prefs = get_user_preferences(st.session_state.user_id)
    if len(prefs) >= 2:
        opt_a1, opt_a2 = prefs[0]
        opt_b1, opt_b2 = prefs[1]
    else:
        opt_a1, opt_a2 = "Go Out 🏃‍♂️", "Stay In 🏠"
        opt_b1, opt_b2 = "Run Quick ⚡", "Walk Slow 🚶‍♂️"

    st.markdown("#### 🪙 Destiny Coin Flip")
    col1, col2, col3 = st.columns([1, 0.3, 1])

    with col1:
        st.markdown(f"""
        <div class="flip-choice">
            <div class="flip-choice-icon">☕</div>
            <div class="flip-choice-label">{opt_a1}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🎰", key="flip_btn", use_container_width=True):
            result = random.choice([opt_a1, opt_a2])
            st.session_state.flip_result = f"✨ Fate chose: **{result}**"

    with col3:
        st.markdown(f"""
        <div class="flip-choice">
            <div class="flip-choice-icon">🏃</div>
            <div class="flip-choice-label">{opt_a2}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 0.3, 1])

    with col1:
        st.markdown(f"""
        <div class="flip-choice">
            <div class="flip-choice-icon">⚡</div>
            <div class="flip-choice-label">{opt_b1}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🎰", key="flip_btn2", use_container_width=True):
            result = random.choice([opt_b1, opt_b2])
            st.session_state.flip_result = f"✨ Fate chose: **{result}**"

    with col3:
        st.markdown(f"""
        <div class="flip-choice">
            <div class="flip-choice-icon">🚶</div>
            <div class="flip-choice-label">{opt_b2}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.get("flip_result"):
        st.info(st.session_state.flip_result)


def render_archive():
    st.markdown("#### 📜 Past Quests")
    completions = get_recent_completions(st.session_state.user_id, 12)

    if completions:
        st.markdown('<div class="archive-grid">', unsafe_allow_html=True)
        for i, title in enumerate(completions):
            legendary = "archive-item-legendary" if i == 0 else ""
            st.markdown(f"""
            <div class="archive-item {legendary}">
                <div class="archive-item-icon">✨</div>
                <div class="archive-item-title">{title}</div>
                <div class="archive-item-date">Recently</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("No quests completed yet. Your journey begins today.")


def get_recent_completions(user_id: int, limit: int = 10) -> list[str]:
    with get_session() as session:
        from core.models import Quest
        results = session.execute(
            select(Quest.title)
            .join(QuestCompletion, Quest.id == QuestCompletion.quest_id)
            .where(QuestCompletion.user_id == user_id)
            .order_by(QuestCompletion.completed_at.desc())
            .limit(limit)
        ).scalars().all()
        return list(results)


def main():
    init_app()

    if "user_id" not in st.session_state:
        login_page()
        return

    theme_mode = st.session_state.get("theme_mode", "dark")
    inject_theme(theme_mode)

    sidebar_user_panel()

    ds = get_or_create_daily_session(st.session_state.user_id)

    if ds.quest_completed:
        render_ritual_complete(ds)
        return

    if not ds.vibe_check_done:
        render_vibe_check(ds)
    elif not ds.vocab_recall_done:
        render_vocab_recall(ds)
    else:
        render_quest_reveal(ds)


if __name__ == "__main__":
    main()