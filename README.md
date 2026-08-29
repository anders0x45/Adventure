# DayRise Adventures

A personalized daily quest app that breaks routine through micro-adventures, vocabulary discovery, and a touch of chaos. Built with Streamlit, SQLAlchemy, and a design system inspired by premium tech dashboards.

## 🎯 What It Does

**Daily Ritual** — A guided 4-step flow each day:
1. **Vibe Check** — 3 quick taps (energy, social, setting) to calibrate your quest
2. **Memory Forge** — Recall yesterday's vocabulary word, then discover a new one
3. **Quest Reveal** — Unlock a personalized micro-adventure weighted by your vibe, spice level, and rarity
4. **Ritual Complete** — Log completion, see streak milestones, access the Toolbox

**Toolbox** (available all day):
- **Destiny Coin Flip** — Your custom "This or That" dilemma resolver
- **Archive** — Browse completed quests

**Admin Dashboard** — Manage quests, vocab, feature flags, and users

## 🎨 Design System

The visual language draws from the **Aeon Prime** design system:
- **Dark-mode first** with slate-900 backgrounds
- **Icy Blue (#00E5FF)** primary accent for active states
- **Electric Indigo (#6366F1)** for brand moments
- **Plus Jakarta Sans** typography (Light 300 for body, Semi-Bold 600 for headlines)
- **Glassmorphism** cards with 1px borders, 8px radius
- **8px spacing rhythm** throughout

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Local Development

```bash
# Clone and enter
cd Adventure

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and set a secure admin_passcode

# Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

### First Run
1. Open the app → you'll see the login screen
2. Click "Create Adventurer" → choose a username and 4-digit PIN
3. Your adventurer name (e.g., "Vesper Rogue") is generated automatically
4. Complete your first Daily Ritual!

## 🔐 Admin Access

Navigate to `http://localhost:8501/1_🔐_Admin` (or use the multipage nav) and enter the `admin_passcode` from your secrets file.

Admin capabilities:
- **Dashboard** — Platform metrics, streak leaderboard, category distribution
- **Quest Manager** — Full CRUD on quests (title, category, day_type, rarity, spice, active)
- **Vocab Manager** — Full CRUD on vocabulary entries
- **Feature Flags** — Toggle quizzes, spice selector, set reroll cap, rare/legendary chances
- **User Lookup** — Search users, view streaks/preferences, reset PINs

## ☁️ Deployment to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select your repo, branch `main`, main file `app.py`
4. In **Advanced settings → Secrets**, add:
   ```toml
   admin_passcode = "your-secure-passcode-here"
   DATABASE_URL = "postgresql://..."  # See below
   ```
5. Deploy!

### ⚠️ Production Persistence: The Postgres Swap

**Streamlit Community Cloud's filesystem is ephemeral** — containers can be recycled, losing any local SQLite file. For durable production data:

1. Provision a free hosted Postgres (recommended: [Supabase](https://supabase.com) or [Neon](https://neon.tech))
2. Get the connection string (looks like `postgresql://user:pass@host:port/db`)
3. Add it as `DATABASE_URL` in Streamlit secrets
4. That's it — SQLAlchemy handles the rest, zero code changes

```toml
# .streamlit/secrets.toml (production)
admin_passcode = "super-secure-passcode"
DATABASE_URL = "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
```

The app defaults to `sqlite:///dayrise.db` when `DATABASE_URL` is unset, perfect for local dev.

## 📁 Project Structure

```
Adventure/
├── app.py                      # Daily Ritual entrypoint
├── pages/
│   └── 1_🔐_Admin.py           # Admin dashboard (multipage)
├── core/
│   ├── __init__.py
│   ├── db.py                   # SQLAlchemy engine/session
│   ├── models.py               # ORM models
│   ├── seed_data.py            # Idempotent quest/vocab/flag seeding
│   ├── auth.py                 # Username + PIN signup/login
│   ├── quests.py               # Weighted selection, rarity, spice
│   ├── vocab.py                # Vocab recall quiz logic
│   ├── streaks.py              # Streak calculation, milestones
│   └── theme.py                # CSS/theme constants (Aeon Prime)
├── .streamlit/
│   ├── secrets.toml.example    # Template for secrets
│   └── config.toml             # Streamlit config
├── requirements.txt            # Pinned dependencies
└── tests/
    ├── test_quests.py
    └── test_streaks.py
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests cover:
- `test_quests.py` — Weighted selection respects spice filtering, rarity probabilities, reroll cap
- `test_streaks.py` — Consecutive days, gap resets, same-day double-completion protection

## 🎮 Game Mechanics

| Mechanic | Description |
|----------|-------------|
| **Rarity** | Common (75%), Rare (20%), Legendary (5%) — configurable via admin |
| **Spice Levels** | Mild / Spicy / Unhinged — filters quest pool, suggested by vibe check |
| **Reroll Cap** | Default 1/day — prevents infinite rerolling |
| **Streak Milestones** | 3, 7, 30 days — distinct celebrations |
| **Vibe Weighting** | 3 binary questions → category boost for quest selection |
| **Vocab Recall** | Spaced repetition — quiz on prior day's word before new word |

## 🔧 Configuration

All tunable parameters live in `AdminSetting` table, editable via admin UI:
- `quiz_enabled` (bool)
- `spice_selector_enabled` (bool)
- `reroll_cap` (int)
- `rare_chance` (float 0-1)
- `legendary_chance` (float 0-1)

## 📝 License

MIT — feel free to fork and customize for your own daily adventures.