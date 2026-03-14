#!/usr/bin/env python3
"""
为 subscription_history 表添加 comments 字段
"""
import sqlite3
from path_utils import SUBSCRIBE_DB

conn = sqlite3.connect(SUBSCRIBE_DB)
c = conn.cursor()

print("=" * 80)
print("为 subscription_history 表添加 comments 字段")
print("=" * 80)

try:
    # 检查字段是否已存在
    c.execute("PRAGMA table_info(subscription_history)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'comments' not in columns:
        # 添加 comments 字段
        c.execute('''
            ALTER TABLE subscription_history 
            ADD COLUMN comments INTEGER DEFAULT 0
        ''')
        conn.commit()
        print("✓ 成功添加 comments 字段 (INTEGER, 默认值 0)")
    else:
        print("✓ comments 字段已存在")
    
    # 验证
    c.execute("PRAGMA table_info(subscription_history)")
    columns = {row[1]: row[2] for row in c.fetchall()}
    print(f"\n当前表结构：{list(columns.keys())}")
    
    if 'comments' in columns:
        print(f"✓ comments 字段类型：{columns['comments']}")
    
    conn.close()
    print("\n✓ 完成！")
    
except Exception as e:
    print(f"✗ 错误：{e}")
    conn.rollback()
    conn.close()
