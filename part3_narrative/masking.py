from __future__ import annotations
import csv
import os


def alias_for(reseller_id: str) -> str:
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(text: str, reseller_names: list[str]) -> bool:
    for name in reseller_names:
        if name in text:
            return False
    return True


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base, "..", "data", "resellers.csv")
    with open(csv_path, newline="", encoding="utf-8") as f:
        names = [row["reseller_name"] for row in csv.DictReader(f)]

    # alias checks
    assert alias_for("RS019") == "ALIAS-19"
    assert alias_for("RS006") == "ALIAS-06"
    print("alias_for: OK")

    # negative case: raw name is still in the text, so it must return False
    leaky = "West region: Mumbai Reseller 1 was the top reseller."
    assert assert_no_raw_names_leak(leaky, names) is False
    print("Leaky text detected (returns False): OK")

    # positive case: only the alias is used, so it must return True
    clean = "West region: ALIAS-19 was the top reseller."
    assert assert_no_raw_names_leak(clean, names) is True
    print("Clean text passes (returns True): OK")

    # final check: the real narrative file must contain no raw names
    report_path = os.path.join(base, "narrative_report.md")
    with open(report_path, encoding="utf-8") as f:
        report_text = f.read()
    assert assert_no_raw_names_leak(report_text, names) is True
    print("Narrative file has no raw names (returns True): OK")