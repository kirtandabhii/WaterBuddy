# WaterBuddy – Storyboard & Flowchart Notes

These notes describe the finished app so you can build the FA-1 storyboard and flowchart from it.
Every function named here exists in the code. File names are shown like `logic.py → get_mood()`.

---

## 1. Screens, sections and visual states

WaterBuddy is a **single page**. On a laptop the sections sit in two columns; on a phone they
stack from top to bottom in the order below. There is also a **sidebar**. It is always visible on
a laptop, and on a phone it opens from the **»** button at the top-left.

### 1.1 Header
- **Title:** "💧 WaterBuddy"
- **Greeting** based on the user's local hour (`content.py → greeting()`):
  - before 12:00 → "Good morning!"
  - 12:00–16:59 → "Good afternoon!"
  - 17:00 onward → "Good evening!"
- Followed by "Let's keep you hydrated today · *Thursday, 22 October*".

### 1.2 Goal card – "🎯 Your daily goal" (collapsible, open at start)
| Element | Widget | What it does |
|---|---|---|
| Age group | dropdown (`st.selectbox`) | 5 groups. Changing it sets the goal to that group's suggestion |
| ☀️ Hot day (+500 ml) | toggle | Adds 500 ml to the suggestion |
| 🏃 Active day / exercise (+500 ml) | toggle | Adds 500 ml to the suggestion |
| Your goal for today (ml) | number box (500–6000, steps of 50) | User can type their own goal |
| Age standard / Your goal | two big numbers side by side | Compares the guideline with the user's goal. Shows a green **+200 ml** style difference when they differ |
| ↩️ Use suggested goal | button, **only visible when the goal ≠ suggestion** | Puts the suggestion back |

The user can fold the card away with one tap. Its label never changes, so it stays folded.

### 1.3 Boondi + bottle (the "hero")
- **Boondi** (from Hindi *boond* = drop) is on the left and the **bottle** on the right.
  Below them is a speech bubble with Boondi's message.
- The bottle has tick marks at 25 / 50 / 75 / 100%. On every change the water **rises (or falls)
  from the old level to the new one** with a small bounce, and the surface ripples in a constant wave.
  Above 100% the bottle simply stays full.

**Boondi's 7 moods** (`logic.py → get_mood()`, drawings in `visuals.py → mascot_svg()`):

| % of goal | Mood | How Boondi looks | Animation |
|---|---|---|---|
| exactly 0 | **thirsty** | Pale grey-blue body, tired slanted eyes, wobbly mouth, sweat drop, arms drooping | Slow sway side to side |
| 1 – 24.9 | **waking** | Light blue, small round eyes, small smile, arms relaxed | Gentle bob |
| 25 – 49.9 | **smiling** | Brighter blue, bigger eyes, smile, pink cheeks | Bob |
| 50 – 74.9 | **happy** | Bright blue, big shiny eyes, open smile, cheeks | Bob + **right arm waves** |
| 75 – 99.9 | **excited** | Vivid blue, biggest eyes, wide grin with tongue | Fast bob, fast wave, **yellow sparkles twinkle** |
| 100 – 149.9 | **celebrating** | Bright aqua, closed "^ ^" happy eyes, huge grin, **pink party hat** | **Bounces**, both arms wave, **confetti falls** |
| 150+ | **overflowing** | Deep blue, calm closed eyes, small content smile | Slow bob, **bubbles float up** – the "you've had plenty" state |

**Boondi's messages** (`content.py → get_mascot_message()`). There is one message per mood, written
in 4 tones that depend on the age group (Kids → *kid*, Teens → *teen*, 19-50 and 51-64 → *adult*,
65+ → *senior*):

