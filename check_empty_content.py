#!/usr/bin/env python3
"""
检查内容为空的问题
"""
import sqlite3
from path_utils import SUBSCRIBE_DB

conn = sqlite3.connect(SUBSCRIBE_DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 80)
print("检查内容为空的问题")
print("=" * 80)

# 统计总记录数
c.execute("SELECT COUNT(*) FROM subscription_history")
total = c.fetchone()[0]
print(f"\n总记录数：{total}")

# 检查 summary 为空的
c.execute("""
    SELECT COUNT(*) FROM subscription_history 
    WHERE summary IS NULL OR summary = '' OR length(trim(summary)) = 0
""")
empty_summary = c.fetchone()[0]
print(f"summary 为空：{empty_summary} ({empty_summary/total*100:.1f}%)")

# 检查 content 为空的
c.execute("""
    SELECT COUNT(*) FROM subscription_history 
    WHERE content IS NULL OR content = '' OR length(trim(content)) = 0
""")
empty_content = c.fetchone()[0]
print(f"content 为空：{empty_content} ({empty_content/total*100:.1f}%)")

# 抽样检查 summary 很短的（< 20 字符）
c.execute("""
    SELECT id, sub_name, title, length(summary) as summary_len, length(content) as content_len
    FROM subscription_history 
    WHERE summary IS NOT NULL AND length(trim(summary)) > 0 AND length(trim(summary)) < 20
    ORDER BY id DESC
    LIMIT 10
""")
short_summary = c.fetchall()
print(f"\nsummary 很短（<20 字符）的样本:")
for row in short_summary:
    print(f"  ID={row['id']}, sub={row['sub_name']}, title={row['title'][:30]}, summary_len={row['summary_len']}, content_len={row['content_len']}")

# 检查 summary 和 content 都为空的
c.execute("""
    SELECT id, sub_name, title 
    FROM subscription_history 
    WHERE (summary IS NULL OR summary = '' OR length(trim(summary)) = 0)
      AND (content IS NULL OR content = '' OR length(trim(content)) = 0)
    LIMIT 10
""")
both_empty = c.fetchall()
print(f"\nsummary 和 content 都为空的样本:")
for row in both_empty:
    print(f"  ID={row['id']}, sub={row['sub_name']}, title={row['title'][:50]}")

conn.close()

print("\n" + "=" * 80)
