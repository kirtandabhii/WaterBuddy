"""
WaterBuddy - Your Daily Hydration Companion
==========================================
A Streamlit web app that helps people drink enough water each day.

How the code is organised:
    app.py      - the page layout (this file): what goes where on screen
    logic.py    - all calculations (goals, progress, milestones, pace)
    state.py    - st.session_state setup and the button callbacks
    visuals.py  - Boondi the mascot and the animated bottle (SVG)
    content.py  - messages, tips and other text

Run it with:  streamlit run app.py
"""

from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

import content
import logic
import state
import visuals

# st.set_page_config must be the first Streamlit command in the script.
st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="wide")

# A little extra styling: limit the page width, round the buttons and
# make the important numbers big and easy to read.
# Containers whose key starts with "row_" keep their columns side by side
# on phones too (Streamlit normally stacks columns on narrow screens).
st.markdown("""
<style>
.block-container { max-width: 1100px; padding-top: 2rem; }
.stButton button, .stPopover button { border-radius: 14px; font-weight: 700; min-height: 3rem; }
[data-testid="stMetricValue"] { font-size: 1.7rem; font-weight: 800; }
h1 { font-weight: 800 !important; }
[class*="st-key-row_"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.6rem; }
[class*="st-key-row_"] [data-testid="stColumn"] { min-width: 0 !important; flex: 1 1 0 !important; }
@media (max-width: 640px) {
  .block-container { padding-top: 1rem; }
  h1 { font-size: 2.1rem !important; }
  [data-testid="stMetricValue"] { font-size: 1.25rem; }
  [data-testid="stMetricLabel"] p { font-size: 0.8rem; }
  .stButton button p, .stPopover button p { font-size: 0.9rem; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page sections - each one is its own function so the layout is easy to follow
# ---------------------------------------------------------------------------

def show_header(now):
    """Title, greeting and today's date."""
    st.title("💧 WaterBuddy")
    st.markdown(f"**{content.greeting(now.hour)}!** Let's keep you hydrated today "
                f"· {now.strftime('%A, %d %B')}")


def show_goal_section():
    """Stage 4: age group, auto-suggested goal and manual adjustment."""
    # Open at the start so new users set their age first. The user can fold
    # it away with one tap; the label never changes, so Streamlit remembers
    # that choice and the buttons below never jump around unexpectedly.
    goal = st.session_state.goal_ml
    with st.expander("🎯 Your daily goal · tap to hide or show", expanded=True):
        left, right = st.columns(2)

        with left:
            st.selectbox("Age group", options=list(logic.AGE_GROUPS),
                         key="age_group", on_change=state.apply_suggested_goal,
                         help="We suggest a goal based on health guidelines for your age.")
            st.toggle(f"☀️ Hot day (+{logic.HOT_DAY_EXTRA_ML} ml)", key="hot_day",
                      on_change=state.apply_suggested_goal)
            st.toggle(f"🏃 Active day / exercise (+{logic.ACTIVE_DAY_EXTRA_ML} ml)",
                      key="active_day", on_change=state.apply_suggested_goal)

        with right:
            st.number_input("Your goal for today (ml) - change it if you like",
                            min_value=logic.MIN_GOAL_ML, max_value=logic.MAX_GOAL_ML,
                            step=50, key="goal_ml", on_change=state.on_goal_edited)

            # Optional idea from the brief: standard target vs user goal side by side.
            standard = logic.standard_goal(st.session_state.age_group)
            difference = goal - standard
            with st.container(key="row_compare"):
                col_a, col_b = st.columns(2)
                col_a.metric("Age standard", f"{standard:,} ml")
                col_b.metric("Your goal", f"{goal:,} ml",
                             delta=f"{difference:+,} ml" if difference else None)

            if goal != state.get_suggested_goal():
                st.button(f"↩️ Use suggested goal ({state.get_suggested_goal():,} ml)",
                          on_click=state.apply_suggested_goal)


def show_mascot_and_bottle(progress):
    """Stage 5: Boondi and the bottle react to the current percentage."""
    percent = progress["percent"]
    mood = logic.get_mood(percent)
    message = content.get_mascot_message(mood, st.session_state.age_group)

    st.markdown(visuals.hero_html(mood, percent, st.session_state.previous_percent,
                                  message, content.MASCOT_NAME),
                unsafe_allow_html=True)

    # Remember the level we just drew so the next change animates from here.
    st.session_state.previous_percent = percent


def show_stats(progress, now):
    """The three key numbers, the progress bar and the pace check."""
    total = progress["total"]
    with st.container(key="row_stats"):
        col1, col2, col3 = st.columns(3)
    col1.metric("Drunk", f"{total:,} ml",
                help=f"That's about {logic.ml_to_cups(total):g} glasses of 250 ml.")
    if progress["extra"] > 0:
        col2.metric("Above goal", f"+{progress['extra']:,} ml")
    else:
        col2.metric("To go", f"{progress['remaining']:,} ml")
    col3.metric("Achieved", f"{progress['percent']:.0f}%")

    st.progress(logic.progress_bar_value(progress["percent"]),
                text=f"{total:,} / {st.session_state.goal_ml:,} ml")

    # Pace check: compare with where you'd ideally be at this time of day.
    expected = logic.expected_percent_now(now, st.session_state.wake_time,
                                          st.session_state.sleep_time)
    status = logic.pace_status(progress["percent"], expected)
    icon, text = content.PACE_MESSAGES[status]
    if expected is not None and status != "done":
        text += f" (ideal by {now.strftime('%H:%M')}: about {expected:.0f}%)"
    st.caption(f"{icon} **Pace:** {text}")


def show_logging_controls(now):
    """Stage 4: quick +250 ml button, other amounts, undo and reset."""
    with st.container(key="row_log"):
        col1, col2 = st.columns(2)
    col1.button("🥛 +250 ml  (glass)", on_click=state.on_add_glass,
                type="primary", width="stretch")
    col2.button("🍶 +500 ml  (bottle)", on_click=state.on_add_bottle,
                width="stretch")

    with st.expander("✏️ Log a different amount"):
        amount_col, unit_col = st.columns([2, 1])
        unit = st.session_state.custom_unit
        amount_col.number_input(f"Amount ({unit})", min_value=0.0,
                                step=50.0 if unit == "ml" else 0.5,
                                key="custom_amount")
        unit_col.radio("Unit", ["ml", "cups"], key="custom_unit",
                       on_change=state.on_unit_change, horizontal=True)
        st.button("➕ Add this amount", on_click=state.on_add_custom, width="stretch")

    # Any problem with the last input is shown here (e.g. 0 ml or too much).
    if st.session_state.warning:
        st.warning(st.session_state.warning, icon="⚠️")

    # Safety note if a lot was logged very quickly.
    last_hour = logic.intake_in_last_hour(st.session_state.log, now)
    if last_hour > logic.FAST_DRINKING_LIMIT_ML:
        st.info(f"You've logged {last_hour:,} ml in the last hour. Your kidneys "
                "can only clear about 0.8-1 litre an hour, so slow down a little.",
                icon="🐢")

    with st.container(key="row_undo"):
        undo_col, reset_col = st.columns(2)
    undo_col.button("↩️ Undo last drink", on_click=state.on_undo_last,
                    disabled=len(st.session_state.log) == 0, width="stretch")
    with reset_col.popover("🔄 Start a new day", width="stretch"):
        st.write("This clears today's drinks and saves today's total to "
                 "**This week**. Your goal settings stay the same.")
        st.button("Yes, start fresh", on_click=state.on_start_new_day,
                  type="primary", key="reset_confirm")


def make_timeline_chart(now):
    """Line chart of water drunk through the day vs the ideal pace."""
    today = now.date()
    wake = datetime.combine(today, st.session_state.wake_time)
    sleep = datetime.combine(today, st.session_state.sleep_time)
    goal = st.session_state.goal_ml

    # Your actual intake: a running total that steps up after each drink.
    you_rows = [{"time": min(wake, st.session_state.log[0]["time"]), "ml": 0}]
    running_total = 0
    for entry in st.session_state.log:
        running_total += entry["amount_ml"]
        you_rows.append({"time": entry["time"], "ml": running_total})
    you_rows.append({"time": max(now, you_rows[-1]["time"]), "ml": running_total})

    x_axis = alt.X("time:T", title=None, axis=alt.Axis(format="%H:%M"))
    you_line = alt.Chart(pd.DataFrame(you_rows)).mark_line(
        interpolate="step-after", strokeWidth=3, color="#0EA5C6").encode(
        x=x_axis, y=alt.Y("ml:Q", title="ml"))

    # Orange line = the goal.
    goal_line = alt.Chart(pd.DataFrame({"ml": [goal]})).mark_rule(
        color="#F59E0B", strokeWidth=2).encode(y="ml:Q")

    chart = you_line + goal_line

    # Grey dashed line = ideal pace, straight from 0 at wake-up to the goal at bedtime.
    if sleep > wake:
        ideal_rows = [{"time": wake, "ml": 0}, {"time": sleep, "ml": goal}]
        ideal_line = alt.Chart(pd.DataFrame(ideal_rows)).mark_line(
            strokeDash=[6, 4], strokeWidth=2, color="#94A3B8").encode(x=x_axis, y="ml:Q")
        chart = ideal_line + chart

    return chart.properties(height=280)


def show_today_tab(now):
    """Chart and table of today's drinks."""
    if not st.session_state.log:
        st.info("No drinks logged yet today. Tap **+250 ml** to start! "
                "Your timeline will appear here.", icon="🫗")
        return
    st.altair_chart(make_timeline_chart(now), width="stretch")
    st.caption("Blue = what you drank · grey dashed = ideal steady pace · orange = goal")

    table = pd.DataFrame([{"Time": e["time"].strftime("%H:%M"),
                           "Drink": e["label"],
                           "Amount (ml)": e["amount_ml"]}
                          for e in reversed(st.session_state.log)])
    st.dataframe(table, hide_index=True, width="stretch")


def show_end_of_day_tab(progress):
    """Optional idea from the brief: an end-of-day summary."""
    log = st.session_state.log
    if not log:
        st.info("Your summary appears once you've logged a drink.", icon="🌙")
        return

    if progress["percent"] >= 100:
        st.success("### 🎉 Great job today! You reached your goal.")
    elif progress["percent"] >= 50:
        st.info(f"### 💪 Good effort - {progress['percent']:.0f}% of your goal.")
    else:
        st.warning(f"### 🌱 {progress['percent']:.0f}% today - tomorrow is a fresh start.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", f"{progress['total']:,} ml")
    col2.metric("Drinks logged", len(log))
    col3.metric("Glasses (250 ml)", f"{logic.ml_to_cups(progress['total']):g}")

    badges = logic.earned_badges(log, progress["total"], st.session_state.goal_ml)
    if badges:
        st.markdown("**Badges earned today**")
        for emoji, name, reason in badges:
            st.markdown(f"{emoji} **{name}** - {reason}")
    else:
        st.caption("Keep going to earn badges like 🏆 Goal Getter and 🔁 Steady Sipper.")

    st.button("🔄 Finish today & start a new day", on_click=state.on_start_new_day,
              key="reset_from_summary")


def show_week_tab(progress):
    """Days finished in this session, plus today so far."""
    days = list(st.session_state.history)
    days.append({"day": f"Day {st.session_state.day_number} (today)",
                 "total_ml": progress["total"], "goal_ml": st.session_state.goal_ml,
                 "percent": progress["percent"], "drinks": len(st.session_state.log)})

    data = pd.DataFrame(days)
    data["reached"] = data["percent"].apply(lambda p: "Goal reached" if p >= 100 else "Below goal")
    bars = alt.Chart(data).mark_bar(size=48, cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("day:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("total_ml:Q", title="ml"),
        color=alt.Color("reached:N", title=None,
                        scale=alt.Scale(domain=["Goal reached", "Below goal"],
                                        range=["#0EA5C6", "#93C5D6"]),
                        legend=alt.Legend(orient="top")),
        tooltip=["day", "total_ml", "goal_ml", "percent"],
    )
    st.altair_chart(bars.properties(height=260), width="stretch")

    days_hit = sum(1 for d in st.session_state.history if d["percent"] >= 100)
    st.caption(f"Finished days this session: {len(st.session_state.history)} · "
               f"goal reached on {days_hit}. Data lives only in this browser tab "
               "and disappears when you close it - nothing is stored anywhere.")


def show_sidebar(now):
    """Tips, converter, day settings and the mascot guide."""
    with st.sidebar:
        st.header("💡 Tip of the moment")
        st.info(content.TIPS[st.session_state.tip_index])
        st.button("Another tip", on_click=state.on_new_tip)

        st.divider()
        st.header("🔁 Cups ↔ ml")
        st.number_input("Cups", min_value=0.0, max_value=40.0, step=0.5,
                        key="converter_cups")
        cups = st.session_state.converter_cups
        st.markdown(f"**{cups:g} cups = {logic.cups_to_ml(cups):,} ml**")
        st.caption(f"1 cup = 1 glass = {logic.ML_PER_CUP} ml")

        st.divider()
        st.header("⏰ My day")
        st.time_input("I usually wake up at", key="wake_time", step=1800)
        st.time_input("I usually go to bed at", key="sleep_time", step=1800)
        if st.session_state.sleep_time <= st.session_state.wake_time:
            st.warning("Bedtime should be later than wake-up time for the pace check.")

        st.divider()
        st.header(f"💧 How {content.MASCOT_NAME} feels")
        st.markdown(
            "- 0% · 😩 thirsty and droopy\n"
            "- 1-24% · 🙂 waking up\n"
            "- 25-49% · 😊 smiling\n"
            "- 50-74% · 😄 happy wave\n"
            "- 75-99% · 🤩 excited sparkles\n"
            "- 100-149% · 🥳 party time\n"
            "- 150%+ · 😌 full - drink to thirst"
        )
        st.caption("Tip: switch light/dark mode from the ⋮ menu → Settings.")
        st.caption("🔒 Private by design: no login, no database. "
                   "Everything stays in this browser tab.")


def show_pending_feedback():
    """Pop up any milestone toasts or balloons queued by the callbacks."""
    for icon, message in st.session_state.pending_toasts:
        st.toast(message, icon=icon)
    st.session_state.pending_toasts = []
    if st.session_state.pending_balloons:
        st.balloons()
        st.session_state.pending_balloons = False


# ---------------------------------------------------------------------------
# Main program - runs from top to bottom on every click
# ---------------------------------------------------------------------------

def main():
    state.init_state()
    now = state.current_time()
    progress = state.get_progress()   # total, remaining, percent, extra

    show_header(now)
    show_goal_section()

    st.write("")
    hero_col, controls_col = st.columns([5, 6], gap="large")
    with hero_col:
        show_mascot_and_bottle(progress)
    with controls_col:
        show_stats(progress, now)
        show_logging_controls(now)

    st.write("")
    today_tab, summary_tab, week_tab = st.tabs(["📈 Today", "🌙 End of day", "📅 This week"])
    with today_tab:
        show_today_tab(now)
    with summary_tab:
        show_end_of_day_tab(progress)
    with week_tab:
        show_week_tab(progress)

    show_sidebar(now)
    show_pending_feedback()


main()