| Mood | Kid | Teen | Adult | Senior |
|---|---|---|---|---|
| thirsty | "I'm a dry little drop! Can we drink a glass of water together?" | "Running on empty. One glass to boot up?" | "Fresh start! A glass of water now wakes up your body and brain." | "Good day! Let's begin with a glass - thirst signals get quieter with age…" |
| waking | "Ooh, that felt nice! Let's keep going!" | "Nice, first sips logged. Keep the bottle close." | "Good start. Small regular sips work better than gulping later." | "Lovely start. Keep a glass within reach so it's easy to sip." |
| smiling | "Yay, a quarter done! You're a hydration hero!" | "25% done - you're ahead of most people already." | "Great - you've passed 25%! Keep it steady." | "A quarter of the way there - well done!" |
| happy | "WOW! Halfway! I'm doing a happy wiggle!" | "Halfway there. Your focus thanks you." | "Great! You reached 50%! Halfway to your goal." | "Halfway! Your body is thanking you." |
| excited | "Almost there! Just a few more sips, champ!" | "75%+! The finish line is in sight." | "Almost there - just a little more to go!" | "Nearly there - a couple more glasses and you're done." |
| celebrating | "YOU DID IT!! Party time! 🎉" | "Goal smashed. Legend." | "Goal reached - great job today!" | "You reached your goal today - wonderful!" |
| overflowing | "Whoa, I'm super full! Only drink more if you feel thirsty." | "Way past the goal - no need to force more…" | "Well past your goal. No need to push further - drink to thirst now." | "You've had plenty today. Just sip if you feel thirsty." |

### 1.4 Stats + logging panel
- **Three big numbers:** *Drunk* (ml), *To go* (ml), *Achieved* (%).
  Once you pass the goal, *To go* changes to **Above goal: +X ml**.
- **Progress bar** with the label "750 / 2,500 ml". It is capped at full when you go over 100%.
- **Pace line** (`logic.py → pace_status()`):
  | Status | Icon | Text |
  |---|---|---|
  | ahead | 🟢 | "Ahead of pace - lovely!" |
  | on_track | 🔵 | "Right on track for this time of day." |
  | behind | 🟠 | "A little behind for this time of day - a glass now would help." |
  | done | 🏁 | "Goal done for today." |
  | unknown | ⚪ | "Set your wake and sleep times to see your pace." |
  The line also shows the ideal value, e.g. *"(ideal by 14:30: about 50%)"*.
- **Buttons:** 🥛 **+250 ml (glass)** (main, highlighted) and 🍶 **+500 ml (bottle)**.
- **✏️ Log a different amount** (folding section): an amount box, an **ml / cups** switch and
  ➕ **Add this amount**.
- **Messages that appear only when needed:**
  - ⚠️ yellow warning: "Please enter an amount above 0 ml." or "That's more than 2000 ml at once…"
  - 🐢 blue note: "You've logged X ml in the last hour. Your kidneys can only clear about 0.8-1 litre an hour, so slow down a little." It shows when more than 1000 ml has been logged in the past 60 minutes.
- **↩️ Undo last drink** is greyed out when nothing has been logged.
- **🔄 Start a new day** opens a small confirm box: "This clears today's drinks…" → **Yes, start fresh**.

### 1.5 Pop-ups (toasts) and balloons
| Trigger | Pop-up |
|---|---|
| crossing 25% | 🌱 "25% done - nice start!" |
| crossing 50% | 🎯 "Great! You reached 50%!" |
| crossing 75% | 🚀 "75% - almost there!" |
| crossing 100% | 🏆 "Daily goal reached - amazing!" **+ balloons fly up the screen** |
| starting a new day | 🌊 "New day started - let's go!" |

Each milestone pops up once per day. If you undo below a milestone, it can pop up again.

### 1.6 Tabs at the bottom
1. **📈 Today**
   - **Empty state:** 🫗 "No drinks logged yet today. Tap +250 ml to start!"
   - **With drinks:** a line chart showing your running total in blue (it steps up at each drink),
     the ideal steady pace as a grey dashed line from 0 at wake-up to the goal at bedtime, and the
     goal as an orange line. Below it, a table of drinks (time, type, amount), newest first.
2. **🌙 End of day**
   - **Empty state:** "Your summary appears once you've logged a drink."
   - **Banner:**
     - ≥100% → green "🎉 Great job today! You reached your goal."
     - 50–99% → blue "💪 Good effort – X% of your goal."
     - <50% → yellow "🌱 X% today – tomorrow is a fresh start."
   - Total, drinks logged, glasses, plus **badges**:
     - 🏆 Goal Getter (reached goal)
     - 🔁 Steady Sipper (8+ drinks)
     - 🌅 Early Bird (500 ml+ before 10 am)
     - 🐢 Slow & Steady (4+ drinks, none over 500 ml, spread over 6+ hours)
   - Button: **Finish today & start a new day**.
3. **📅 This week:** a bar chart with one bar per finished day this session plus "today". Bars are
   dark aqua if the goal was reached and light aqua if not. A caption explains that the data stays only in this tab.

