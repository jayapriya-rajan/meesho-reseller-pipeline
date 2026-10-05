from growth_engine import mom_growth, is_flagged, validate_feed

# Test 1: April to May, Ethnic Wear
pct = mom_growth(104520.77, 185107.61)
print("Ethnic Wear April->May:", pct, is_flagged(pct))

# Test 2: May to June, Beauty & Personal Care
pct = mom_growth(35542.11, 37559.07)
print("Beauty May->June:", pct, is_flagged(pct))

# Test 3: exact boundary
pct = mom_growth(100000, 108000)
print("Boundary case:", pct, is_flagged(pct))

# Test 4: the corrupted feed
ok, errors = validate_feed("part2_engine/fixtures/corrupted_feed.csv")
print("Corrupted feed:", ok)
for e in errors:
    print("  ", e)

# Test 5: the good feed
ok, errors = validate_feed("part2_engine/fixtures/monthly_category_revenue.csv")
print("Good feed:", ok, errors)