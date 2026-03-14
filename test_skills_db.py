#!/usr/bin/env python3
"""
临时脚本：清理 skills.db 重复数据 + 运行爬虫测试
用完后可删除
"""
import sqlite3
import os
import sys

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB = os.path.join('data', 'skills.db')


def check_and_clean():
    """Step 1: 检查并清理重复数据"""
    if not os.path.exists(DB):
        print(f'[WARN] {DB} not found, will be created by crawler')
        return

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Show current data
    c.execute('SELECT id, name, owner, stars FROM skills ORDER BY name, id')
    rows = c.fetchall()
    print(f'=== Current skills: {len(rows)} rows ===')
    for r in rows:
        print(f'  id={r[0]:<3} name={r[1]:<15} owner={r[2]:<15} stars={r[3]}')

    # Find and remove duplicates (keep highest id per name+owner)
    c.execute('''
        SELECT name, owner, COUNT(*) as cnt
        FROM skills GROUP BY name, owner HAVING cnt > 1
    ''')
    dupes = c.fetchall()

    if dupes:
        print(f'\n=== Found {len(dupes)} duplicate groups, cleaning... ===')
        for name, owner, cnt in dupes:
            c.execute('''
                DELETE FROM skills WHERE name=? AND owner=?
                AND id NOT IN (SELECT MAX(id) FROM skills WHERE name=? AND owner=?)
            ''', (name, owner, name, owner))
            print(f'  Removed {cnt-1} duplicate(s) for {name}/{owner}')
        conn.commit()
        c.execute('SELECT COUNT(*) FROM skills')
        print(f'\nAfter cleanup: {c.fetchone()[0]} rows')
    else:
        print('\nNo duplicates found.')

    conn.close()


def run_crawler():
    """Step 2: 运行 Skills 爬虫"""
    print('\n' + '=' * 50)
    print('Running Skills Crawler...')
    print('=' * 50)
    from modules.news_crawler.crawlers.fetch_skills import fetch_skills
    result = fetch_skills()
    print(f'\nResult: {result}')

    # Verify data
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, name, owner, stars, description FROM skills ORDER BY name')
    rows = c.fetchall()
    print(f'\n=== Final data: {len(rows)} rows ===')
    for r in rows:
        desc = (r[4] or '')[:60]
        print(f'  id={r[0]:<3} name={r[1]:<15} owner={r[2]:<15} stars={r[3]:<6} desc={desc}')
    conn.close()


if __name__ == '__main__':
    check_and_clean()
    run_crawler()
    print('\nDone! You can delete this file: test_skills_db.py')
