#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/home/zhang/.copaw/news_system/data/skills.db')
c = conn.cursor()
c.execute('SELECT name, features, capabilities, skill_level, chinese_intro, github_url, download_url FROM skills LIMIT 5')
for r in c.fetchall():
    print(f"=== {r[0]} ===")
    print(f"功能: {r[1]}")
    print(f"能力: {r[2]}")
    print(f"级别: {r[3]}")
    print(f"介绍: {r[4][:60]}...")
    print(f"GitHub: {r[5]}")
    print(f"下载: {r[6]}")
    print()
conn.close()
