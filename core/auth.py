import hashlib
import secrets
from core.db import get_session
from core.models import User, Preference
from sqlalchemy import select
import random


PREFIX_DATA = {
    "Vesper": {"theme": "Shadow/Night", "desc": "A quiet catalyst operating in twilight hours", "color": "#d8b4fe"},
    "Atlas": {"theme": "Mapping/Earth", "desc": "A structural anchor testing the boundaries of routine", "color": "#7dd3fc"},
    "Echo": {"theme": "Rhythm/Sound", "desc": "An atmospheric force expanding sensory signals", "color": "#fca5a5"},
    "Sable": {"theme": "Stealth/Focus", "desc": "A sleek, highly observant disruption agent", "color": "#94a3b8"},
    "Nova": {"theme": "Cosmic/Energy", "desc": "A sudden burst of bright, chaotic behavioral shifts", "color": "#fde047"},
    "Zephyr": {"theme": "Air/Movement", "desc": "A free-flowing entity shifting paths fluidly", "color": "#86efac"},
}
SUFFIX_DATA = {
    "Rogue": "who shatters established guidelines to uncover hidden micro-moments.",
    "Vortex": "who pulls nearby structures into a swirl of deliberate spontaneity.",
    "Sage": "who calculates precise, thoughtful deviations from the everyday norm.",
    "Wilder": "who roams through urban and creative spaces with uninhibited curiosity.",
    "Flux": "who constantly shifts states to keep external environments off-balance.",
    "Chrono": "who bends the daily timeline to extract extra life from standard hours.",
}


def hash_pin(pin: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    pin_hash = hashlib.sha256((pin + salt).encode()).hexdigest()
    return pin_hash, salt


def verify_pin(pin: str, pin_hash: str, salt: str) -> bool:
    computed_hash, _ = hash_pin(pin, salt)
    return computed_hash == pin_hash


def generate_adventurer_name() -> tuple[str, str]:
    used_names = set()
    with get_session() as session:
        for user in session.execute(select(User)).scalars():
            if user.adventurer_name:
                used_names.add(user.adventurer_name)

    while True:
        p_choice = random.choice(list(PREFIX_DATA.keys()))
        s_choice = random.choice(list(SUFFIX_DATA.keys()))
        candidate = f"{p_choice} {s_choice}"
        if candidate not in used_names:
            return p_choice, s_choice


def create_user(username: str, pin: str) -> tuple[int, str]:
    pin_hash, salt = hash_pin(pin)
    prefix, suffix = generate_adventurer_name()
    adventurer_name = f"{prefix} {suffix}"

    with get_session() as session:
        user = User(
            username=username.lower(),
            pin_hash=pin_hash,
            pin_salt=salt,
            adventurer_name=adventurer_name,
            prefix=prefix,
            suffix=suffix,
        )
        session.add(user)
        session.flush()

        user_id = user.id

        default_prefs = [
            Preference(user_id=user_id, axis_index=0, option_a="Go Out 🏃‍♂️", option_b="Stay In 🏠"),
            Preference(user_id=user_id, axis_index=1, option_a="Run Quick ⚡", option_b="Walk Slow 🚶‍♂️"),
        ]
        for pref in default_prefs:
            session.add(pref)

        return user_id, adventurer_name


def authenticate_user(username: str, pin: str) -> tuple[int, str, str, str] | None:
    with get_session() as session:
        user = session.execute(
            select(User).where(User.username == username.lower())
        ).scalar_one_or_none()
        if user and verify_pin(pin, user.pin_hash, user.pin_salt):
            return user.id, user.username, user.adventurer_name, user.theme_preference
        return None


def get_user_by_id(user_id: int) -> User | None:
    with get_session() as session:
        return session.get(User, user_id)


def get_user_preferences(user_id: int) -> list[tuple[str, str]]:
    with get_session() as session:
        prefs = session.execute(
            select(Preference).where(Preference.user_id == user_id).order_by(Preference.axis_index)
        ).scalars().all()
        return [(p.option_a, p.option_b) for p in prefs]


def update_user_preferences(user_id: int, preferences: list[tuple[str, str]]):
    with get_session() as session:
        for axis_index, (option_a, option_b) in enumerate(preferences):
            pref = session.execute(
                select(Preference).where(
                    Preference.user_id == user_id,
                    Preference.axis_index == axis_index
                )
            ).scalar_one_or_none()
            if pref:
                pref.option_a = option_a
                pref.option_b = option_b
            else:
                session.add(Preference(
                    user_id=user_id,
                    axis_index=axis_index,
                    option_a=option_a,
                    option_b=option_b
                ))


def update_user_spice_level(user_id: int, spice_level: str):
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            user.spice_level = spice_level


def update_user_theme(user_id: int, theme: str):
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            user.theme_preference = theme


def username_exists(username: str) -> bool:
    with get_session() as session:
        return session.execute(
            select(User.id).where(User.username == username.lower())
        ).scalar_one_or_none() is not None