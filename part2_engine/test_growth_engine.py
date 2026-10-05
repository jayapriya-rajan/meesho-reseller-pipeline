import csv
import os
import unittest

from growth_engine import mom_growth, is_flagged, validate_feed

BASE = os.path.dirname(os.path.abspath(__file__))
CORRUPTED = os.path.join(BASE, "fixtures", "corrupted_feed.csv")
GOOD_FEED = os.path.join(BASE, "fixtures", "monthly_category_revenue.csv")


def load_revenue():
    data = {}
    with open(GOOD_FEED, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data[(row["month"], row["category"])] = float(row["revenue"])
    return data


class TestGrowthEngine(unittest.TestCase):

    def test_ethnic_wear_april_to_may_is_flagged(self):
        # GIVEN Ethnic Wear revenue moves from 104520.77 to 185107.61
        previous, current = 104520.77, 185107.61
        # WHEN mom_growth then is_flagged run on it
        pct = mom_growth(previous, current)
        result = is_flagged(pct)
        # THEN mom_growth returns 77.1 and is_flagged returns "flagged"
        self.assertEqual(pct, 77.1)
        self.assertEqual(result, "flagged")

    def test_beauty_may_to_june_is_not_flagged(self):
        # GIVEN Beauty & Personal Care revenue moves from 35542.11 to 37559.07
        previous, current = 35542.11, 37559.07
        # WHEN evaluated
        pct = mom_growth(previous, current)
        result = is_flagged(pct)
        # THEN mom_growth returns 5.67 and is_flagged returns "not_flagged"
        self.assertEqual(pct, 5.67)
        self.assertEqual(result, "not_flagged")

    def test_exact_boundary_is_escalated(self):
        # GIVEN previous=100000 and current=108000
        previous, current = 100000, 108000
        # WHEN evaluated
        pct = mom_growth(previous, current)
        result = is_flagged(pct)
        # THEN mom_growth returns exactly 8.0 and is_flagged returns "escalate_exact_boundary"
        self.assertEqual(pct, 8.0)
        self.assertEqual(result, "escalate_exact_boundary")

    def test_corrupted_feed_returns_three_errors(self):
        # GIVEN the corrupted feed fixture
        # WHEN validate_feed runs on it
        ok, errors = validate_feed(CORRUPTED)
        # THEN it returns (False, errors) with exactly 3 entries, in order
        self.assertFalse(ok)
        self.assertEqual(errors, [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)",
        ])

    def test_good_feed_passes_validation(self):
        # GIVEN the validated Part 1 file
        # WHEN validate_feed runs on it
        ok, errors = validate_feed(GOOD_FEED)
        # THEN it returns (True, [])
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_full_mom_tables(self):
        # GIVEN the real revenue figures from Part 1
        rev = load_revenue()
        expected = {
            ("April", "May"): {
                "Ethnic Wear": (77.1, "flagged"),
                "Western Wear": (-23.6, "flagged"),
                "Kids Wear": (-23.48, "flagged"),
                "Home & Kitchen": (-9.25, "flagged"),
                "Beauty & Personal Care": (-12.75, "flagged"),
            },
            ("May", "June"): {
                "Ethnic Wear": (-58.74, "flagged"),
                "Western Wear": (11.97, "flagged"),
                "Kids Wear": (23.9, "flagged"),
                "Home & Kitchen": (42.59, "flagged"),
                "Beauty & Personal Care": (5.67, "not_flagged"),
            },
        }
        # WHEN mom_growth and is_flagged run on every category
        for (prev_m, cur_m), table in expected.items():
            for category, (want_pct, want_flag) in table.items():
                pct = mom_growth(rev[(prev_m, category)], rev[(cur_m, category)])
                # THEN each result matches the brief's table
                self.assertEqual(pct, want_pct, f"{cur_m} {category}")
                self.assertEqual(is_flagged(pct), want_flag, f"{cur_m} {category}")


if __name__ == "__main__":
    unittest.main(verbosity=2)