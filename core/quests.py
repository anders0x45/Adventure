import random
from datetime import date
from core.db import get_session
from core.models import Quest, AdminSetting, DailySession
from sqlalchemy import select


def get_admin_setting(key: str, default: str) -> str:
    with get_session() as session:
        setting = session.get(AdminSetting, key)
        return setting.value if setting else default


def is_weekend(d: date = None) -> bool:
    if d is None:
        d = date.today()
    return d.weekday() >= 5


def get_day_type(d: date = None) -> str:
    return "weekend" if is_weekend(d) else "weekday"


def get_rarity_chances() -> tuple[float, float]:
    rare_chance = float(get_admin_setting("rare_chance", "0.20"))
    legendary_chance = float(get_admin_setting("legendary_chance", "0.05"))
    return rare_chance, legendary_chance


def roll_rarity() -> str:
    rare_chance, legendary_chance = get_rarity_chances()
    r = random.random()
    if r < legendary_chance:
        return "legendary"
    elif r < legendary_chance + rare_chance:
        return "rare"
    return "common"


def get_quest_candidates(spice_level: str, day_type: str, target_rarity: str = None):
    with get_session() as session:
        query = select(Quest).where(
            Quest.active == True,
            Quest.spice_level == spice_level,
            Quest.day_type.in_([day_type, "both"])
        )
        if target_rarity:
            query = query.where(Quest.rarity == target_rarity)
        candidates = session.execute(query).scalars().all()
        # Force load all columns and expunge to avoid detached instance errors
        for c in candidates:
            _ = c.id, c.title, c.category, c.rarity, c.spice_level, c.day_type, c.emoji, c.desc, c.assistance_text
            session.expunge(c)
        return candidates


def select_quest_for_user(user_id: int, spice_level: str, vibe_weights: dict = None) -> Quest | None:
    day_type = get_day_type()
    target_rarity = roll_rarity()

    candidates = get_quest_candidates(spice_level, day_type, target_rarity)

    if not candidates:
        candidates = get_quest_candidates(spice_level, day_type)

    if not candidates:
        with get_session() as session:
            candidates = session.execute(
                select(Quest).where(Quest.active == True, Quest.day_type.in_([day_type, "both"]))
            ).scalars().all()
            for c in candidates:
                _ = c.id, c.title, c.category, c.rarity, c.spice_level, c.day_type, c.emoji, c.desc, c.assistance_text
                session.expunge(c)

    if not candidates:
        return None

    if vibe_weights:
        weights = []
        for quest in candidates:
            weight = 1.0
            cat_weight = vibe_weights.get(quest.category, 1.0)
            weight *= cat_weight
            if quest.rarity == "legendary":
                weight *= 0.5
            elif quest.rarity == "rare":
                weight *= 0.75
            weights.append(weight)

        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
            selected = random.choices(candidates, weights=weights, k=1)[0]
        else:
            selected = random.choice(candidates)
    else:
        selected = random.choice(candidates)

    # Expunge the selected quest to avoid detached instance errors
    with get_session() as session:
        if selected in session:
            session.expunge(selected)

    return selected


def get_reroll_cap() -> int:
    return int(get_admin_setting("reroll_cap", "1"))


def can_reroll(user_id: int) -> bool:
    today = date.today()
    with get_session() as session:
        session_obj = session.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today
            )
        ).scalar_one_or_none()
        if not session_obj:
            return True
        return session_obj.reroll_count < get_reroll_cap()


def increment_reroll(user_id: int):
    today = date.today()
    with get_session() as session:
        session_obj = session.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today
            )
        ).scalar_one_or_none()
        if session_obj:
            session_obj.reroll_count += 1


def get_vibe_check_questions() -> list[dict]:
    return [
        {
            "key": "energy",
            "question": "How's your energy right now?",
            "option_a": "Energetic ⚡",
            "option_b": "Calm 🧘",
            "categories_a": ["dance", "fitness", "chaos"],
            "categories_b": ["mindfulness", "sensory", "creative"],
        },
        {
            "key": "social",
            "question": "What's your vibe for company?",
            "option_a": "Solo 🦸",
            "option_b": "Social 🤝",
            "categories_a": ["sensory", "creative", "knowledge"],
            "categories_b": ["social", "dance", "chaos"],
        },
        {
            "key": "setting",
            "question": "Where would you rather be?",
            "option_a": "Indoors 🏠",
            "option_b": "Outdoors 🌲",
            "categories_a": ["creative", "knowledge", "mindfulness"],
            "categories_b": ["fitness", "sensory", "chaos"],
        },
    ]


def compute_vibe_weights(answers: dict) -> dict:
    weights = {}
    questions = get_vibe_check_questions()
    for q in questions:
        key = q["key"]
        answer = answers.get(key, "a")
        if answer == "a":
            for cat in q["categories_a"]:
                weights[cat] = weights.get(cat, 1.0) + 0.3
        else:
            for cat in q["categories_b"]:
                weights[cat] = weights.get(cat, 1.0) + 0.3

    all_categories = ["dance", "social", "sensory", "chaos", "creative", "vocab", "mindfulness", "fitness", "knowledge"]
    for cat in all_categories:
        weights.setdefault(cat, 1.0)

    return weights


def suggest_spice_level(answers: dict) -> str:
    energetic = answers.get("energy") == "a"
    social = answers.get("social") == "b"
    outdoors = answers.get("setting") == "b"

    score = sum([energetic, social, outdoors])

    if score >= 2:
        return "spicy"
    elif score >= 1:
        return "mild"
    return "mild"


def get_spice_levels() -> list[str]:
    return ["mild", "spicy", "unhinged"]


def complete_quest(user_id: int, quest_id: int):
    from datetime import datetime
    today = date.today()
    with get_session() as session:
        completion = session.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today
            )
        ).scalar_one_or_none()
        if completion:
            completion.quest_completed = True
            completion.quest_id = quest_id