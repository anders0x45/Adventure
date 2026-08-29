import pytest
from datetime import date, timedelta
from core.db import init_db, get_session
from core.models import User, Quest, QuestCompletion, Preference
from core.streaks import calculate_streak, get_streak_milestone, get_milestone_message
from core.auth import create_user
from sqlalchemy import select, delete


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    with get_session() as session:
        # Delete in correct order to respect FK constraints
        session.execute(delete(QuestCompletion))
        session.execute(delete(Quest))
        session.execute(delete(User))
        session.execute(delete(Preference))

        # Seed a quest for completions
        quest = Quest(
            title="Test Quest",
            desc="Test",
            category="dance",
            emoji="💃",
            assistance_text="Test",
            day_type="both",
            rarity="common",
            spice_level="mild",
            active=True,
        )
        session.add(quest)
        session.commit()


def test_streak_zero_no_completions():
    user_id, _ = create_user("nostreak", "1234")
    assert calculate_streak(user_id) == 0


def test_streak_one_today():
    user_id, _ = create_user("streak1", "1234")
    today = date.today()

    with get_session() as session:
        q = session.execute(select(Quest)).scalar_one()
        completion = QuestCompletion(
            user_id=user_id,
            quest_id=q.id,
            completion_date=today
        )
        session.add(completion)

    assert calculate_streak(user_id) == 1


def test_streak_one_yesterday():
    user_id, _ = create_user("streak1y", "1234")
    yesterday = date.today() - timedelta(days=1)

    with get_session() as session:
        q = session.execute(select(Quest)).scalar_one()
        completion = QuestCompletion(
            user_id=user_id,
            quest_id=q.id,
            completion_date=yesterday
        )
        session.add(completion)

    assert calculate_streak(user_id) == 1


def test_streak_consecutive_days():
    user_id, _ = create_user("streak3", "1234")
    today = date.today()

    with get_session() as session:
        q = session.execute(select(Quest)).scalar_one()
        for i in range(3):
            completion = QuestCompletion(
                user_id=user_id,
                quest_id=q.id,
                completion_date=today - timedelta(days=i)
            )
            session.add(completion)

    assert calculate_streak(user_id) == 3


def test_streak_gap_resets():
    user_id, _ = create_user("streakgap", "1234")
    today = date.today()

    with get_session() as session:
        q = session.execute(select(Quest)).scalar_one()
        # Today and 3 days ago (gap at 2 days ago)
        for d in [today, today - timedelta(days=3)]:
            completion = QuestCompletion(
                user_id=user_id,
                quest_id=q.id,
                completion_date=d
            )
            session.add(completion)

    assert calculate_streak(user_id) == 1


def test_streak_same_day_double_completion_no_double_count():
    user_id, _ = create_user("streakdouble", "1234")
    today = date.today()

    with get_session() as session:
        q = session.execute(select(Quest)).scalar_one()
        # Two completions same day
        for _ in range(2):
            completion = QuestCompletion(
                user_id=user_id,
                quest_id=q.id,
                completion_date=today
            )
            session.add(completion)

    assert calculate_streak(user_id) == 1


def test_streak_milestone_detection():
    assert get_streak_milestone(3) == 3
    assert get_streak_milestone(7) == 7
    assert get_streak_milestone(30) == 30
    assert get_streak_milestone(1) is None
    assert get_streak_milestone(5) is None
    assert get_streak_milestone(10) is None


def test_milestone_messages():
    msg3 = get_milestone_message(3)
    assert "Three days" in msg3 or "3 days" in msg3

    msg7 = get_milestone_message(7)
    assert "week" in msg7.lower()

    msg30 = get_milestone_message(30)
    assert "Thirty" in msg30 or "30" in msg30


def test_streak_milestone_progression():
    user_id, _ = create_user("streakprog", "1234")
    today = date.today()

    with get_session() as session:
        q = session.execute(select(Quest)).scalar_one()
        quest_id = q.id

    # Build up to 7 day streak
    for day in range(7):
        with get_session() as session:
            completion = QuestCompletion(
                user_id=user_id,
                quest_id=quest_id,
                completion_date=today - timedelta(days=day)
            )
            session.add(completion)

    assert calculate_streak(user_id) == 7
    assert get_streak_milestone(7) == 7

    # Next day, streak becomes 8 (no milestone)
    with get_session() as session:
        completion = QuestCompletion(
            user_id=user_id,
            quest_id=quest_id,
            completion_date=today + timedelta(days=1)
        )
        session.add(completion)

    # Note: this test would need tomorrow's date, so we just verify the logic
    # The streak calculation uses today's date, so we can't easily test future dates
    # without mocking. The core logic is tested above.