**Meesho Reseller Growth and Alert Intelligence Pipeline**

This project is a small, working pipeline that finds which product categories moved enough month on month to matter, drafts a message for each one, and holds every message for a human to approve. It has four parts. Each part feeds the next.

**1. How to run it (in order)**

Run every command from the main project folder.

Step 1: regenerate the dataset (24 resellers, 900 orders)

    python data/generate_dataset.py

This writes resellers.csv, orders.csv and meesho_reseller.db inside the data folder. The seed and weights are not changed, so the numbers are always the same. It should print: Wrote 24 resellers and 900 orders. Zero-order reseller: RS024

Step 2: Part 1, SQL queries

    python part1_sql/run_queries.py

This runs every query in queries.sql and saves each result as a CSV in part1_sql/output. The explanation of why COUNT(*) cannot detect a zero-match LEFT JOIN row is in the comments of Query 4b in queries.sql. For RS024, COUNT(*) is 1 and COUNT(order_id) is 0.

Step 3: Part 2, growth engine tests

    python part2_engine/test_growth_engine.py

It should end with OK after running 6 tests.

Step 4: Part 3, masking checks

    python part3_narrative/masking.py

It should print four OK lines. The prompt pack and the written narratives are in prompt_pack.md and narrative_report.md.

Step 5: Part 4, mock agent runner

    python part4_agent/mock_agent_runner.py

It prints one JSON object for each of three scenarios: May, June, and the corrupted feed. The agent specification is in agent_spec.md.

**2. How the parts connect**

- Part 1 writes monthly_category_revenue.csv. A copy of it is in part2_engine/fixtures.
- Part 2 (growth_engine.py) reads that file. It gives the month-on-month percentage, the flag decision, and the input check.
- Part 3 gives the message template (the prompt pack) and the masking rules for reseller names.
- Part 4 (mock_agent_runner.py) imports the Part 2 functions without changing them. It fills the Part 3 template for each flagged category and holds the drafts for approval. The template-fill function is written inside mock_agent_runner.py.

**3. Zero API keys**

The whole pipeline runs with no API keys, no paid service, and no account. Every narrative step is an offline template fill. The runner makes no network call and sends nothing. Drafts are only held for approval.

**4. Which workflow pattern each part follows**

- Part 1 to Part 2: real numbers are computed with SQL first, then handed to the next stage.
- Part 2: a numeric rule replaces the vague phrase "significant change". Input is validated first, and an exact-boundary result is held for a human and not decided automatically.
- Part 3: Context, Insight and Implication, with facts and hypotheses labeled separately and reseller names masked.
- Part 4: Intake, then Summary, then Report Draft, then Validate. The agent validates the feed, calculates and flags, drafts at most 3 messages, and holds them for approval.

**5. Documentation referenced**

Official Python standard library documentation for the sqlite3, csv, os, sys, json and unittest modules.