"""
Tests for logic.py - run with:  python -m unittest discover tests

These check the calculations before they are linked to the visuals,
as the brief suggests ("Test calculations before linking to visuals").
"""

import os
import sys
import unittest
from datetime import datetime, time

# Let the tests import logic.py from the folder above.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logic  # noqa: E402


def entry(ml, hour=12, minute=0):
    """Helper: make a log entry at a given time today."""
    return logic.make_log_entry(ml, "Test", datetime(2026, 10, 22, hour, minute))


class TestGoals(unittest.TestCase):
    def test_standard_goals(self):
        self.assertEqual(logic.standard_goal("Kids (6-12 yrs)"), 1600)
        self.assertEqual(logic.standard_goal("Adults (19-50 yrs)"), 2500)
        self.assertEqual(logic.standard_goal("Seniors (65+ yrs)"), 2000)

    def test_suggested_goal_adds_extras(self):
        self.assertEqual(logic.suggested_goal("Teens (13-18 yrs)"), 2000)
        self.assertEqual(logic.suggested_goal("Teens (13-18 yrs)", hot_day=True), 2500)
        self.assertEqual(logic.suggested_goal("Teens (13-18 yrs)", True, True), 3000)

    def test_clamp_goal(self):
        self.assertEqual(logic.clamp_goal(100), logic.MIN_GOAL_ML)
        self.assertEqual(logic.clamp_goal(99999), logic.MAX_GOAL_ML)
        self.assertEqual(logic.clamp_goal(-50), logic.MIN_GOAL_ML)
        self.assertEqual(logic.clamp_goal(2200), 2200)


class TestConversion(unittest.TestCase):
    def test_cups_and_ml(self):
        self.assertEqual(logic.cups_to_ml(1), 250)
        self.assertEqual(logic.cups_to_ml(1.5), 375)
        self.assertEqual(logic.ml_to_cups(750), 3.0)
        self.assertEqual(logic.ml_to_cups(0), 0.0)


class TestValidation(unittest.TestCase):
    def test_rejects_zero_negative_and_huge(self):
        self.assertFalse(logic.validate_log_amount(0)[0])
        self.assertFalse(logic.validate_log_amount(-250)[0])
        self.assertFalse(logic.validate_log_amount(2001)[0])

    def test_accepts_normal_amounts(self):
        self.assertTrue(logic.validate_log_amount(1)[0])
        self.assertTrue(logic.validate_log_amount(250)[0])
        self.assertTrue(logic.validate_log_amount(2000)[0])


class TestProgress(unittest.TestCase):
    def test_total_intake(self):
        self.assertEqual(logic.total_intake([]), 0)
        self.assertEqual(logic.total_intake([entry(250), entry(500), entry(100)]), 850)

    def test_progress_below_goal(self):
        p = logic.calculate_progress(1250, 2500)
        self.assertEqual(p["remaining"], 1250)
        self.assertEqual(p["percent"], 50.0)
        self.assertEqual(p["extra"], 0)

    def test_progress_above_goal(self):
        p = logic.calculate_progress(3000, 2500)
        self.assertEqual(p["remaining"], 0)      # never negative
        self.assertEqual(p["percent"], 120.0)
        self.assertEqual(p["extra"], 500)

    def test_progress_zero_goal_is_safe(self):
        self.assertEqual(logic.calculate_progress(500, 0)["percent"], 0)

    def test_progress_bar_is_capped(self):
        self.assertEqual(logic.progress_bar_value(50), 0.5)
        self.assertEqual(logic.progress_bar_value(180), 1.0)


class TestMoodAndMilestones(unittest.TestCase):
    def test_mood_thresholds(self):
        cases = [(0, "thirsty"), (1, "waking"), (24.9, "waking"), (25, "smiling"),
                 (50, "happy"), (74.9, "happy"), (75, "excited"), (99.9, "excited"),
                 (100, "celebrating"), (149.9, "celebrating"), (150, "overflowing")]
        for percent, mood in cases:
            self.assertEqual(logic.get_mood(percent), mood, percent)

    def test_milestones_crossed(self):
        self.assertEqual(logic.new_milestones_reached(40, 80, []), [50, 75])
        self.assertEqual(logic.new_milestones_reached(0, 100, []), [25, 50, 75, 100])
        self.assertEqual(logic.new_milestones_reached(40, 80, [50]), [75])
        self.assertEqual(logic.new_milestones_reached(60, 70, []), [])


class TestPace(unittest.TestCase):
    def setUp(self):
        self.wake, self.sleep = time(7, 0), time(22, 0)

    def test_expected_percent(self):
        def at(h, m=0):
            return logic.expected_percent_now(datetime(2026, 1, 1, h, m),
                                              self.wake, self.sleep)
        self.assertEqual(at(6), 0.0)
        self.assertEqual(at(14, 30), 50.0)
        self.assertEqual(at(23), 100.0)

    def test_invalid_times(self):
        self.assertIsNone(logic.expected_percent_now(datetime(2026, 1, 1, 12),
                                                     time(22, 0), time(7, 0)))

    def test_pace_status(self):
        self.assertEqual(logic.pace_status(70, 50), "ahead")
        self.assertEqual(logic.pace_status(45, 50), "on_track")
        self.assertEqual(logic.pace_status(20, 50), "behind")
        self.assertEqual(logic.pace_status(100, 50), "done")
        self.assertEqual(logic.pace_status(20, None), "unknown")

    def test_last_hour(self):
        log = [entry(500, 10, 0), entry(300, 11, 30), entry(400, 11, 50)]
        self.assertEqual(logic.intake_in_last_hour(log, datetime(2026, 10, 22, 12, 0)), 700)


class TestSummary(unittest.TestCase):
    def test_badges(self):
        log = [entry(250, 8), entry(250, 9)] + [entry(250, 12 + i) for i in range(8)]
        names = [b[1] for b in logic.earned_badges(log, 2500, 2500)]
        self.assertIn("Goal Getter", names)
        self.assertIn("Steady Sipper", names)
        self.assertIn("Early Bird", names)
        self.assertIn("Slow & Steady", names)

    def test_no_slow_and_steady_when_rushed(self):
        log = [entry(500, 12, m) for m in range(5)]   # five drinks in 5 minutes
        names = [b[1] for b in logic.earned_badges(log, 2500, 2500)]
        self.assertNotIn("Slow & Steady", names)

    def test_no_badges_for_empty_day(self):
        self.assertEqual(logic.earned_badges([], 0, 2500), [])

    def test_day_summary(self):
        s = logic.make_day_summary(3, [entry(1000), entry(250)], 2500)
        self.assertEqual(s["total_ml"], 1250)
        self.assertEqual(s["percent"], 50.0)
        self.assertEqual(s["day"], "Day 3")


if __name__ == "__main__":
    unittest.main()
