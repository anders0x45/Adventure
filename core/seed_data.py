from core.db import get_session
from core.models import Quest, Vocab, AdminSetting
from sqlalchemy import select


WEEKDAY_QUESTS = [
    {
        "title": "The Kitchen Counter Dance-Off",
        "desc": "While waiting for morning prep work or water to boil, clear a 3-foot space and execute an uninhibited, energetic 45-second solo dance routine. Nobody is watching.",
        "category": "dance",
        "emoji": "💃",
        "assistance_text": "💡 *Need a track? Put on a high-tempo song right now before you chicken out!*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Secret Agent Walk",
        "desc": "Match your steps precisely to the rhythm of whatever upbeat track is in your head right now. Navigate your next walk like you are the lead character in a high-stakes film.",
        "category": "dance",
        "emoji": "🕺",
        "assistance_text": "💡 *Keep your chin up, shoulders back, and time your pace precisely to the rhythm.*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Desktop Conductor",
        "desc": "Put on an intense track at your desk. Use your hands and arms to dramatically conduct the music for 60 seconds as if leading an invisible orchestra.",
        "category": "dance",
        "emoji": "🪄",
        "assistance_text": "💡 *Lean into the crescendo! Perfect for a quick, mid-day mental clarity break.*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Dynamic Drink Call",
        "desc": "Send a spontaneous text to a nearby friend: 'Free for a quick drink or coffee in the next 48 hours? Catch up with zero fixed agendas.'",
        "category": "social",
        "emoji": "🍹",
        "assistance_text": "💡 *Stuck on who? Open your message app, scroll down to the 5th person on your list, and hit them up.*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The One-Word Compliment Drop",
        "desc": "Give three different people a genuine one-word compliment today. Track their reactions — see who lights up the most.",
        "category": "social",
        "emoji": "💬",
        "assistance_text": "💡 *Impactful words that work nicely: 'Radiant', 'Stellar', 'Impactful', or 'Unstoppable'.",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Reverse Commute Explorer",
        "desc": "Take one different turn, street, or exit on your way home today. Document one new thing you spotted.",
        "category": "sensory",
        "emoji": "🔄",
        "assistance_text": "💡 *Look closely for dynamic architectural lines or unique storefronts you usually pass by.*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Left-Handed Rebel",
        "desc": "Do an ordinary task right now — like unlocking a door or navigating your phone — using your non-dominant hand.",
        "category": "chaos",
        "emoji": "✋",
        "assistance_text": "💡 *Use your personalized Destiny Flip tool below to choose which basic task you should force your hand to try first!*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Cultural Language Integration",
        "desc": "Take a beautifully descriptive word from another culture and intentionally inject it into a text, conversation, or journal entry today.",
        "category": "vocab",
        "emoji": "🌐",
        "assistance_text": "💡 *Check out the randomized Concept Vocabulary module at the bottom of your screen to source your word!*",
        "day_type": "weekday",
        "rarity": "common",
        "spice_level": "mild",
    },
]

WEEKEND_QUESTS = [
    {
        "title": "The Midnight Dance Ritual",
        "desc": "Turn off all the lights in a room, queue up a song with a heavy bassline, and move your body strictly based on what feels right in the pitch dark.",
        "category": "dance",
        "emoji": "🌌",
        "assistance_text": "💡 *Close your eyes even if it's already dark. Let go of what you look like entirely.*",
        "day_type": "weekend",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Flavor Alchemist",
        "desc": "Bake or cook something simple today, but consciously swap out one foundational sugar, spice, or base liquid for a dynamic alternative you have in your cupboards.",
        "category": "creative",
        "emoji": "🍪",
        "assistance_text": "💡 *Unsure which direction to head? Use the Destiny Flip below to choose between a flavor switch or a texture modification.*",
        "day_type": "weekend",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Coin Toss Explorer",
        "desc": "At every unplanned fork in your day, let your custom preference matrix choose your direction.",
        "category": "chaos",
        "emoji": "🪙",
        "assistance_text": "💡 *The Destiny Flip tool below is completely calibrated to your profile choices and ready.*",
        "day_type": "weekend",
        "rarity": "common",
        "spice_level": "mild",
    },
    {
        "title": "The Soundscape Iso-Check",
        "desc": "Sit somewhere outside for 3 minutes with your eyes closed. Isolate the single highest-pitched sound and the lowest-frequency sound around you.",
        "category": "sensory",
        "emoji": "🎧",
        "assistance_text": "💡 *Block out passing cars if you can, and listen instead for wind rustles or deep bird calls.*",
        "day_type": "weekend",
        "rarity": "common",
        "spice_level": "mild",
    },
]

VOCAB_BANK = [
    {
        "language": "Spanish",
        "flag": "🇪🇸",
        "word": "Duende",
        "meaning": "A heightened state of raw emotion and authenticity, especially felt during art or performance.",
        "pronunciation": "dwen-deh",
    },
    {
        "language": "Amharic",
        "flag": "🇪🇹",
        "word": "Buna",
        "meaning": "Coffee — but truly a ceremony of slowing down and connecting with the people around you.",
        "pronunciation": "boo-nah",
    },
    {
        "language": "Japanese",
        "flag": "🇯🇵",
        "word": "Komorebi",
        "meaning": "The dappled sunlight that filters through leaves in a forest canopy.",
        "pronunciation": "koh-moh-reh-bee",
    },
    {
        "language": "Swedish",
        "flag": "🇸🇪",
        "word": "Gökotta",
        "meaning": "Waking up early in the morning intentionally to go outside and hear the first birds sing.",
        "pronunciation": "goh-kot-tah",
    },
]

DEFAULT_ADMIN_SETTINGS = {
    "quiz_enabled": "true",
    "spice_selector_enabled": "true",
    "reroll_cap": "1",
    "legendary_chance": "0.05",
    "rare_chance": "0.20",
}


def seed_quests(session):
    for q_data in WEEKDAY_QUESTS + WEEKEND_QUESTS:
        exists = session.execute(
            select(Quest).where(Quest.title == q_data["title"])
        ).scalar_one_or_none()
        if not exists:
            quest = Quest(**q_data)
            session.add(quest)


def seed_vocab(session):
    for v_data in VOCAB_BANK:
        exists = session.execute(
            select(Vocab).where(Vocab.word == v_data["word"])
        ).scalar_one_or_none()
        if not exists:
            vocab = Vocab(**v_data)
            session.add(vocab)


def seed_admin_settings(session):
    for key, value in DEFAULT_ADMIN_SETTINGS.items():
        exists = session.get(AdminSetting, key)
        if not exists:
            setting = AdminSetting(key=key, value=value)
            session.add(setting)


def run_seed():
    with get_session() as session:
        seed_quests(session)
        seed_vocab(session)
        seed_admin_settings(session)


if __name__ == "__main__":
    from core.db import init_db
    init_db()
    run_seed()
    print("Seed complete.")