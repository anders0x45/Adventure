# DayRise Adventures — Implementation Plan

**Target repo:** `meklitermias38-max/Adventure` (currently a single-file Streamlit app, `myapp.py`)
**Goal:** Turn the app from a session-only demo into a persistent, multi-user Streamlit app with a guided daily flow, light quiz mechanics, an admin view, and enough "game feel" to make it worth opening every day — without scope-creeping into a full platform (no OAuth, no native mobile app, no payments, no push notifications in v1).

---

## 0. Architecture overview

**Stack:** Streamlit + SQLAlchemy + SQLite (default), swappable to a hosted Postgres via a connection string. No new frontend framework — all UI stays in Streamlit, styled with the existing custom-CSS approach.

**Why SQLAlchemy over raw SQLite calls:** Streamlit Community Cloud's filesystem is not guaranteed to persist across app restarts/redeploys (the container can be recycled). Building on SQLAlchemy from day one means swapping `sqlite:///dayrise.db` for a hosted Postgres URL (e.g. a free Supabase or Neon instance) is a one-line change in `st.secrets`, with zero model code changes. **Ship v1 on SQLite for local dev and demo purposes, but document the Postgres swap clearly in the README so real persistence in production is a config change, not a rewrite.**

**New file structure:**

```
Adventure/
├── app.py                      # renamed from myapp.py — the Daily Ritual entrypoint
├── pages/
│   └── 1_🔐_Admin.py            # Streamlit multipage admin view
├── core/
│   ├── __init__.py
│   ├── db.py                   # engine/session setup, st.cache_resource
│   ├── models.py                # SQLAlchemy models
│   ├── seed_data.py             # ports the existing hardcoded quest/vocab banks into DB rows
│   ├── auth.py                  # username + PIN login/signup helpers
│   ├── quests.py                # selection, weighting, rarity, reroll-cap logic
│   ├── vocab.py                 # vocab bank + recall-quiz logic
│   ├── streaks.py               # streak calculation, milestone/badge logic
│   └── theme.py                 # CSS/theme constants, pulled out of app.py
├── .streamlit/
│   ├── secrets.toml.example
│   └── config.toml
├── requirements.txt             # pinned versions
├── README.md
└── tests/
    ├── test_quests.py
    └── test_streaks.py
```

---

## 1. Data model

Define in `core/models.py` using SQLAlchemy declarative models.

```
User
  id, username (unique, indexed), pin_hash, adventurer_name, prefix, suffix,
  theme_preference ("light"/"dark"), spice_level ("mild"/"spicy"/"unhinged"),
  created_at

Preference               # the "This or That" dilemma matrix, now per-user rows not a tuple list
  id, user_id (FK), axis_index (0 or 1), option_a, option_b

Quest
  id, title, desc, category, emoji, assistance_text,
  day_type ("weekday"/"weekend"/"both"),
  rarity ("common"/"rare"/"legendary"), spice_level ("mild"/"spicy"/"unhinged"),
  active (bool, default True), created_by_admin (bool), created_at

QuestCompletion
  id, user_id (FK), quest_id (FK), completed_at (datetime), completion_date (date, indexed)

Vocab
  id, language, flag, word, meaning, pronunciation, active (bool)

VocabSeen                 # tracks which word was shown to which user on which day, for recall quiz
  id, user_id (FK), vocab_id (FK), shown_on (date)

QuizAttempt
  id, user_id (FK), quiz_type ("vocab_recall"/"vibe_check"), question_ref,
  was_correct (bool, nullable — vibe_check has no right answer), answered_at

DailySession               # tracks a user's progress through today's Daily Ritual
  id, user_id (FK), session_date (date, indexed),
  vibe_check_done (bool), vocab_recall_done (bool),
  quest_id (FK, nullable), quest_completed (bool), reroll_count (int, default 0),
  spice_level_selected

AdminSetting                # simple key/value feature-flag store
  key (str, primary key), value (str)
```

Seed `AdminSetting` with defaults on first run: `quiz_enabled=true`, `spice_selector_enabled=true`, `reroll_cap=1`, `legendary_chance=0.05`, `rare_chance=0.20`.

**Acceptance criteria:** `core/db.py` creates all tables on first import if they don't exist (`Base.metadata.create_all`). `core/seed_data.py` is idempotent — running it twice doesn't duplicate quests/vocab. The 8 weekday quests, 4 weekend quests, and 4 vocab entries from the current `myapp.py` are ported in as the initial seed rows (tag them `common` rarity, `mild` spice, so nothing regresses on day one).

