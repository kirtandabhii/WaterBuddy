"""
logic.py - All of WaterBuddy's calculations.

Every function in this file is "pure": it only uses the values passed in
and returns a result. It never touches Streamlit, so each function can be
tested on its own (see tests/test_logic.py).
"""

from datetime import time, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Recommended daily water from drinks, in millilitres, for each age group.
# Based on EFSA (2010) adequate intakes and the ESPEN (2022) geriatric
# guideline - see STORYBOARD_NOTES.md section 4 for the full reasoning.
AGE_GROUPS = {
    "Kids (6-12 yrs)": 1600,
    "Teens (13-18 yrs)": 2000,
    "Adults (19-50 yrs)": 2500,
    "Adults (51-64 yrs)": 2500,
    "Seniors (65+ yrs)": 2000,
}

HOT_DAY_EXTRA_ML = 500      # extra water suggested on a hot day
ACTIVE_DAY_EXTRA_ML = 500   # extra water suggested on an exercise day

ML_PER_CUP = 250            # one cup / glass = 250 ml (metric cup)

MIN_GOAL_ML = 500           # smallest goal a user may set
MAX_GOAL_ML = 6000          # largest goal a user may set
MAX_SINGLE_LOG_ML = 2000    # largest amount accepted in one log entry

# Milestones that trigger a celebration message (percent of goal).
MILESTONES = [25, 50, 75, 100]

# If someone logs more than this within one hour, we show a gentle caution.
# Healthy kidneys can only clear roughly 0.8-1.0 litre per hour.
FAST_DRINKING_LIMIT_ML = 1000


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

def standard_goal(age_group):
    """Return the standard daily goal (ml) for an age group."""
    return AGE_GROUPS[age_group]


def suggested_goal(age_group, hot_day=False, active_day=False):
    """Standard goal plus any extra water for a hot or active day."""
    goal = standard_goal(age_group)
    if hot_day:
        goal = goal + HOT_DAY_EXTRA_ML
    if active_day:
        goal = goal + ACTIVE_DAY_EXTRA_ML
    return goal


def clamp_goal(goal_ml):
    """Keep a goal inside the allowed range (protects against odd input)."""
    return max(MIN_GOAL_ML, min(MAX_GOAL_ML, int(goal_ml)))


# ---------------------------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------------------------

def cups_to_ml(cups):
    """Convert cups to millilitres (rounded to a whole number)."""
    return round(cups * ML_PER_CUP)


def ml_to_cups(ml):
    """Convert millilitres to cups (rounded to one decimal place)."""
    return round(ml / ML_PER_CUP, 1)


# ---------------------------------------------------------------------------
# Logging validation
# ---------------------------------------------------------------------------

def validate_log_amount(amount_ml):
    """
    Check a single amount before it is logged.
    Returns (is_ok, message). The message explains any problem.
    """
    if amount_ml <= 0:
        return False, "Please enter an amount above 0 ml."
    if amount_ml > MAX_SINGLE_LOG_ML:
        return False, (f"That's more than {MAX_SINGLE_LOG_ML} ml at once. "
                       "Please log big amounts in smaller parts.")
    return True, ""


# ---------------------------------------------------------------------------
# Progress calculations
# ---------------------------------------------------------------------------

def total_intake(log):
    """Add up every amount in today's log (a list of dicts)."""
    total = 0
    for entry in log:
        total = total + entry["amount_ml"]
    return total


def calculate_progress(total_ml, goal_ml):
    """
    The three core numbers WaterBuddy shows.
    Returns a dict with total, remaining, percent and extra (above goal).
    """
    if goal_ml <= 0:
        # Should never happen (goal is clamped) but avoids dividing by zero.
        return {"total": total_ml, "remaining": 0, "percent": 0.0, "extra": 0}

    remaining = max(goal_ml - total_ml, 0)
    extra = max(total_ml - goal_ml, 0)
    percent = round(total_ml / goal_ml * 100, 1)
    return {"total": total_ml, "remaining": remaining,
            "percent": percent, "extra": extra}