### 1.7 Sidebar
- **💡 Tip of the moment:** a random tip from a list of 12, with an **Another tip** button.
- **🔁 Cups ↔ ml** converter (1 cup = 250 ml).
- **⏰ My day:** wake-up and bedtime (used for the pace check). It warns if bedtime isn't after wake-up.
- **💧 How Boondi feels:** a legend of the 7 moods and their % ranges.
- Notes on switching light/dark mode (⋮ menu → Settings) and on privacy.

---

## 2. User journey – first open to end of day

1. **Open the link.** Boondi is pale and droopy (thirsty, 0%). The goal card is open, showing
   "Adults (19-50 yrs)" and a goal of 2,500 ml. The greeting matches the time of day.
2. **Set up (about 10 seconds).** Pick an age group, e.g. *Teens* → the goal changes to 2,000 ml.
   It's a hot day, so switch on ☀️ → 2,500 ml. Optionally type your own goal, which shows the
   difference from the age standard. Fold the card away.
3. **First glass.** Tap **+250 ml**. The bottle rises to 10%, Boondi wakes up and smiles
   ("Nice, first sips logged…"), the numbers show 250 / 2,250 / 10%, and the timeline chart appears.
4. **During the day.** Each tap updates everything at once. Crossing 25%, 50% and 75% gives a
   pop-up and a new Boondi mood. The pace line says whether you're ahead or behind for the time
   of day. A wrong tap? **Undo**. Drank from a mug? Use **Log a different amount** in ml or cups.
5. **Reach the goal.** Balloons, 🏆 pop-up, and Boondi bounces in a party hat with confetti.
6. **Too much?** Above 150% Boondi turns calm and says to drink only by thirst. If more than
   1 litre was logged within an hour, a 🐢 safety note appears.
7. **Evening.** Open **🌙 End of day** to see the total, drinks and badges earned.
8. **Next morning (or to test).** Tap **Start a new day** → confirm. Today's total moves to
   **📅 This week**, the bottle empties and Boondi is thirsty again. The age and goal settings stay.
9. **Closing the tab** clears everything. This is on purpose: the app is private, with no account and no server storage.

---

## 3. Logic and data flow (flowchart-ready)

### 3.1 How Streamlit runs the app
Streamlit runs `app.py` **from top to bottom on every click**. Values that must survive between
runs live in `st.session_state`. Buttons use **callbacks** (`on_click=`): Streamlit runs the
callback first, then redraws the page, so the screen always shows the new numbers immediately.

### 3.2 Data stored (`state.py → init_state()`, only filled in on the very first run)
| Key | Starts as | Meaning |
|---|---|---|
| `age_group` | "Adults (19-50 yrs)" | chosen age group |
| `hot_day`, `active_day` | False | day-type toggles |
| `goal_ml` | 2500 | today's goal |
| `log` | [] | list of drinks: `{amount_ml, label, time}` |
| `celebrated` | [] | milestones already celebrated today |
| `previous_percent` | 0.0 | bottle level last drawn (animation start) |
| `pending_toasts`, `pending_balloons` | [], False | celebrations waiting to be shown |
| `warning` | "" | last input problem |
| `history`, `day_number` | [], 1 | finished days |
| `tip_index` | random | current tip |
| `wake_time`, `sleep_time` | 07:00, 22:00 | for the pace check |
| `custom_amount`, `custom_unit` | 250.0, "ml" | custom log box |

### 3.3 Main flow on every run (`app.py → main()`)
```
START
 → init_state()                       create missing keys
 → now = current_time()               user's local time (browser time zone)
 → progress = get_progress()          total, remaining, percent, extra
 → show_header(now)
 → show_goal_section()
 → show_mascot_and_bottle(progress)   mood → message → draw → remember level
 → show_stats(progress, now)          numbers, progress bar, pace
 → show_logging_controls(now)         buttons, warnings, fast-drinking note
 → tabs: show_today_tab / show_end_of_day_tab / show_week_tab
 → show_sidebar(now)
 → show_pending_feedback()            toasts + balloons, then clear the queue
END (wait for the next click)
```

### 3.4 Goal calculation
**Input:** age group, hot-day toggle, active-day toggle, optional manual goal.

1. `logic.standard_goal(age)` looks up the table:
   | Age group | ml |
   |---|---|
   | 6-12 | 1600 |
   | 13-18 | 2000 |
   | 19-50 | 2500 |
   | 51-64 | 2500 |
   | 65+ | 2000 |
