import sqlite3
import os

# 连接数据库
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'subscribe.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查当前表结构
print('检查 subscription_history 表结构...')
c.execute('PRAGMA table_info(subscription_history)')
columns = c.fetchall()
print('当前字段:')
for col in columns:
    print(f'  {col[1]}: {col[2]}')

# 添加新字段（如果不存在）
try:
    c.execute('ALTER TABLE subscription_history ADD COLUMN title TEXT')
    print('添加 title 字段成功')
except:
    print('title 字段已存在')

try:
    c.execute('ALTER TABLE subscription_history ADD COLUMN summary TEXT')
    print('添加 summary 字段成功')
except:
    print('summary 字段已存在')

try:
    c.execute('ALTER TABLE subscription_history ADD COLUMN link TEXT')
    print('添加 link 字段成功')
except:
    print('link 字段已存在')

conn.commit()

# 更新现有数据，尝试从 content 中提取标题
print('\n尝试更新现有数据...')
c.execute('SELECT id, content FROM subscription_history WHERE title IS NULL OR title = ""')
rows = c.fetchall()
print(f'找到 {len(rows)} 条需要更新的记录')

for row_id, content in rows:
    if not content:
        continue
    # 提取第一行作为标题
    lines = content.strip().split('\n')
    title = lines[0][:200] if lines else '无标题'
    
    # 提取第二行到第N行作为摘要
    summary = '\n'.join(lines[1:])[:500] if len(lines) > 1 else content[:500]
    
    c.execute('UPDATE subscription_history SET title = ?, summary = ? WHERE id = ?', 
              (title, summary, row_id))

conn.commit()

# 验证更新结果
c.execute('SELECT id, title, summary FROM subscription_history LIMIT 3')
rows = c.fetchall()
print('\n更新后的数据示例:')
for row in rows:
    print(f'  ID: {row[0]}, Title: {row[1][:50] if row[1] else "无"}..., Summary: {row[2][:50] if row[2] else "无"}...')

conn.close()
print('\n数据库修复完成！')
