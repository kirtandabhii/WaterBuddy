"""
state.py - Everything WaterBuddy remembers, kept in st.session_state.

st.session_state is a dictionary that survives between button clicks
(Streamlit re-runs app.py from the top after every click). Nothing is
saved to a server or database, so the app stays private: closing or
refreshing the tab clears it.

The functions named on_... are "callbacks". Streamlit runs a callback
first when a button is clicked, then redraws the page, so the screen
always shows the newest numbers straight away.
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import streamlit as st

import content
import logic


# ---------------------------------------------------------------------------
# Time - use the visitor's own time zone, not the server's
# ---------------------------------------------------------------------------

def current_time():
    """
    The current time where the user is. Streamlit Cloud servers run on
    UTC, so we ask the browser for its time zone (st.context.timezone).
    """
    timezone_name = st.context.timezone
    if timezone_name:
        try:
            return datetime.now(ZoneInfo(timezone_name)).replace(tzinfo=None)
        except ZoneInfoNotFoundError:
            pass
    return datetime.now()


# ---------------------------------------------------------------------------
# Setting up the starting values
# ---------------------------------------------------------------------------

DEFAULT_AGE_GROUP = "Adults (19-50 yrs)"


def init_state():
    """Create every session_state key once, the first time the app runs."""
    defaults = {
        "age_group": DEFAULT_AGE_GROUP,
        "hot_day": False,
        "active_day": False,
        "goal_ml": logic.suggested_goal(DEFAULT_AGE_GROUP),
        "log": [],                 # today's drinks: list of dicts
        "celebrated": [],          # milestones already celebrated today
        "previous_percent": 0.0,   # bottle level last drawn (animation start)
        "pending_toasts": [],      # messages to pop up on the next redraw
        "pending_balloons": False,
        "warning": "",             # a problem with the last input
        "history": [],             # finished days (this session only)
        "day_number": 1,
        "tip_index": content.random_tip_index(-1),
        "wake_time": logic.default_wake_time(),
        "sleep_time": logic.default_sleep_time(),
        "custom_amount": 250.0,
        "custom_unit": "ml",
        "converter_cups": 1.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Small helpers that read the state
# ---------------------------------------------------------------------------

def get_total():
    return logic.total_intake(st.session_state.log)


def get_progress():
    return logic.calculate_progress(get_total(), st.session_state.goal_ml)


def get_suggested_goal():
    return logic.suggested_goal(st.session_state.age_group,
                                st.session_state.hot_day,
                                st.session_state.active_day)


# ---------------------------------------------------------------------------
# Callbacks for the goal section
# ---------------------------------------------------------------------------

def apply_suggested_goal():
    """
    Set the goal to the suggested amount. Runs when the age group or a
    day-type toggle changes, and when 'Use suggested goal' is clicked.
    """
    st.session_state.goal_ml = get_suggested_goal()


def on_goal_edited():
    """Manual goal typed in: keep it inside the safe range."""
    st.session_state.goal_ml = logic.clamp_goal(st.session_state.goal_ml)


# ---------------------------------------------------------------------------
# Callbacks for logging water
# ---------------------------------------------------------------------------

def add_water(amount_ml, label):
    """
    The heart of the app: validate, add a log entry, then check whether
    any milestone was just reached so we can celebrate it.
    """
    is_ok, problem = logic.validate_log_amount(amount_ml)
    if not is_ok:
        st.session_state.warning = problem
        return
    st.session_state.warning = ""

    old_percent = get_progress()["percent"]
    entry = logic.make_log_entry(amount_ml, label, current_time())
    st.session_state.log.append(entry)
    new_percent = get_progress()["percent"]

    # Celebrate milestones crossed by this drink (each only once per day).
    reached = logic.new_milestones_reached(old_percent, new_percent,
                                           st.session_state.celebrated)
    for milestone in reached:
        st.session_state.celebrated.append(milestone)
        st.session_state.pending_toasts.append(content.MILESTONE_TOASTS[milestone])
        if milestone == 100:
            st.session_state.pending_balloons = True


def on_add_glass():
    add_water(250, "Glass")


def on_add_bottle():
    add_water(500, "Bottle")


def on_add_custom():
    """Custom amount form: convert cups to ml first if needed."""
    amount = st.session_state.custom_amount
    if st.session_state.custom_unit == "cups":
        amount_ml = logic.cups_to_ml(amount)
    else:
        amount_ml = round(amount)
    add_water(amount_ml, "Custom")


def on_unit_change():
    """When the unit switches, convert the number so it means the same amount."""
    amount = st.session_state.custom_amount
    if st.session_state.custom_unit == "cups":
        st.session_state.custom_amount = logic.ml_to_cups(amount)
    else:
        st.session_state.custom_amount = float(logic.cups_to_ml(amount))


def on_undo_last():
    """Remove the most recent drink (for mis-taps)."""
    if not st.session_state.log:
        return
    st.session_state.log.pop()
    st.session_state.warning = ""
    # Allow a milestone to be celebrated again if we dropped below it.
    new_percent = get_progress()["percent"]
    st.session_state.celebrated = [m for m in st.session_state.celebrated
                                   if m <= new_percent]


def on_start_new_day():
    """
    Reset button: save today into the session's history, then clear
    today's log so the user starts fresh. The goal settings are kept.
    """
    if st.session_state.log:
        summary = logic.make_day_summary(st.session_state.day_number,
                                         st.session_state.log,
                                         st.session_state.goal_ml)
        st.session_state.history.append(summary)
        st.session_state.day_number += 1
    st.session_state.log = []
    st.session_state.celebrated = []
    st.session_state.warning = ""
    st.session_state.pending_toasts = [("🌊", "New day started - let's go!")]


def on_new_tip():
    st.session_state.tip_index = content.random_tip_index(st.session_state.tip_index)