2. `logic.suggested_goal(age, hot, active)` = standard **+ 500 if hot** **+ 500 if active**.
3. When the age or a toggle changes, `state.apply_suggested_goal()` sets `goal_ml` to the suggestion.
4. If the user types a goal, `state.on_goal_edited()` runs `logic.clamp_goal()` to keep it between 500 and 6000.
5. **Decision:** is `goal_ml ≠ suggested`?
   - Yes → show the "Use suggested goal" button, which calls `apply_suggested_goal()`.
   - No → hide it.

### 3.5 Logging a drink (the core flowchart) – `state.py → add_water(amount_ml, label)`
```
User taps +250  → on_add_glass()   → add_water(250, "Glass")
User taps +500  → on_add_bottle()  → add_water(500, "Bottle")
User taps Add   → on_add_custom(): if unit == cups → amount_ml = cups × 250 (logic.cups_to_ml)
                                   else amount_ml = round(amount)
                                   → add_water(amount_ml, "Custom")

add_water:
 1. logic.validate_log_amount(amount_ml)
      amount ≤ 0     → NO  → warning "enter an amount above 0"      → STOP
      amount > 2000  → NO  → warning "more than 2000 ml at once"   → STOP
      otherwise      → OK  → clear warning
 2. old_percent = current percent
 3. append {amount_ml, label, time=now} to log      (logic.make_log_entry)
 4. new_percent = recalculated percent
 5. reached = logic.new_milestones_reached(old, new, celebrated)
       for each milestone M in [25, 50, 75, 100]:
          if old < M ≤ new and M not yet celebrated → reached
 6. for each M in reached: add to celebrated; queue its toast
       if M == 100 → queue balloons
 → page redraws (3.6)
```

### 3.6 Calculations shown after every run
1. **Total:** `logic.total_intake(log)` = sum of every `amount_ml`.
2. **Progress:** `logic.calculate_progress(total, goal)`:
   - `remaining = max(goal − total, 0)` (never negative)
   - `extra = max(total − goal, 0)`
   - `percent = round(total ÷ goal × 100, 1)` (if goal ≤ 0 → 0, which avoids dividing by zero)
3. **Progress bar:** `logic.progress_bar_value(percent)` = `min(percent, 100) ÷ 100`.
4. **Mood:** `logic.get_mood(percent)`, a chain of if/elif:
   `≤0 thirsty` → `<25 waking` → `<50 smiling` → `<75 happy` → `<100 excited` → `<150 celebrating` → else `overflowing`.
5. **Message:** `content.get_mascot_message(mood, age_group)` picks the mood row and the age tone column.
6. **Drawing:** `visuals.hero_html()` → `mascot_svg(mood)` (body colour, eyes, mouth, cheeks,
   arms, extras) + `bottle_svg(percent, previous_percent)`. The water's height is
   `water_level_y(p) = 228 − 168 × min(p,100)/100`. Then `previous_percent = percent` is
   stored so the next change animates from here.
7. **Over-goal display:** if `extra > 0` show "Above goal +extra", otherwise show "To go remaining".

### 3.7 Pace check
1. `logic.expected_percent_now(now, wake, sleep)`:
   - bedtime ≤ wake-up → **None** (invalid)
   - now ≤ wake → 0
   - now ≥ bedtime → 100
   - otherwise → `(minutes since wake ÷ minutes awake) × 100`
2. `logic.pace_status(actual, expected)`:
   - expected is None → *unknown*
   - actual ≥ 100 → *done*
   - actual ≥ expected + 10 → *ahead*
   - actual ≥ expected − 10 → *on_track*
   - else → *behind*

### 3.8 Safety check
`logic.intake_in_last_hour(log, now)` adds up drinks in the past 60 minutes.
If the total is **> 1000 ml**, show the 🐢 slow-down note.

### 3.9 Undo – `state.on_undo_last()`
Is the log empty? → do nothing (the button is greyed out anyway).
Otherwise → remove the last drink, clear any warning, and forget any milestone that is now above
the new percent, so it can be celebrated again.

### 3.10 Start a new day – `state.on_start_new_day()`
Is the log non-empty? → `logic.make_day_summary()` adds `{day, total, goal, percent, drinks}` to
`history`, then `day_number + 1`.
Then always: clear `log`, `celebrated` and `warning`, and queue the 🌊 toast.
The goal and age settings are **kept**.