def progress_bar_value(percent):
    """st.progress needs a number between 0.0 and 1.0, so cap at 100%."""
    return min(percent, 100) / 100


def get_mood(percent):
    """
    Decide which mood Boondi (the mascot) should show.
    The thresholds here are the milestones drawn in the flowchart.
    """
    if percent <= 0:
        return "thirsty"
    elif percent < 25:
        return "waking"
    elif percent < 50:
        return "smiling"
    elif percent < 75:
        return "happy"
    elif percent < 100:
        return "excited"
    elif percent < 150:
        return "celebrating"
    else:
        return "overflowing"


def new_milestones_reached(old_percent, new_percent, already_celebrated):
    """
    Return the milestones that were crossed by the latest log and have
    not been celebrated yet today. Example: 40% -> 80% gives [50, 75].
    """
    reached = []
    for milestone in MILESTONES:
        crossed = old_percent < milestone <= new_percent
        if crossed and milestone not in already_celebrated:
            reached.append(milestone)
    return reached


# ---------------------------------------------------------------------------
# Pace check (are you on track for the time of day?)
# ---------------------------------------------------------------------------

def expected_percent_now(now, wake_time, sleep_time):
    """
    How far through the goal you would ideally be right now, assuming
    you drink evenly between waking up and going to bed.
    Returns None if the wake/sleep times don't make sense.
    """
    if sleep_time <= wake_time:
        return None

    now_minutes = now.hour * 60 + now.minute
    wake_minutes = wake_time.hour * 60 + wake_time.minute
    sleep_minutes = sleep_time.hour * 60 + sleep_time.minute

    if now_minutes <= wake_minutes:
        return 0.0
    if now_minutes >= sleep_minutes:
        return 100.0

    fraction = (now_minutes - wake_minutes) / (sleep_minutes - wake_minutes)
    return round(fraction * 100, 1)


def pace_status(actual_percent, expected_percent):
    """Compare actual progress with the ideal pace (10% wiggle room)."""
    if expected_percent is None:
        return "unknown"
    if actual_percent >= 100:
        return "done"
    if actual_percent >= expected_percent + 10:
        return "ahead"
    if actual_percent >= expected_percent - 10:
        return "on_track"
    return "behind"


def intake_in_last_hour(log, now):
    """Total ml logged in the 60 minutes before `now`."""
    one_hour_ago = now - timedelta(hours=1)
    total = 0
    for entry in log:
        if entry["time"] > one_hour_ago:
            total = total + entry["amount_ml"]
    return total


# ---------------------------------------------------------------------------
# End-of-day summary
# ---------------------------------------------------------------------------

def earned_badges(log, total_ml, goal_ml):
    """Return a list of (emoji, name, reason) badges for today's summary."""
    badges = []
    if total_ml >= goal_ml:
        badges.append(("🏆", "Goal Getter", "You reached your daily goal."))
    if len(log) >= 8:
        badges.append(("🔁", "Steady Sipper", "You logged 8 or more drinks."))
    morning_ml = sum(e["amount_ml"] for e in log if e["time"].hour < 10)
    if morning_ml >= 500:
        badges.append(("🌅", "Early Bird", "500 ml or more before 10 am."))
    if len(log) >= 4:
        biggest = max(e["amount_ml"] for e in log)
        hours_spread = (log[-1]["time"] - log[0]["time"]).total_seconds() / 3600
        if biggest <= 500 and hours_spread >= 6:
            badges.append(("🐢", "Slow & Steady",
                           "Small drinks spread over 6+ hours."))
    return badges


def default_wake_time():
    return time(7, 0)


def default_sleep_time():
    return time(22, 0)


def make_log_entry(amount_ml, label, when):
    """Build one log record. Kept as a function so the shape is clear."""
    return {"amount_ml": int(amount_ml), "label": label, "time": when}


def make_day_summary(day_number, log, goal_ml):
    """A small record of a finished day, used for the 'This week' view."""
    total = total_intake(log)
    progress = calculate_progress(total, goal_ml)
    return {"day": f"Day {day_number}", "total_ml": total,
            "goal_ml": goal_ml, "percent": progress["percent"],
            "drinks": len(log)}
