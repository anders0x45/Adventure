# Coding agent prompt — build DayRise Adventures v2

Paste this into your coding agent (e.g. Claude Code) inside a clone of the `Adventure` repo, with `1_implementation_plan.md` and the Google Stitch design export both placed in the repo root (or otherwise accessible in context) before running it.

---

You are working in the `Adventure` repo — a Streamlit app currently implemented as a single file, `myapp.py`. Your job is to rebuild it into the persistent, multi-user version described in `1_implementation_plan.md`, using the visual design reference exported from Google Stitch (attached as images / a Figma link / an HTML export — check the repo root and this conversation for whichever form it's in).

## Inputs to read first

1. Read `myapp.py` in full — this is the current working app and the source of truth for existing quest text, vocab entries, copy tone, and behavior that must not regress.
2. Read `1_implementation_plan.md` in full — this is your spec. Follow its phase order, file structure, data model, and acceptance criteria exactly unless something in it is genuinely inconsistent with itself, in which case use your judgment and note the deviation in your final summary.
3. Review the Stitch design export contained in the `design` folder — treat it as the visual system to translate, not a literal template. Streamlit cannot render arbitrary custom HTML/JS components as freely as a hand-built frontend, so:
   - Extract the **design system** from it: exact/approximate colors, type scale, card treatments, spacing rhythm, and the rarity/legendary accent — and implement those faithfully via Streamlit's custom-CSS injection (the existing app already does this; extend the same pattern in `core/theme.py`).
   - Do **not** attempt pixel-perfect reproduction of layouts that Streamlit's component model can't natively support (e.g. exotic custom animations, non-standard input controls). Approximate the *feel* with what's actually available: `st.container`, `st.columns`, `st.tabs`, `st.data_editor`, custom CSS on markdown blocks, and `time.sleep`-based reveal delays for the "unlock" moment.
   - If a screen in the Stitch export implies an interaction Streamlit genuinely cannot do well, pick the closest reasonable Streamlit-native equivalent and move on — don't get stuck trying to force it.

## Build order

Follow the phase order in the implementation plan: persistence → auth → Daily Ritual flow → quizzes → fun mechanics → admin view → theming refactor → deployment polish → tests. After each phase, run the app locally (`streamlit run app.py`) and confirm that phase's acceptance criteria from the plan hold before moving to the next one. Don't wait until the very end to test — verify incrementally.

## Hard requirements

- The finished app must run with `streamlit run app.py` from a clean clone, needing only `pip install -r requirements.txt` and a filled-in `.streamlit/secrets.toml` (based on the `.example` file you create).
- Default persistence is SQLite via SQLAlchemy, with `DATABASE_URL` in `st.secrets` as an override — no model code should assume one or the other.
- Every existing quest, vocab entry, and piece of copy tone from `myapp.py` must be preserved (ported into seed data), not silently dropped or rewritten in a different voice.
- The admin view must be genuinely gated by `st.secrets["admin_passcode"]` — don't leave it reachable without it, even during development (use a placeholder passcode in the example secrets file).
- `requirements.txt` versions must be pinned, not left bare.
- Keep the reroll cap, streak milestones, spice levels, and rarity system all admin-configurable via the `AdminSetting` table as specified in the plan — don't hardcode values that the plan says should be adjustable.

## What "done" looks like

- A working multipage Streamlit app (`app.py` + `pages/1_🔐_Admin.py`) deployable as-is to Streamlit Community Cloud.
- A README covering what the app does, a screenshot or two, local setup, and the Postgres-swap note for production persistence, as specified in the plan's deployment phase.
- The two test files from the plan, passing.
- A short final summary to me listing: any deviations you made from the plan and why, any part of the Stitch design you couldn't faithfully reproduce in Streamlit and what you substituted instead, and anything you'd flag as a good next step but deliberately left out of scope.

If something in the plan is ambiguous enough that guessing wrong would mean rework (not just a minor judgment call), ask me before proceeding on that specific piece — otherwise, use your best judgment and keep moving; I'd rather review a complete, working app with a few noted assumptions than get interrupted repeatedly for small decisions.