### 3.11 End-of-day badges – `logic.earned_badges(log, total, goal)`
- total ≥ goal → 🏆
- drinks ≥ 8 → 🔁
- ml before 10:00 ≥ 500 → 🌅
- ≥4 drinks AND largest ≤ 500 ml AND first-to-last ≥ 6 h → 🐢

### 3.12 Other small flows
- **Unit switch** (`state.on_unit_change`): ml → cups divides by 250; cups → ml multiplies by 250,
  so the number in the box means the same amount.
- **Another tip** (`state.on_new_tip` → `content.random_tip_index`): picks a random index that differs from the current one.
- **Time zone** (`state.current_time`): uses the browser's time zone (`st.context.timezone`),
  because Streamlit Cloud's server runs on UTC. If that fails, it falls back to the server's clock.

### 3.13 Tests
- `tests/test_logic.py`: 21 tests of every calculation, covering zero, negative and huge amounts,
  going past the goal, every mood boundary, milestones, pace and badges.
- `tests/test_app.py`: 7 end-to-end tests that run the real app with Streamlit's `AppTest` and
  click buttons. They cover glass/bottle logging, age → goal, past-goal, 0 ml rejected, cups
  conversion, undo and reset.

Run them with `python -m unittest discover tests`.

---

## 4. Research rationale

