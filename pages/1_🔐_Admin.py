import streamlit as st
import pandas as pd
from datetime import date, timedelta
from core.db import init_db, get_session
from core.models import User, Quest, Vocab, QuestCompletion, VocabSeen, QuizAttempt, DailySession, AdminSetting, Preference
from core.theme import inject_theme
from sqlalchemy import select, func, desc


st.set_page_config(
    page_title="DayRise Admin",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def check_admin_access():
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 600;">🔐 Admin Access</h1>
            <p style="color: #bac9cc;">Enter the admin passcode to continue.</p>
        </div>
        """, unsafe_allow_html=True)

        passcode = st.text_input("Admin Passcode", type="password", placeholder="Enter passcode")
        if st.button("Access Admin Panel", type="primary", use_container_width=True):
            expected = st.secrets.get("admin_passcode", "changeme123")
            if passcode == expected:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Invalid passcode.")
        st.stop()


def render_dashboard():
    st.markdown('<h1 class="drx-title">📊 Dashboard</h1>', unsafe_allow_html=True)

    with get_session() as session:
        total_users = session.execute(select(func.count(User.id))).scalar()

        today = date.today()
        week_ago = today - timedelta(days=7)

        quests_today = session.execute(
            select(func.count(QuestCompletion.id)).where(QuestCompletion.completion_date == today)
        ).scalar()

        quests_week = session.execute(
            select(func.count(QuestCompletion.id)).where(QuestCompletion.completion_date >= week_ago)
        ).scalar()

        streak_data = session.execute(
            select(User.id, User.username).where(User.adventurer_name.isnot(None))
        ).all()

    streaks = []
    for user_id, username in streak_data:
        with get_session() as session:
            completions = session.execute(
                select(QuestCompletion.completion_date)
                .where(QuestCompletion.user_id == user_id)
                .order_by(QuestCompletion.completion_date.desc())
            ).scalars().all()

        if completions:
            unique_dates = sorted(set(completions), reverse=True)
            streak = 0
            expected = today
            for i, d in enumerate(unique_dates):
                if i == 0:
                    if d == today or d == today - timedelta(days=1):
                        streak = 1
                        expected = d - timedelta(days=1)
                    else:
                        streak = 0
                        break
                else:
                    if d == expected:
                        streak += 1
                        expected = d - timedelta(days=1)
                    else:
                        break
            if streak > 0:
                streaks.append((username, streak))

    streaks.sort(key=lambda x: x[1], reverse=True)
    top_streaks = streaks[:5]

    with get_session() as session:
        category_stats = session.execute(
            select(Quest.category, func.count(QuestCompletion.id))
            .join(QuestCompletion, Quest.id == QuestCompletion.quest_id)
            .group_by(Quest.category)
            .order_by(func.count(QuestCompletion.id).desc())
        ).all()

        reroll_stats = session.execute(
            select(Quest.title, func.count(QuestCompletion.id))
            .join(QuestCompletion, Quest.id == QuestCompletion.quest_id)
            .group_by(Quest.title)
            .order_by(func.count(QuestCompletion.id).desc())
            .limit(5)
        ).all()

        vocab_accuracy = session.execute(
            select(
                func.count(QuizAttempt.id).filter(QuizAttempt.was_correct == True),
                func.count(QuizAttempt.id)
            ).where(QuizAttempt.quiz_type == "vocab_recall")
        ).first()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="drx-card">
            <p class="drx-tag">TOTAL USERS</p>
            <div class="drx-quest-title">{total_users}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="drx-card">
            <p class="drx-tag">QUESTS TODAY</p>
            <div class="drx-quest-title">{quests_today}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="drx-card">
            <p class="drx-tag">QUESTS THIS WEEK</p>
            <div class="drx-quest-title">{quests_week}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Streak Leaderboard")
        if top_streaks:
            for i, (username, streak) in enumerate(top_streaks):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                st.markdown(f"{medal} **{username}** — {streak} days")
        else:
            st.caption("No streaks yet.")

    with col2:
        st.markdown("### 📈 Category Distribution")
        if category_stats:
            df_cat = pd.DataFrame(category_stats, columns=["Category", "Count"])
            st.bar_chart(df_cat.set_index("Category"))
        else:
            st.caption("No quest data yet.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔀 Most Rerolled Quests")
        if reroll_stats:
            for title, count in reroll_stats:
                st.markdown(f"- **{title}**: {count} completions")
        else:
            st.caption("No data yet.")

    with col2:
        st.markdown("### 📝 Vocab Recall Accuracy")
        if vocab_accuracy and vocab_accuracy[1] > 0:
            correct, total = vocab_accuracy
            acc = (correct / total) * 100
            st.metric("Accuracy", f"{acc:.1f}%", f"{correct}/{total}")
        else:
            st.caption("No vocab quiz attempts yet.")


def render_quest_manager():
    st.markdown('<h1 class="drx-title">🗡️ Quest Manager</h1>', unsafe_allow_html=True)

    with get_session() as session:
        quests = session.execute(select(Quest).order_by(Quest.id)).scalars().all()
        for q in quests:
            session.expunge(q)

    if quests:
        df = pd.DataFrame([{
            "ID": q.id,
            "Title": q.title,
            "Category": q.category,
            "Day Type": q.day_type,
            "Rarity": q.rarity,
            "Spice": q.spice_level,
            "Active": q.active,
            "Admin Created": q.created_by_admin,
        } for q in quests])

        edited = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "ID": st.column_config.NumberColumn("ID", disabled=True),
                "Category": st.column_config.SelectboxColumn("Category", options=["dance", "social", "sensory", "chaos", "creative", "vocab", "mindfulness", "fitness", "knowledge"]),
                "Day Type": st.column_config.SelectboxColumn("Day Type", options=["weekday", "weekend", "both"]),
                "Rarity": st.column_config.SelectboxColumn("Rarity", options=["common", "rare", "legendary"]),
                "Spice": st.column_config.SelectboxColumn("Spice", options=["mild", "spicy", "unhinged"]),
                "Active": st.column_config.CheckboxColumn("Active"),
                "Admin Created": st.column_config.CheckboxColumn("Admin Created", disabled=True),
            },
            key="quest_editor"
        )

        if st.button("Save Changes", type="primary"):
            with get_session() as session:
                for _, row in edited.iterrows():
                    quest = session.get(Quest, int(row["ID"]))
                    if quest:
                        quest.title = row["Title"]
                        quest.category = row["Category"]
                        quest.day_type = row["Day Type"]
                        quest.rarity = row["Rarity"]
                        quest.spice_level = row["Spice"]
                        quest.active = row["Active"]
            st.success("Quests updated!")
            st.rerun()
    else:
        st.info("No quests yet.")


def render_vocab_manager():
    st.markdown('<h1 class="drx-title">📚 Vocab Manager</h1>', unsafe_allow_html=True)

    with get_session() as session:
        vocab_list = session.execute(select(Vocab).order_by(Vocab.id)).scalars().all()
        for v in vocab_list:
            session.expunge(v)

    if vocab_list:
        df = pd.DataFrame([{
            "ID": v.id,
            "Language": v.language,
            "Flag": v.flag,
            "Word": v.word,
            "Meaning": v.meaning,
            "Pronunciation": v.pronunciation or "",
            "Active": v.active,
        } for v in vocab_list])

        edited = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "ID": st.column_config.NumberColumn("ID", disabled=True),
                "Active": st.column_config.CheckboxColumn("Active"),
            },
            key="vocab_editor"
        )

        if st.button("Save Changes", type="primary", key="save_vocab"):
            with get_session() as session:
                for _, row in edited.iterrows():
                    vocab = session.get(Vocab, int(row["ID"]))
                    if vocab:
                        vocab.language = row["Language"]
                        vocab.flag = row["Flag"]
                        vocab.word = row["Word"]
                        vocab.meaning = row["Meaning"]
                        vocab.pronunciation = row["Pronunciation"] or None
                        vocab.active = row["Active"]
            st.success("Vocab updated!")
            st.rerun()
    else:
        st.info("No vocab entries yet.")


def render_feature_flags():
    st.markdown('<h1 class="drx-title">⚙️ Feature Flags</h1>', unsafe_allow_html=True)

    with get_session() as session:
        settings = session.execute(select(AdminSetting).order_by(AdminSetting.key)).scalars().all()
        for s in settings:
            session.expunge(s)

    setting_map = {s.key: s.value for s in settings}

    col1, col2 = st.columns(2)
    with col1:
        quiz_enabled = st.toggle("Quiz Enabled", value=setting_map.get("quiz_enabled", "true") == "true")
        spice_selector = st.toggle("Spice Selector Enabled", value=setting_map.get("spice_selector_enabled", "true") == "true")
    with col2:
        reroll_cap = st.number_input("Reroll Cap (per day)", min_value=0, max_value=10, value=int(setting_map.get("reroll_cap", "1")))
        rare_chance = st.slider("Rare Chance", 0.0, 1.0, float(setting_map.get("rare_chance", "0.20")), 0.01)
        legendary_chance = st.slider("Legendary Chance", 0.0, 1.0, float(setting_map.get("legendary_chance", "0.05")), 0.01)

    if st.button("Save Flags", type="primary"):
        with get_session() as session:
            for key, value in [
                ("quiz_enabled", str(quiz_enabled).lower()),
                ("spice_selector_enabled", str(spice_selector).lower()),
                ("reroll_cap", str(reroll_cap)),
                ("rare_chance", str(rare_chance)),
                ("legendary_chance", str(legendary_chance)),
            ]:
                setting = session.get(AdminSetting, key)
                if setting:
                    setting.value = value
                else:
                    session.add(AdminSetting(key=key, value=value))
        st.success("Feature flags updated!")
        st.rerun()


def render_user_lookup():
    st.markdown('<h1 class="drx-title">👥 User Lookup</h1>', unsafe_allow_html=True)

    search = st.text_input("Search by username", placeholder="Enter username...")

    with get_session() as session:
        query = select(User).order_by(User.created_at.desc())
        if search:
            query = query.where(User.username.ilike(f"%{search}%"))
        users = session.execute(query.limit(50)).scalars().all()
        for u in users:
            session.expunge(u)

    if users:
        for user in users:
            with st.expander(f"{user.username} — {user.adventurer_name or 'No name yet'}"):
                streak = calculate_streak(user.id)
                st.markdown(f"**Streak:** {streak} days")
                st.markdown(f"**Theme:** {user.theme_preference}")
                st.markdown(f"**Spice:** {user.spice_level}")
                st.markdown(f"**Created:** {user.created_at.strftime('%Y-%m-%d')}")

                with get_session() as session:
                    completions = session.execute(
                        select(QuestCompletion)
                        .where(QuestCompletion.user_id == user.id)
                        .order_by(QuestCompletion.completed_at.desc())
                        .limit(10)
                    ).scalars().all()
                    for c in completions:
                        session.expunge(c)

                if completions:
                    st.markdown("**Recent Quests:**")
                    for c in completions:
                        with get_session() as session:
                            quest = session.get(Quest, c.quest_id)
                            if quest:
                                session.expunge(quest)
                        st.caption(f"- {quest.title if quest else 'Unknown'} ({c.completion_date})")

                with get_session() as session:
                    prefs = session.execute(
                        select(Preference).where(Preference.user_id == user.id).order_by(Preference.axis_index)
                    ).scalars().all()
                    for p in prefs:
                        session.expunge(p)
                if prefs:
                    st.markdown("**Preferences:**")
                    for p in prefs:
                        st.caption(f"- Axis {p.axis_index}: {p.option_a} | {p.option_b}")

                if st.button("Reset PIN", key=f"reset_{user.id}", type="secondary"):
                    st.session_state[f"reset_pin_{user.id}"] = True

                if st.session_state.get(f"reset_pin_{user.id}"):
                    new_pin = st.text_input("New 4-digit PIN", type="password", max_chars=4, key=f"newpin_{user.id}")
                    if st.button("Confirm Reset", key=f"confirm_{user.id}"):
                        if len(new_pin) == 4 and new_pin.isdigit():
                            from core.auth import hash_pin
                            pin_hash, salt = hash_pin(new_pin)
                            with get_session() as session:
                                u = session.get(User, user.id)
                                if u:
                                    u.pin_hash = pin_hash
                                    u.pin_salt = salt
                            st.success("PIN reset!")
                            st.session_state[f"reset_pin_{user.id}"] = False
                            st.rerun()
                        else:
                            st.error("PIN must be 4 digits.")


def calculate_streak(user_id: int) -> int:
    with get_session() as session:
        completions = session.execute(
            select(QuestCompletion.completion_date)
            .where(QuestCompletion.user_id == user_id)
            .order_by(QuestCompletion.completion_date.desc())
        ).scalars().all()

    if not completions:
        return 0

    unique_dates = sorted(set(completions), reverse=True)
    today = date.today()

    streak = 0
    expected = today
    for i, d in enumerate(unique_dates):
        if i == 0:
            if d == today or d == today - timedelta(days=1):
                streak = 1
                expected = d - timedelta(days=1)
            else:
                return 0
        else:
            if d == expected:
                streak += 1
                expected = d - timedelta(days=1)
            else:
                break

    return streak


def main():
    init_db()
    inject_theme("dark")
    check_admin_access()

    st.sidebar.title("🔐 Admin Panel")
    tab = st.sidebar.radio("Navigate", ["Dashboard", "Quest Manager", "Vocab Manager", "Feature Flags", "User Lookup"])

    if tab == "Dashboard":
        render_dashboard()
    elif tab == "Quest Manager":
        render_quest_manager()
    elif tab == "Vocab Manager":
        render_vocab_manager()
    elif tab == "Feature Flags":
        render_feature_flags()
    elif tab == "User Lookup":
        render_user_lookup()


if __name__ == "__main__":
    main()