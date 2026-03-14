#!/usr/bin/env python3
"""
查看当前订阅源并添加优质 AI 科技类订阅源
"""
import sqlite3
from datetime import datetime
from path_utils import SUBSCRIBE_DB

conn = sqlite3.connect(SUBSCRIBE_DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 80)
print("当前订阅源")
print("=" * 80)

c.execute("SELECT * FROM subscription ORDER BY id")
subs = c.fetchall()

for sub in subs:
    print(f"\nID: {sub['id']}")
    print(f"  name: {sub['name']}")
    print(f"  url: {sub['url']}")
    print(f"  sub_type: {sub['sub_type']}")
    print(f"  is_active: {sub['is_active']}")

conn.close()