### 4.1 Why hydration matters
- Water is needed for temperature control, circulation, kidney function and brain function.
  Even mild dehydration has measurable effects (Popkin, D'Anci & Rosenberg, 2010).
- Losing about **2% of body weight** in water can impair attention, memory and mood (Adan, 2012).
  This is why the app nudges people early in the day rather than only at the end.
- Children and teens are often under-hydrated. A US national survey found that **over half** of
  children and adolescents were inadequately hydrated (Kenney et al., 2015). This is why the app
  has a kid-friendly mascot and tone.
- **Older adults feel less thirsty** than younger adults when they are equally dehydrated
  (Kenney & Chiu, 2001), so thirst alone is a poor guide for them. This is why seniors get messages
  like "sip before you feel thirsty" and "keep a glass within reach".
- Too much water too fast is also risky. Healthy kidneys can only pass roughly **0.8–1 L of water
  per hour** (Noakes et al., 2001), and over-drinking can cause hyponatraemia. Expert consensus says
  to let thirst guide drinking once needs are met (Hew-Butler et al., 2015). This is why the app has
  the 150%+ "drink to thirst" mood and the 🐢 more-than-1-L-in-an-hour note.

### 4.2 Age-based goals used, and where they come from
The goals mean **water from drinks per day**, rounded to amounts that are easy to log in 250 ml glasses.

| Group | App goal | Evidence |
|---|---|---|
| Kids 6-12 | **1600 ml** | EFSA (2010) adequate intake of *total* water: 1.6 L at 4–8 y, 1.9–2.1 L at 9–13 y. Food supplies roughly 20–30% of total water, so 1.6 L from drinks fits the whole 6–12 range. It is also the brief's example for kids. |
| Teens 13-18 | **2000 ml** | EFSA: 9–13 y 1.9–2.1 L; from 14 y the adult values apply (2.0 L women, 2.5 L men). 2.0 L is a middle value. |
| Adults 19-50 | **2500 ml** | EFSA adult total water AI: 2.0 L (women) / 2.5 L (men). US National Academies (IOM, 2004): 2.7 L / 3.7 L total, about 80% of it from drinks (≈2.2 / 3.0 L). 2.5 L sits between these and is the brief's example for adults. |
| Adults 51-64 | **2500 ml** | EFSA gives older adults the same values as younger adults. This group is listed separately only to close the gap between "19-50" and "65+" in the brief's example groups. |
| Seniors 65+ | **2000 ml** | ESPEN geriatric guideline (Volkert et al., 2019; updated 2022): at least **1.6 L/day for women and 2.0 L/day for men** from drinks. The app uses 2.0 L. |
| Hot day | **+500 ml** | Heat increases sweat losses. EFSA notes that requirements rise in hot climates. This is a simple, safe rule of thumb. |
| Active day | **+500 ml** | Sweat rates during exercise are commonly 0.5–2 L per hour (ACSM position stand, Sawka et al., 2007). +500 ml covers roughly 30–60 minutes of moderate exercise. |

The user can always type their own goal (for example, if a doctor gave them a target). The app
keeps it within 500–6000 ml.

### 4.3 Why existing water apps fail
- **People stop using them.** In app-based health interventions, dropout averages about **43%**
  (Meyerowitz-Katz et al., 2020). Typical water trackers ask for too much input (cup sizes, sign-up,
  notifications) and then become a chore.
- **Numbers without meaning.** "1,250 ml" by itself doesn't say whether you're doing well *right now*.
- **One goal for everyone.** Many use a fixed "8 glasses" target, ignoring age, heat and activity.
- **Nagging instead of encouraging.** Constant alarms get muted. Habits form through small,
  repeated actions with immediate positive feedback, and automaticity takes on average about
  **66 days** to build (Lally et al., 2010).
- **Privacy:** many need accounts and store health data on servers.

### 4.4 How WaterBuddy is different
1. **One tap to log**, with no sign-up. Setting up takes about 10 seconds.
2. **Age-aware goal *and* tone:** the goal comes from guidelines and adjusts for heat and exercise,
   and Boondi talks differently to a 9-year-old and a 70-year-old.
3. **Instant, emotional feedback:** the bottle fills and Boondi's mood changes on every tap, with
   celebrations at 25/50/75/100%. Small rewards make the habit enjoyable.
4. **The pace check** turns the number into a judgement for this moment: "on track for 2 pm".
5. **Safety built in:** it doesn't push people past their goal, warns about drinking too fast, and
   says "drink to thirst" at 150%+.
6. **Private by design:** everything stays in the browser tab, with no account, no database and no tracking
   (Streamlit usage statistics are turned off in `.streamlit/config.toml`).
7. **Inclusive and local:** large text, works on phones and laptops, light and dark themes, a
   cups ↔ ml converter, and India-friendly tips (chaas, coconut water).

### 4.5 Sources
- Adan, A. (2012). Cognitive performance and dehydration. *Journal of the American College of Nutrition*, 31(2), 71–78.
- EFSA Panel on Dietetic Products, Nutrition and Allergies (2010). Scientific Opinion on Dietary Reference Values for water. *EFSA Journal*, 8(3):1459. https://doi.org/10.2903/j.efsa.2010.1459
- Hew-Butler, T. et al. (2015). Statement of the Third International Exercise-Associated Hyponatremia Consensus Development Conference, Carlsbad, California, 2015. *Clinical Journal of Sport Medicine*, 25(4), 303–320; *British Journal of Sports Medicine*, 49(22), 1432–1446. https://bjsm.bmj.com/content/49/22/1432
- Institute of Medicine (2004/2005). *Dietary Reference Intakes for Water, Potassium, Sodium, Chloride, and Sulfate*. National Academies Press. https://doi.org/10.17226/10925
- Kenney, E. L., Long, M. W., Cradock, A. L., & Gortmaker, S. L. (2015). Prevalence of inadequate hydration among US children and disparities by gender and race/ethnicity: NHANES 2009–2012. *American Journal of Public Health*, 105(8), e113–e118.
- Kenney, W. L., & Chiu, P. (2001). Influence of age on thirst and fluid intake. *Medicine & Science in Sports & Exercise*, 33(9), 1524–1532.
- Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W., & Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. *European Journal of Social Psychology*, 40(6), 998–1009.
- Meyerowitz-Katz, G. et al. (2020). Rates of attrition and dropout in app-based interventions for chronic disease: systematic review and meta-analysis. *Journal of Medical Internet Research*, 22(9), e20283.
- Noakes, T. D. et al. (2001). Peak rates of diuresis in healthy humans during oral fluid overload. *South African Medical Journal*, 91(10), 852–857. https://pubmed.ncbi.nlm.nih.gov/11732457/
- Popkin, B. M., D'Anci, K. E., & Rosenberg, I. H. (2010). Water, hydration, and health. *Nutrition Reviews*, 68(8), 439–458.
- Sawka, M. N. et al. (2007). American College of Sports Medicine position stand: Exercise and fluid replacement. *Medicine & Science in Sports & Exercise*, 39(2), 377–390.
- Volkert, D. et al. (2019). ESPEN guideline on clinical nutrition and hydration in geriatrics. *Clinical Nutrition*, 38(1), 10–47 (practical version updated 2022, *Clinical Nutrition*, 41(4), 958–989).

> Tip for your FA-1 write-up: double-check each reference in Google Scholar before submitting, and
> cite the ones you actually read. The numbers above are the ones the app's code uses.
