#!/usr/bin/env python3
"""
检查订阅内容的 comments 字段
"""
import sqlite3
from path_utils import SUBSCRIBE_DB

conn = sqlite3.connect(SUBSCRIBE_DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 80)
print("检查 subscription_history 表的 comments 字段")
print("=" * 80)

# 检查表结构
c.execute("PRAGMA table_info(subscription_history)")
columns = {row['name']: row['type'] for row in c.fetchall()}

print(f"\n表字段：{list(columns.keys())}")

if 'comments' not in columns:
    print("\n⚠️  表中没有 comments 字段！")
    print("需要添加 comments 字段")
else:
    print("\n✓ comments 字段存在")
    
    # 检查 comments 为空的记录
    c.execute("SELECT COUNT(*) FROM subscription_history")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM subscription_history WHERE comments IS NULL OR comments = ''")
    empty = c.fetchone()[0]
    
    print(f"\n总记录数：{total}")
    print(f"comments 为空：{empty} ({empty/total*100:.1f}%)")
    
    # 抽样检查
    c.execute("SELECT id, sub_name, title, comments FROM subscription_history LIMIT 10")
    samples = c.fetchall()
    
    print(f"\n抽样检查:")
    for row in samples:
        comments_len = len(row['comments']) if row['comments'] else 0
        print(f"  ID={row['id']}, sub={row['sub_name']}, comments_len={comments_len}")

conn.close()
