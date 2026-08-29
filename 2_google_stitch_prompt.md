# Google Stitch prompt — DayRise Adventures

Paste everything below the line into Google Stitch as one prompt (or split by screen if Stitch works better with one screen per generation — the "Screens to generate" list is already broken into discrete units for that).

---

**Product:** DayRise Adventures — a daily habit-building app that gives the user one small, playful "quest" a day to break their routine (a dance break, a social nudge, a sensory exercise), plus a short daily ritual around it: a quick vibe check, a word-of-the-day with recall practice, and a streak you build over time. It's built and deployed as a Streamlit app, so the design should favor clean, componentized screens (cards, tabs, simple form inputs, progress indicators) over exotic custom interactions — think "polished internal tool" energy pushed toward "playful consumer app," not a fully custom animated experience.

**Tone:** Warm, a little mischievous, encouraging — like a friend daring you to do something small and fun, not a productivity app. Avoid corporate-SaaS blandness and avoid anything twee/childish.

**Design system to build from:**
- Typography: display/headline font similar to Poppins (bold, rounded geometric sans), body font similar to Inter.
- Base palette — Light mode: background `#f8fafc`, primary text `#1e293b`, secondary text `#64748b`, card background `#ffffff`, card border `#e2e8f0`. Accents: purple `#9c27b0`, coral `#ff4b4b`, cyan `#00b4d8`.
- Base palette — Dark mode: background `#0f172a`, primary text `#f1f5f9`, secondary text `#94a3b8`, card background `#1e293b`, card border `#334155`. Accents: purple `#d8b4fe`, coral `#fca5a5`, cyan `#7dd3fc`.
- Add one new accent for "legendary" rarity items: a warm gold/amber gradient, distinct from the three existing accents, used sparingly (a border treatment or a subtle glow, not a full-screen takeover).
- Cards: rounded corners (~16px), soft shadow, a colored top border or left border indicating category/rarity.
- Support both light and dark mode for every screen.
- Layout should read well both as a centered mobile-width column (~400px) and as a wider desktop layout — Streamlit renders wide by default, so don't assume a fixed narrow frame.

**Screens to generate:**

1. **Login / Signup** — a simple, friendly entry screen: username field, 4-digit PIN field, a toggle between "log in" and "create adventurer." No email field, no social login buttons.

2. **Vibe Check** — step 1 of the daily ritual. Three quick binary-choice taps (e.g. "Energetic ⚡ vs. Calm 🌙", "Solo 🧍 vs. Social 👥", "Indoors 🏠 vs. Outdoors 🌳") shown one at a time or all together, with a small progress indicator (1 of 3 / 2 of 3 / 3 of 3) at the top.

3. **Vocab Recall + New Word** — step 2. A small quiz card ("What does *Komorebi* mean?" with 3 answer options) followed, after answering, by a reveal card for today's new word: flag emoji, word, phonetic pronunciation, and meaning.

4. **Quest Reveal (locked state)** — a "locked" card with a mystery icon and a single call-to-action button to unlock today's quest, with a sense of anticipation (subtle glow, dashed border).

5. **Quest Reveal (unlocked state)** — the quest card itself: category tag, emoji, title, description, a small "assistance tip" callout below it. Include a variant showing the "legendary" rarity treatment described above.

6. **Ritual Complete summary** — a celebratory screen showing the current streak count, an optional milestone badge (e.g. "7-day streak!"), and a clear path into a secondary "Toolbox" area.

7. **Toolbox** — a lighter, secondary-feeling screen (accessible any time after the ritual) containing the "Destiny Coin Flip" widget (two labeled option cards with a flip button each) and a scrollable list/archive of past completed quests with dates.

8. **Admin dashboard** — a data-dense but still on-brand screen: summary stat cards across the top (total users, quests completed today, active streak leaders), and below them a simple data table view suitable for managing quest/vocab entries (add/edit/toggle-active). Use a slightly more neutral, utilitarian styling than the user-facing screens — this is a backstage view, it shouldn't compete visually with the main app, but it also shouldn't feel like a totally disconnected product.

**Interaction notes (for reference, not literal animation specs):** the unlock button in screen 4 should feel like it's building anticipation before revealing screen 5. Streak milestones should feel like a small reward moment, not a full-screen interruption. Keep the admin screens dense and scannable — this is used occasionally by one person, not daily by everyone.

**Deliverable:** export the screens (or a shareable Stitch link/Figma export) so they can be handed to a coding agent as a visual reference — the coding agent will be translating this into Streamlit's component model, so prioritize a clear, consistent design *system* (colors, spacing, card treatments, type scale) over pixel-perfect custom widgets that Streamlit can't natively reproduce.