---

## 2. Lightweight auth

Replace "type any name to log in" with a real account, but keep it simple — **no email, no OAuth, no password-reset flow.**

- Signup: username + 4-digit PIN. Hash the PIN (e.g. `hashlib.sha256` with a per-user salt — this is a hobby app, not a bank, so keep the crypto proportionate but never store the PIN in plaintext).
- Login: username + PIN, checked against `pin_hash`.
- Session persists only for the current browser session via `st.session_state` (Streamlit has no reliable built-in persistent cookie without an extra component) — user re-enters their PIN on a fresh browser session, but **their data (streak, archive, preferences) is now preserved in the DB regardless**, which is the actual problem being solved.
- On first login, generate the adventurer name (prefix/suffix) exactly as today, but check uniqueness against the `User` table globally, not against a per-session list — this fixes the existing bug where the "no duplicate names" logic silently did nothing.

**Acceptance criteria:** Closing and reopening the browser loses the *logged-in session* but not the *data* — logging back in with the same username/PIN restores streak, archive, and preferences exactly as they were.

---

## 3. The Daily Ritual (unifying feature)

This is the feature that ties persistence, quizzes, and quest selection into one coherent flow, replacing today's flat stack of independent sections.

**Concept:** each day, the app walks the user through a short sequence instead of dumping every module on one page at once. Progress through the sequence is stored in `DailySession` so a refresh resumes where the user left off instead of restarting.

**Steps:**

1. **Vibe Check** — 3 quick tap questions (energetic vs. calm / alone vs. social / indoors vs. outdoors). Logged as `QuizAttempt(quiz_type="vibe_check")` rows (no right/wrong, just signal). Result: a weighting vector used in quest selection, and a suggested default `spice_level` for the day (user can override).
2. **Vocab Recall + New Word** — if a `VocabSeen` row exists from a prior day that hasn't been quizzed yet, show a 1-question multiple-choice recall quiz first ("What does *Komorebi* mean?" with 2 wrong meanings pulled from other vocab rows as distractors). Then reveal today's new word and log it as `VocabSeen`.
3. **Quest Reveal** — a short "unlocking" animation (2–3 second delay, reuse the existing locked-card UI as the "before" state), then reveal a quest selected by weighted-random draw (see §5 for weighting logic), respecting the day's spice level and the rarity roll.
4. **Complete or Reroll** — same as today, but rerolls are capped per `AdminSetting.reroll_cap` (default 1/day) to preserve the "get out of your comfort zone" intent. Completing logs a `QuestCompletion` row and updates `DailySession.quest_completed`.
5. **Ritual Complete** — a summary screen: today's streak count, any milestone reached, and a transition into the **Toolbox** — the Destiny Coin Flip and the completed-archive view, which remain available as standalone utilities for the rest of the day (not part of the sequential steps, since they're used ad hoc, not once daily).

**Acceptance criteria:** A user who completes step 1, refreshes the page, and comes back sees step 2, not step 1 again. A user who already completed today's full ritual sees a "you're done for today" summary screen instead of being able to redo it (aside from the Toolbox, which stays open).

---

## 4. Quizzes

Both quiz types are folded into the Daily Ritual above, not a separate "quiz tab" — a standalone trivia section was considered and deliberately rejected because it doesn't reinforce anything else the app does (see design rationale below if asked). Implement:

- **Vocab recall quiz** (`core/vocab.py`): pulls the most recent unquizzed `VocabSeen` row for the user, builds a 3-option multiple choice (1 correct + 2 distractor meanings from other active `Vocab` rows), records the attempt, shows immediate feedback.
- **Vibe check** (`core/quests.py`): 3 binary taps, no persistence needed beyond the `QuizAttempt` log and the resulting weight vector held in `DailySession` for the day.

**Acceptance criteria:** Recall quiz never repeats the same word twice for the same user, and correctly handles the case where a user has no prior `VocabSeen` row yet (skip straight to new-word reveal on day 1).

---

## 5. Fun mechanics (not extreme — additive, not a redesign)

