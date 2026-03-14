#!/usr/bin/env python3
"""
检查订阅数据库中的原始数据
"""
import sqlite3
from path_utils import SUBSCRIBE_DB

conn = sqlite3.connect(SUBSCRIBE_DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 80)
print("检查 subscription_history 表中的原始数据")
print("=" * 80)

c.execute("SELECT * FROM subscription_history ORDER BY id DESC LIMIT 3")
rows = c.fetchall()

for i, row in enumerate(rows):
    print(f"\n--- 记录 {i+1} (ID: {row['id']}) ---")
    print(f"sub_name: {row['sub_name']}")
    print(f"title: {row['title']}")
    print(f"summary: {repr(row['summary'][:100]) if row['summary'] else 'None'}")
    print(f"content: {repr(row['content'][:200]) if row['content'] else 'None'}")
    print(f"link: {row['link']}")
    print(f"pub_date: {row['pub_date']}")
    print(f"detected_at: {row['detected_at']}")

print("\n" + "=" * 80)
print("检查 subscription 表")
print("=" * 80)

c.execute("SELECT * FROM subscription")
subs = c.fetchall()

for sub in subs:
    print(f"\nID: {sub['id']}")
    print(f"  name: {sub['name']}")
    print(f"  url: {sub['url']}")
    print(f"  sub_type: {sub['sub_type']}")
    print(f"  last_content: {repr(sub['last_content'][:100]) if sub['last_content'] else 'None'}")

conn.close()
