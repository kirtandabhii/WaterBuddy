# 💧 WaterBuddy – Your Daily Hydration Companion

WaterBuddy is a small Streamlit web app that helps you drink enough water each day.
Pick your age group and it suggests a daily goal. Log each glass with one tap.
**Boondi**, a little water-drop mascot, reacts as your bottle fills up.

*Python Programming – Formative Assessment 2 (CRS, Artificial Intelligence, Year 1).*

## Features

| Brief requirement | How WaterBuddy does it |
|---|---|
| Age group selector | Kids 6-12, Teens 13-18, Adults 19-50, Adults 51-64, Seniors 65+ |
| Auto-suggested goal + manual adjust | Goal comes from the age group (plus optional *hot day* / *active day* extras). You can type your own goal, and **Use suggested goal** puts it back |
| Quick log | **+250 ml glass** and **+500 ml bottle** buttons, plus any amount in ml or cups |
| Reset for a new day | **Start a new day** (with a confirm step) saves today to *This week* and clears the log |
| Total, remaining, % achieved | Three live numbers, worked out again after every tap |
| Progress bar / animated bottle | A progress bar and an SVG bottle whose water rises to the new level |
| Mascot reacts at milestones | Boondi has 7 moods (0%, 1-24, 25-49, 50-74, 75-99, 100-149, 150%+), with pop-up messages at 25/50/75/100% and balloons at 100% |
| Optional ideas | Standard vs your goal side by side, cups ↔ ml converter, random tips, age-aware messages, end-of-day summary with badges, light/dark themes, "pace" check for the time of day, timeline chart, a *drinking too fast* safety note |

Everything is kept in `st.session_state`. There is no login, no database and there are no API keys.
Your data stays in your browser tab and is gone when you close it.

## Project structure

```
app.py            Page layout - the entry point Streamlit runs
logic.py          All calculations (goals, progress, moods, milestones, pace, badges)
state.py          session_state setup + button callbacks
visuals.py        Boondi the mascot and the animated bottle, drawn as SVG
content.py        Messages, tips and other text
tests/            Unit tests for logic.py and end-to-end tests for app.py
.streamlit/config.toml   Theme (aqua colours, Nunito font, light + dark)
requirements.txt  Python packages, with pinned versions
```

## Run it on your computer

You need Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

To run the tests:

```bash
python -m unittest discover tests
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a **public** GitHub repository (e.g. `WaterBuddy`).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Pick the repository, branch `main` and main file path `app.py`.
5. Open **Advanced settings** and choose **Python 3.12**.
6. Click **Deploy**. A minute or two later you get a public `*.streamlit.app` URL.

## Why no Turtle or Tkinter?

The brief mentions Turtle graphics and Tkinter pop-ups as optional ideas. Both need a
desktop window, and Streamlit Cloud runs on a server that has no screen, so they would crash there.
WaterBuddy does the same jobs in the browser:

- Boondi is drawn by Python functions that build SVG shapes. It works like Turtle, but the result shows in a web page.
- Reminders appear as `st.toast` pop-ups instead of Tkinter windows.