- **Weighted quest selection:** instead of pure `random.choice`, weight candidate quests by (a) matching the day's spice level, (b) a small boost toward categories favored in the vibe check, and (c) a rarity roll (`common` by default; `AdminSetting.rare_chance` / `legendary_chance` govern the odds of upgrading the draw to a rare/legendary-tagged quest if any are active). Legendary quests get distinct card styling (e.g. a gold border/gradient).
- **Reroll cap:** enforced via `DailySession.reroll_count` against `AdminSetting.reroll_cap`.
- **Streak milestones:** compute current streak in `core/streaks.py` from consecutive `completion_date` rows. At 3, 7, and 30 days, trigger a distinct celebration (bigger `st.balloons()`/`st.snow()` combo, a badge line in the Ritual Complete summary) instead of the same animation every time.
- **Spice level selector:** `mild` / `spicy` / `unhinged`, defaulting to the vibe-check suggestion, overridable by the user, filters the quest candidate pool.

**Acceptance criteria:** A fresh user with no completions has a `current_streak` of 0 and no milestone triggers false-positive. Rerolling past the cap disables the reroll button with a short explanatory caption rather than silently failing.

---

## 6. Admin view

New Streamlit multipage file: `pages/1_🔐_Admin.py`. Gated by a passcode stored in `st.secrets["admin_passcode"]`, checked via a simple `st.text_input(type="password")` at the top of the page before rendering anything else.

**Sections (use `st.tabs`):**

1. **Dashboard** — total users, quests completed today / this week, a small streak leaderboard (top 5 by current streak), most-picked category, most-rerolled quest, recall-quiz accuracy rate. All read-only aggregate queries.
2. **Quest Manager** — `st.data_editor` bound to the `Quest` table: add, edit, deactivate (soft-delete via `active=False`, never hard-delete rows that have completion history), set category/day_type/rarity/spice_level per quest.
3. **Vocab Manager** — same CRUD pattern for the `Vocab` table.
4. **Feature Flags** — toggles/sliders bound to `AdminSetting`: quiz on/off, spice selector on/off, reroll cap, rare/legendary chance.
5. **User Lookup** — search by username, view (read-only) their streak, archive, and preferences; a "reset PIN" action for support purposes.

**Acceptance criteria:** The admin page is unreachable without the correct passcode (wrong or blank passcode renders nothing but the passcode prompt). Editing a quest or flag in the admin view is reflected immediately for users on their next quest draw, without needing an app restart.

---

## 7. Theming refactor

Move the CSS block and light/dark color constants out of `app.py` into `core/theme.py` as a function `get_theme(mode: str) -> dict`, returning the color dict currently hardcoded inline. `app.py` and the admin page both import from here so styling stays consistent across pages. No visual redesign in this phase — that's driven by the Stitch output, layered in during the coding-agent pass.

---

## 8. Deployment

- Pin `requirements.txt`: `streamlit==<current-stable>`, `sqlalchemy==<current-stable>`.
- Add `.streamlit/secrets.toml.example` documenting `admin_passcode` and optional `DATABASE_URL` (falls back to local SQLite if unset).
- README additions: what the app does, screenshot/GIF, local run instructions (`streamlit run app.py`), how to deploy to Streamlit Community Cloud, and an explicit callout that production deployments needing durable persistence should set `DATABASE_URL` to a hosted Postgres instance rather than relying on the default SQLite file.

**Acceptance criteria:** `streamlit run app.py` works from a clean clone with only `pip install -r requirements.txt` and a filled-in `secrets.toml`.

---

## 9. Testing

Not a full test suite — just enough to protect the logic that's easy to get subtly wrong:

- `tests/test_quests.py` — weighted selection respects spice-level filtering; rarity roll probabilities are approximately correct over many trials; reroll cap is enforced.
- `tests/test_streaks.py` — streak calculation across consecutive days, a gap day (streak resets), and same-day double-completion (doesn't double-count).

---

## Suggested execution order

Phases 1 → 2 → 3 are sequential (persistence must exist before auth, auth before the ritual can be per-user). Phases 4 and 5 can be built in parallel once phase 3 exists. Phase 6 (admin) can start as soon as phase 1's models exist, in parallel with 3–5. Phase 7 (theming) and 8 (deployment) come last, once the UI shape is stable enough to skin.

## Explicit non-goals for this pass

No OAuth/social login, no native mobile app or PWA push notifications, no payments, no LLM-generated quests (flagged as a good *future* idea, not in this plan), no multi-language UI. Keep these out unless asked for separately — the goal here is a working, persistent, admin-manageable app, not a platform.
