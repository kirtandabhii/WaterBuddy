"""
content.py - All the words WaterBuddy says.

Keeping text separate from logic makes it easy to change the tone
without touching any calculations.
"""

import random

MASCOT_NAME = "Boondi"   # from the Hindi word "boond" = a drop of water

# Which "tone" of message each age group gets.
AGE_TONE = {
    "Kids (6-12 yrs)": "kid",
    "Teens (13-18 yrs)": "teen",
    "Adults (19-50 yrs)": "adult",
    "Adults (51-64 yrs)": "adult",
    "Seniors (65+ yrs)": "senior",
}

# Boondi's message for every mood, written for every tone.
# The mood names come from logic.get_mood().
MOOD_MESSAGES = {
    "thirsty": {
        "kid": "I'm a dry little drop! Can we drink a glass of water together?",
        "teen": "Running on empty. One glass to boot up?",
        "adult": "Fresh start! A glass of water now wakes up your body and brain.",
        "senior": "Good day! Let's begin with a glass - thirst signals get quieter "
                  "with age, so it helps to sip before you feel thirsty.",
    },
    "waking": {
        "kid": "Ooh, that felt nice! Let's keep going!",
        "teen": "Nice, first sips logged. Keep the bottle close.",
        "adult": "Good start. Small regular sips work better than gulping later.",
        "senior": "Lovely start. Keep a glass within reach so it's easy to sip.",
    },
    "smiling": {
        "kid": "Yay, a quarter done! You're a hydration hero!",
        "teen": "25% done - you're ahead of most people already.",
        "adult": "Great - you've passed 25%! Keep it steady.",
        "senior": "A quarter of the way there - well done!",
    },
    "happy": {
        "kid": "WOW! Halfway! I'm doing a happy wiggle!",
        "teen": "Halfway there. Your focus thanks you.",
        "adult": "Great! You reached 50%! Halfway to your goal.",
        "senior": "Halfway! Your body is thanking you.",
    },
    "excited": {
        "kid": "Almost there! Just a few more sips, champ!",
        "teen": "75%+! The finish line is in sight.",
        "adult": "Almost there - just a little more to go!",
        "senior": "Nearly there - a couple more glasses and you're done.",
    },
    "celebrating": {
        "kid": "YOU DID IT!! Party time! 🎉",
        "teen": "Goal smashed. Legend.",
        "adult": "Goal reached - great job today!",
        "senior": "You reached your goal today - wonderful!",
    },
    "overflowing": {
        "kid": "Whoa, I'm super full! Only drink more if you feel thirsty.",
        "teen": "Way past the goal - no need to force more. Sip by thirst now.",
        "adult": "Well past your goal. No need to push further - drink to thirst now.",
        "senior": "You've had plenty today. Just sip if you feel thirsty.",
    },
}

MILESTONE_TOASTS = {
    25: ("🌱", "25% done - nice start!"),
    50: ("🎯", "Great! You reached 50%!"),
    75: ("🚀", "75% - almost there!"),
    100: ("🏆", "Daily goal reached - amazing!"),
}

PACE_MESSAGES = {
    "ahead": ("🟢", "Ahead of pace - lovely!"),
    "on_track": ("🔵", "Right on track for this time of day."),
    "behind": ("🟠", "A little behind for this time of day - a glass now would help."),
    "done": ("🏁", "Goal done for today."),
    "unknown": ("⚪", "Set your wake and sleep times to see your pace."),
}

# Short, true hydration tips. One is shown at random in the sidebar.
TIPS = [
    "Start your day with a glass of water before tea or coffee.",
    "Keep a bottle on your desk - you drink more when it's in sight.",
    "Pale straw-coloured urine usually means you're well hydrated.",
    "Feeling tired or getting a headache? Mild dehydration can be the cause.",
    "Fruits like watermelon, oranges and cucumber count towards your water too.",
    "Drink a glass of water with every meal - an easy habit to remember.",
    "On hot days or after exercise, your body needs extra water.",
    "Older adults feel less thirsty, so sipping on a schedule helps.",
    "Even 1-2% dehydration can affect concentration and mood.",
    "Sip steadily through the day rather than gulping lots at once.",
    "Buttermilk (chaas), coconut water and lemon water are great Indian hydrators.",
    "Sugary drinks add calories - plain water is the best everyday choice.",
]


def get_mascot_message(mood, age_group):
    """Pick Boondi's message for this mood, in the right tone for the age."""
    tone = AGE_TONE.get(age_group, "adult")
    return MOOD_MESSAGES[mood][tone]


def random_tip_index(current_index):
    """Choose a new random tip that is different from the current one."""
    new_index = random.randrange(len(TIPS))
    while new_index == current_index and len(TIPS) > 1:
        new_index = random.randrange(len(TIPS))
    return new_index


def greeting(hour):
    """A friendly greeting based on the hour of the day (0-23)."""
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"
