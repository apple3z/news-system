#!/usr/bin/env python3
"""检查新闻时间"""

import sqlite3
from path_utils import NEWS_DB

conn = sqlite3.connect(NEWS_DB)
c = conn.cursor()

print("="*80)
print("检查新闻时间")
print("="*80)

c.execute("SELECT id, title, time, source FROM news ORDER BY time DESC LIMIT 20")
for row in c.fetchall():
    print(f"ID: {row[0]:3d} | 时间: {row[2]} | 来源: {row[3]:10s} | 标题: {row[1][:50]}...")

conn.close()

print("\n" + "="*80)
