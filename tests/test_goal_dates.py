import unittest
from services.goal_dates import normalize_goal_date

class GoalDateTests(unittest.TestCase):
    def test_slashes_are_normalized(self):
        self.assertEqual(normalize_goal_date('2026/12/23'),'2026-12-23')
    def test_dashes_and_whitespace(self):
        self.assertEqual(normalize_goal_date(' 2026-12-23 '),'2026-12-23')
    def test_optional_blank(self):
        self.assertEqual(normalize_goal_date(' '),'')
    def test_invalid_dates_and_formats(self):
        for value in ['2026/02/30','2026-13-01','23/12/2026','2026/12-23','abc']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_goal_date(value)
    def test_leap_year(self):
        self.assertEqual(normalize_goal_date('2028/02/29'),'2028-02-29')
        with self.assertRaises(ValueError):normalize_goal_date('2026/02/29')
