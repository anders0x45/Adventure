from datetime import date, timedelta
from core.db import get_session
from core.models import QuestCompletion
from sqlalchemy import select


MILESTONES = [3, 7, 30]


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
    expected_date = today

    for i, completion_date in enumerate(unique_dates):
        if i == 0:
            if completion_date == today or completion_date == today - timedelta(days=1):
                streak = 1
                expected_date = completion_date - timedelta(days=1)
            else:
                return 0
        else:
            if completion_date == expected_date:
                streak += 1
                expected_date = completion_date - timedelta(days=1)
            else:
                break

    return streak


def get_streak_milestone(streak: int) -> int | None:
    for milestone in MILESTONES:
        if streak == milestone:
            return milestone
    return None


def get_next_milestone(streak: int) -> int | None:
    for milestone in MILESTONES:
        if streak < milestone:
            return milestone
    return None


def get_milestone_message(milestone: int) -> str:
    messages = {
        3: "🔥 Three days straight! You're building momentum.",
        7: "⚡ A full week! The rhythm is becoming habit.",
        30: "🏆 Thirty days! You've forged a new path.",
    }
    return messages.get(milestone, f"🎉 Milestone reached: {milestone} days!")


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


def get_completion_count(user_id: int, days: int = 7) -> int:
    cutoff = date.today() - timedelta(days=days - 1)
    with get_session() as session:
        count = session.execute(
            select(QuestCompletion)
            .where(QuestCompletion.user_id == user_id, QuestCompletion.completion_date >= cutoff)
        ).scalars().all()
        return len(count)