import csv
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "..", "data", "meesho_reseller.db")
SQL_PATH = os.path.join(BASE, "queries.sql")
OUT_DIR = os.path.join(BASE, "output")

os.makedirs(OUT_DIR, exist_ok=True)

with open(SQL_PATH, "r", encoding="utf-8") as f:
    blocks = f.read().split("-- @output:")[1:]

conn = sqlite3.connect(DB_PATH)

for block in blocks:
    filename, sql = block.split("\n", 1)
    filename = filename.strip()
    cur = conn.execute(sql)
    header = [col[0] for col in cur.description]
    rows = cur.fetchall()
    with open(os.path.join(OUT_DIR, filename), "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Saved {filename} ({len(rows)} rows)")

conn.close()