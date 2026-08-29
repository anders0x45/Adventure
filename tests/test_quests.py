import pytest
from datetime import date
from core.db import init_db, get_session
from core.models import Quest, AdminSetting, User, QuestCompletion, DailySession, Preference
from core.quests import (
    select_quest_for_user, get_reroll_cap, can_reroll, increment_reroll,
    roll_rarity, compute_vibe_weights, suggest_spice_level, get_spice_levels
)
from core.auth import create_user
from sqlalchemy import select, delete


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    with get_session() as session:
        # Delete in correct order to respect FK constraints
        session.execute(delete(QuestCompletion))
        session.execute(delete(DailySession))
        session.execute(delete(Quest))
        session.execute(delete(AdminSetting))
        session.execute(delete(User))
        session.execute(delete(Preference))

        # Seed admin settings
        for key, value in [
            ("reroll_cap", "1"),
            ("rare_chance", "0.20"),
            ("legendary_chance", "0.05"),
        ]:
            session.add(AdminSetting(key=key, value=value))

        # Seed quests for each spice level
        for spice in ["mild", "spicy", "unhinged"]:
            for rarity in ["common", "rare", "legendary"]:
                for day_type in ["weekday", "weekend"]:
                    q = Quest(
                        title=f"Test {spice} {rarity} {day_type}",
                        desc="Test description",
                        category="dance",
                        emoji="💃",
                        assistance_text="Test",
                        day_type=day_type,
                        rarity=rarity,
                        spice_level=spice,
                        active=True,
                    )
                    session.add(q)
        session.commit()


def test_spice_level_filtering():
    user_id, _ = create_user("testuser1", "1234")
    quest = select_quest_for_user(user_id, "mild")
    assert quest is not None
    assert quest.spice_level == "mild"

    quest = select_quest_for_user(user_id, "spicy")
    assert quest is not None
    assert quest.spice_level == "spicy"

    quest = select_quest_for_user(user_id, "unhinged")
    assert quest is not None
    assert quest.spice_level == "unhinged"


def test_rarity_roll_distribution():
    legendary_count = 0
    rare_count = 0
    common_count = 0
    trials = 10000

    for _ in range(trials):
        r = roll_rarity()
        if r == "legendary":
            legendary_count += 1
        elif r == "rare":
            rare_count += 1
        else:
            common_count += 1

    legendary_pct = legendary_count / trials
    rare_pct = rare_count / trials
    common_pct = common_count / trials

    assert 0.02 < legendary_pct < 0.08  # ~5%
    assert 0.15 < rare_pct < 0.25      # ~20%
    assert 0.70 < common_pct < 0.80    # ~75%


def test_reroll_cap_enforcement():
    user_id, _ = create_user("testuser2", "1234")
    today = date.today()

    with get_session() as session:
        ds = DailySession(user_id=user_id, session_date=today, reroll_count=0)
        session.add(ds)

    assert can_reroll(user_id) == True

    increment_reroll(user_id)
    assert can_reroll(user_id) == False

    # Test with higher cap
    with get_session() as session:
        setting = session.get(AdminSetting, "reroll_cap")
        setting.value = "3"
        ds = session.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today
            )
        ).scalar_one()
        ds.reroll_count = 2

    assert can_reroll(user_id) == True
    increment_reroll(user_id)
    assert can_reroll(user_id) == False


def test_vibe_weights():
    answers = {"energy": "a", "social": "b", "setting": "a"}
    weights = compute_vibe_weights(answers)

    # Energetic + Indoors should boost dance, creative
    assert weights.get("dance", 1.0) > 1.0
    assert weights.get("creative", 1.0) > 1.0

    # Social should boost social
    assert weights.get("social", 1.0) > 1.0

    # All categories present
    for cat in ["dance", "social", "sensory", "chaos", "creative", "vocab", "mindfulness", "fitness", "knowledge"]:
        assert cat in weights


def test_spice_suggestion():
    # High energy + social + outdoors = spicy
    assert suggest_spice_level({"energy": "a", "social": "b", "setting": "b"}) == "spicy"
    # Medium = mild
    assert suggest_spice_level({"energy": "a", "social": "a", "setting": "a"}) == "mild"
    # Low = mild
    assert suggest_spice_level({"energy": "b", "social": "a", "setting": "a"}) == "mild"


def test_get_spice_levels():
    levels = get_spice_levels()
    assert levels == ["mild", "spicy", "unhinged"]


def test_quest_selection_with_vibe_weights():
    user_id, _ = create_user("testuser3", "1234")
    # Strong preference for dance
    weights = {"dance": 2.0, "social": 1.0, "sensory": 1.0, "chaos": 1.0, "creative": 1.0,
               "vocab": 1.0, "mindfulness": 1.0, "fitness": 1.0, "knowledge": 1.0}

    dance_count = 0
    trials = 100
    for _ in range(trials):
        quest = select_quest_for_user(user_id, "mild", weights)
        if quest and quest.category == "dance":
            dance_count += 1

    # Dance should be selected more often than pure random (1/9 ≈ 11%)
    assert dance_count / trials > 0.15