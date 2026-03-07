#!/usr/bin/env python3
import sqlite3

# Check news.db
conn = sqlite3.connect('/home/zhang/.copaw/news_system/data/news.db')
tables = conn.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
print("=== news.db tables ===")
for t in tables:
    print(f"- {t[0]}")
    cols = conn.execute(f'PRAGMA table_info({t[0]})').fetchall()
    for c in cols:
        print(f"  - {c[1]} ({c[2]})")

# Check skills.db
conn2 = sqlite3.connect('/home/zhang/.copaw/news_system/data/skills.db')
tables2 = conn2.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
print("\n=== skills.db tables ===")
for t in tables2:
    print(f"- {t[0]}")
    cols = conn2.execute(f'PRAGMA table_info({t[0]})').fetchall()
    for c in cols:
        print(f"  - {c[1]} ({c[2]})")

# Check subscribe.db
try:
    conn3 = sqlite3.connect('/home/zhang/.copaw/news_system/data/subscribe.db')
    tables3 = conn3.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
    print("\n=== subscribe.db tables ===")
    for t in tables3:
        print(f"- {t[0]}")
except Exception as e:
    print(f"\n=== subscribe.db error: {e} ===")
