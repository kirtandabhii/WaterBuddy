"""
End-to-end tests: run the real app.py with Streamlit's built-in AppTest,
click the buttons and check what the user would see.

Run with:  python -m unittest discover tests
"""

import os
import unittest

from streamlit.testing.v1 import AppTest

APP_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def find_button(at, text):
    """Return the first button whose label contains `text`."""
    for button in at.button:
        if text in button.label:
            return button
    raise AssertionError(f"No button containing {text!r}")


def metric_values(at):
    """All st.metric values on the page, as a {label: value} dict."""
    return {m.label: m.value for m in at.metric}


class TestWaterBuddyApp(unittest.TestCase):
    def setUp(self):
        self.at = AppTest.from_file(APP_FILE, default_timeout=30).run()

    def test_starts_empty_with_adult_goal(self):
        self.assertFalse(self.at.exception)
        values = metric_values(self.at)
        self.assertEqual(values["Drunk"], "0 ml")
        self.assertEqual(values["To go"], "2,500 ml")
        self.assertEqual(values["Achieved"], "0%")

    def test_glass_button_updates_numbers(self):
        find_button(self.at, "+250 ml").click().run()
        find_button(self.at, "+250 ml").click().run()
        values = metric_values(self.at)
        self.assertEqual(values["Drunk"], "500 ml")
        self.assertEqual(values["To go"], "2,000 ml")
        self.assertEqual(values["Achieved"], "20%")

    def test_age_group_changes_goal(self):
        self.at.selectbox(key="age_group").select("Kids (6-12 yrs)").run()
        self.assertEqual(self.at.session_state.goal_ml, 1600)
        self.at.toggle(key="hot_day").set_value(True).run()
        self.assertEqual(self.at.session_state.goal_ml, 2100)

    def test_going_past_goal(self):
        for _ in range(6):
            find_button(self.at, "+500 ml").click().run()
        values = metric_values(self.at)
        self.assertEqual(values["Above goal"], "+500 ml")
        self.assertEqual(values["Achieved"], "120%")
        self.assertEqual(self.at.session_state.celebrated, [25, 50, 75, 100])

    def test_zero_custom_amount_is_rejected(self):
        self.at.number_input(key="custom_amount").set_value(0.0).run()
        find_button(self.at, "Add this amount").click().run()
        self.assertEqual(len(self.at.warning), 1)
        self.assertEqual(metric_values(self.at)["Drunk"], "0 ml")

    def test_cups_are_converted(self):
        self.at.radio(key="custom_unit").set_value("cups").run()
        self.assertEqual(self.at.session_state.custom_amount, 1.0)   # 250 ml -> 1 cup
        self.at.number_input(key="custom_amount").set_value(2.0).run()
        find_button(self.at, "Add this amount").click().run()
        self.assertEqual(metric_values(self.at)["Drunk"], "500 ml")

    def test_undo_and_reset(self):
        find_button(self.at, "+500 ml").click().run()
        find_button(self.at, "+250 ml").click().run()
        find_button(self.at, "Undo").click().run()
        self.assertEqual(metric_values(self.at)["Drunk"], "500 ml")

        self.at.button(key="reset_confirm").click().run()
        self.assertEqual(metric_values(self.at)["Drunk"], "0 ml")
        self.assertEqual(len(self.at.session_state.history), 1)
        self.assertEqual(self.at.session_state.history[0]["total_ml"], 500)


if __name__ == "__main__":
    unittest.main()
