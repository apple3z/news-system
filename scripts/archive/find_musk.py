#!/usr/bin/env python3
"""查找马斯克那条新闻"""

import sqlite3
from path_utils import NEWS_DB

conn = sqlite3.connect(NEWS_DB)
c = conn.cursor()

print("="*80)
print("查找马斯克相关新闻")
print("="*80)

c.execute("SELECT id, title, time, source, link FROM news WHERE title LIKE '%马斯克%' OR title LIKE '%xAI%'")
for row in c.fetchall():
    print(f"\nID: {row[0]}")
    print(f"标题: {row[1]}")
    print(f"时间: {row[2]}")
    print(f"来源: {row[3]}")
    print(f"链接: {row[4]}")
    print("-"*80)

conn.close()
