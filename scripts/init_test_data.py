#!/usr/bin/env python3
"""
初始化测试数据
- 添加订阅源数据
- 添加订阅历史内容
"""

import sqlite3
import os
from datetime import datetime, timedelta
import json

# 创建 data 目录
os.makedirs('data', exist_ok=True)

print("=" * 50)
print("初始化测试数据...")
print("=" * 50)

# ========== 订阅数据库 ==========
print("\n[1/1] 初始化 subscribe.db 测试数据...")
conn = sqlite3.connect('data/subscribe.db')
c = conn.cursor()

# 添加订阅源
subscription_data = [
    ('科技美学', 'https://www.zhihu.com/rss', 'website', 300, None, None, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    ('36氪', 'https://36kr.com/feed', 'rss', 300, None, None, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    ('虎嗅网', 'https://www.huxiu.com/rss', 'rss', 300, None, None, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    ('机器之心', 'https://www.jiqizhixin.com/rss', 'rss', 300, None, None, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    ('量子位', 'https://www.qbitai.com/rss', 'rss', 300, None, None, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
]

for name, url, sub_type, interval, last_check, last_content, is_active, created_at in subscription_data:
    c.execute('''INSERT OR IGNORE INTO subscription (name, url, sub_type, check_interval, last_check, last_content, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (name, url, sub_type, interval, last_check, last_content, is_active, created_at))

conn.commit()
print("✓ 添加 5 个订阅源")

# 添加订阅历史内容（使用正确的表结构）
subscription_history_data = [
    # 科技美学 - 3篇文章
    (1, '科技美学', '<p>AI正在改变工业设计的方式...</p>', '2026-03-12 10:00:00'),
    (1, '科技美学', '<p>智能硬件市场正在快速增长...</p>', '2026-03-11 15:30:00'),
    (1, '科技美学', '<p>最新的交互技术让人耳目一新...</p>', '2026-03-10 09:15:00'),
    
    # 36氪 - 3篇文章
    (2, '36氪', '<p>AI创业公司获得了大量融资...</p>', '2026-03-12 08:30:00'),
    (2, '36氪', '<p>大模型技术正在寻找商业化路径...</p>', '2026-03-11 14:20:00'),
    (2, '36氪', '<p>AI产品经理的需求持续增长...</p>', '2026-03-10 11:45:00'),
    
    # 虎嗅网 - 2篇文章
    (3, '虎嗅网', '<p>自动驾驶技术面临诸多挑战...</p>', '2026-03-12 07:15:00'),
    (3, '虎嗅网', '<p>智能座舱正在成为新的竞争焦点...</p>', '2026-03-11 16:00:00'),
    
    # 机器之心 - 2篇文章
    (4, '机器之心', '<p>大语言模型在多个领域取得突破...</p>', '2026-03-12 06:45:00'),
    (4, '机器之心', '<p>计算机视觉技术已经非常成熟...</p>', '2026-03-11 13:30:00'),
    
    # 量子位 - 2篇文章
    (5, '量子位', '<p>AI绘画工具正在被广泛使用...</p>', '2026-03-12 05:20:00'),
    (5, '量子位', '<p>最新的机器人技术令人惊叹...</p>', '2026-03-11 12:00:00'),
]

for sub_id, sub_name, content, detected_at in subscription_history_data:
    c.execute('''INSERT OR IGNORE INTO subscription_history (sub_id, sub_name, content, detected_at)
        VALUES (?, ?, ?, ?)''',
        (sub_id, sub_name, content, detected_at))

conn.commit()
print("✓ 添加 12 条订阅历史内容")

conn.close()

print("\n" + "=" * 50)
print("测试数据初始化完成！")
print("=" * 50)
print("\n订阅源:")
print("  - 科技美学 (知乎)")
print("  - 36氪")
print("  - 虎嗅网")
print("  - 机器之心")
print("  - 量子位")
print("\n订阅历史:")
print("  - 总计 12 条文章")
print("  - 每个订阅源 2-3 条文章")
print("  - 时间范围：2026-03-10 至 2026-03-12")
