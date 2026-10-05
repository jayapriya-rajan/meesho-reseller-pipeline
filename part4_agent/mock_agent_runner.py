from __future__ import annotations
import csv
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE, "..", "part2_engine"))

from growth_engine import mom_growth, is_flagged, validate_feed

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
MAX_DRAFTS = 3

TEMPLATE = (
    "Context: This update compares {category} revenue in {month} with {prev_month}.\n"
    "Insight (Fact): {category} revenue moved from INR {previous_revenue} in {prev_month} "
    "to INR {current_revenue} in {month}, a month-on-month change of {mom_pct}%.\n"
    "Implication: The {category} category manager should check what changed in {category} "
    "between {prev_month} and {month}, such as offers, new listings or stock gaps. "
    "Hypothesis: the change may come from one of these, but the data alone does not prove it. "
    "Next check: confirm the cause before any stock or target is changed. "
    "This draft is held for human approval and has not been sent."
)


def fill_template(category, month, prev_month, previous_revenue, current_revenue, mom_pct):
    return TEMPLATE.format(
        category=category,
        month=month,
        prev_month=prev_month,
        previous_revenue=previous_revenue,
        current_revenue=current_revenue,
        mom_pct=mom_pct,
    )


def load_month(csv_path, month):
    revenue = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["month"] == month:
                revenue[row["category"]] = float(row["revenue"])
    return revenue


def check_inputs(previous_month_csv, current_month_csv):
    # Input guardrail: both feeds must be valid before anything else runs
    errors = []
    ok_current, current_errors = validate_feed(current_month_csv)
    errors.extend(current_errors)
    if previous_month_csv != current_month_csv:
        ok_previous, previous_errors = validate_feed(previous_month_csv)
        errors.extend(previous_errors)
    return len(errors) == 0, errors


def find_changes(previous, current):
    # Steps 3 and 4: growth and flag for every category
    flagged = []
    escalated = []
    for category, current_revenue in current.items():
        if category not in previous:
            continue
        previous_revenue = previous[category]
        pct = mom_growth(previous_revenue, current_revenue)
        status = is_flagged(pct)
        if status == "flagged":
            flagged.append({
                "category": category,
                "mom_pct": pct,
                "previous_revenue": previous_revenue,
                "current_revenue": current_revenue,
            })
        elif status == "escalate_exact_boundary":
            escalated.append(category)
    return flagged, escalated


def message_is_traceable(item):
    # Output guardrail: the message must carry the category name and the exact mom_pct
    return item["category"] in item["message"] and str(item["mom_pct"]) in item["message"]


def run(month: str, previous_month_csv: str, current_month_csv: str) -> dict:
    result = {
        "run_month": month,
        "validation_status": "valid",
        "validation_errors": [],
        "flagged_categories": [],
        "suppressed_categories": [],
        "escalated_categories": [],
        "action_taken": "drafted_and_held_for_approval",
    }

    # Steps 1 and 2: validate the feeds, Hard Stop if invalid
    inputs_ok, errors = check_inputs(previous_month_csv, current_month_csv)
    if not inputs_ok:
        result["validation_status"] = "invalid"
        result["validation_errors"] = errors
        result["action_taken"] = "hard_stop"
        return result

    prev_month = MONTHS[MONTHS.index(month) - 1]
    previous = load_month(previous_month_csv, prev_month)
    current = load_month(current_month_csv, month)

    # Steps 3 and 4
    flagged, escalated = find_changes(previous, current)

    # Step 5: largest change first
    flagged.sort(key=lambda item: abs(item["mom_pct"]), reverse=True)

    # Steps 6 and 7: draft the top 3, suppress the rest
    for position, item in enumerate(flagged):
        if position < MAX_DRAFTS:
            item["drafted"] = True
            item["message"] = fill_template(
                item["category"], month, prev_month,
                item["previous_revenue"], item["current_revenue"], item["mom_pct"],
            )
            assert message_is_traceable(item), "message does not match its source numbers"
            result["flagged_categories"].append(item)
        else:
            result["suppressed_categories"].append(item["category"])

    # Step 7b: exact-boundary categories get no message
    result["escalated_categories"] = escalated

    # Step 8: one structured result per run
    return result


if __name__ == "__main__":
    good_feed = os.path.join(BASE, "..", "part2_engine", "fixtures", "monthly_category_revenue.csv")
    bad_feed = os.path.join(BASE, "..", "part2_engine", "fixtures", "corrupted_feed.csv")

    scenarios = [
        ("May scenario (April to May)", "May", good_feed, good_feed),
        ("June scenario (May to June)", "June", good_feed, good_feed),
        ("Corrupted feed scenario", "July", good_feed, bad_feed),
    ]
    for title, month, prev_csv, cur_csv in scenarios:
        print("=== " + title + " ===")
        print(json.dumps(run(month, prev_csv, cur_csv), indent=2))