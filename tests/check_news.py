#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('data/news.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM news WHERE summary IS NOT NULL AND summary != ""')
print(f'有摘要的新闻数：{c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM news')
print(f'总新闻数：{c.fetchone()[0]}')
c.execute('SELECT id, title FROM news LIMIT 3')
for row in c.fetchall():
    print(f'  [{row[0]}] {row[1][:60]}')
conn.close()
