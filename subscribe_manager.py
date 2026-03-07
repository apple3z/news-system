#!/usr/bin/env python3
"""
订阅管理模块 - 简化版
"""

import sqlite3
import requests
from datetime import datetime
from bs4 import BeautifulSoup

DB_FILE = "/home/zhang/.copaw/news_system/data/subscribe.db"

SUB_TYPES = {
    'website': '网站',
    'rss': 'RSS订阅',
    'video': '视频',
    'forum': '论坛'
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscription (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        sub_type TEXT DEFAULT 'website',
        check_interval INTEGER DEFAULT 300,
        last_check TEXT,
        last_content TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT
    )''')
    conn.commit()
    return conn

def add_subscription(name, url, sub_type='website', interval=300):
    conn = init_db()
    c = conn.cursor()
    c.execute('''INSERT INTO subscription (name, url, sub_type, check_interval, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              (name, url, sub_type, interval, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    sub_id = c.lastrowid
    conn.commit()
    conn.close()
    return sub_id

def remove_subscription(sub_id):
    conn = init_db()
    c = conn.cursor()
    c.execute("DELETE FROM subscription WHERE id = ?", (sub_id,))
    conn.commit()
    conn.close()

def get_subscriptions():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM subscription WHERE is_active = 1 ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_subs():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM subscription ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# 测试
if __name__ == "__main__":
    print("订阅列表:")
    for sub in get_all_subs():
        print(f"  [{sub[0]}] {sub[1]} - {sub[2]} ({sub[3]})")
