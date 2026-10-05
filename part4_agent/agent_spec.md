# Agent Specification: Monthly Category Alert Agent

## 1. Goal

Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with a human approving every message before it goes out.

## 2. The five components

Goal: the sentence above.

Tools: the functions the agent calls.
- validate_feed (Part 2): checks the feed CSV and returns (True, []) or (False, errors).
- mom_growth (Part 2): works out the month-on-month change in percent.
- is_flagged (Part 2): returns flagged, not_flagged or escalate_exact_boundary.
- The template-fill function (Part 3 prompt pack): puts a category's real numbers into the message template. It works offline, with no LLM call and no API key.

Memory / State: the agent must remember last month's revenue for every category, so it can work out this month's change. In this project that comes from the previous month's CSV, taken from Part 1 monthly_category_revenue.csv.

Planner: the ordered subtasks in section 4.

Feedback loop: a human approves each draft before it counts as sent. In the runner this is only a flag in the output (action_taken = drafted_and_held_for_approval). Nothing is actually sent.

## 3. Constraints, guardrails and stopping conditions

Constraints (the numeric rules)
- A category is flagged when its change is more than 8% in either direction.
- At most 3 drafts per run, ordered by the size of the change. This stops the agent from sending managers one message for every flagged category.

Guardrails (what the agent may not do)
- Input guardrail: validate_feed must pass before anything else runs.
- Action guardrail: no message is ever sent automatically. Messages are only drafted and held.
- Output guardrail: every number in a drafted message must come from a Part 1 or Part 2 value. No figure is invented.

Stopping conditions
- Success, with drafts: drafts are produced and every number can be traced.
- Success, no drafts: nothing crossed the threshold, so zero drafts is the correct result.
- Error stop: validate_feed returns False. This is a Hard Stop and the validation errors are shown in the output. The run is never skipped silently.

Escalation: a category that lands exactly on 8.0% is neither flagged nor not flagged. The agent does not decide it either way. It is listed in escalated_categories for a human to review, and no message is drafted. This is different from an error stop, because the data is fine and only the decision is unclear.

Success criteria
- Numeric accuracy: every percentage and revenue figure in the output matches the Part 1 and Part 2 values exactly.
- Flagging accuracy: categories above 8% are flagged, and categories below 8% are not.
- Safety: in every run, no message is sent and every draft is held for approval.
- Traceability: on a bad feed, the validation errors are exactly the ones validate_feed returns.

## 4. Ordered subtasks (the Planner)

1. Load the monthly revenue feed and run validate_feed.
2. If the feed is invalid, Hard Stop and report the errors.
3. If the feed is valid, compute mom_growth for every category against the previous month.
4. Run is_flagged on every category.
5. Sort the flagged categories by abs(mom_pct), largest first.
6. Draft a message (using the Part 3 template) for at most the top 3 by size of change.
7. Log any remaining flagged categories beyond the cap as "suppressed, review manually". No message is drafted for them.
7b. Separately, log any category whose result is escalate_exact_boundary into escalated_categories. No message is drafted for it. It must never be dropped from both lists or mistaken for flagged or not_flagged.
8. Emit one structured JSON object for the run.

## 5. Output schema

Every run, whether it succeeds or hard stops, produces one JSON object with exactly these top-level keys:

- run_month: the month being checked, for example May.
- validation_status: valid or invalid.
- validation_errors: a list of error strings, empty when the feed is valid.
- flagged_categories: a list of objects with category, mom_pct, previous_revenue, current_revenue, drafted (true or false), and message (only if drafted).
- suppressed_categories: a list of category names, empty if nothing was suppressed.
- escalated_categories: a list of category names with the result escalate_exact_boundary, empty unless an exact-boundary case happens.
- action_taken: drafted_and_held_for_approval or hard_stop.

## 6. Given-When-Then specs

Spec 1
- GIVEN April to May Ethnic Wear revenue moves from 104520.77 to 185107.61,
- WHEN the agent runs mom_growth and then is_flagged on it,
- THEN mom_growth returns 77.1 and is_flagged returns flagged, so the category is drafted for approval.

Spec 2
- GIVEN May to June Beauty & Personal Care revenue moves from 35542.11 to 37559.07,
- WHEN the agent evaluates it,
- THEN mom_growth returns 5.67 and is_flagged returns not_flagged, so no message is drafted and the category appears in none of the output lists.

Spec 3
- GIVEN a synthetic pair previous=100000 and current=108000, chosen so the growth is exactly on the threshold,
- WHEN the agent evaluates it,
- THEN mom_growth returns exactly 8.0 and is_flagged returns escalate_exact_boundary, so the category goes into escalated_categories for human review and is neither flagged nor not_flagged.

Spec 4
- GIVEN the corrupted feed fixture,
- WHEN the agent runs validate_feed on it as its first step,
- THEN validate_feed returns (False, errors) with exactly 3 entries, in this order: the negative-revenue row, the missing-category row, and the missing-revenue row. The run is a Hard Stop and no month-on-month calculation is attempted.