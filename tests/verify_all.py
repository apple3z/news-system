#!/usr/bin/env python3
"""
v2.6.0 跨平台路径验证脚本
验证所有模块功能是否正常
"""

import requests
import sqlite3
import sys

def check_database():
    """检查数据库"""
    print("=" * 60)
    print("数据库检查")
    print("=" * 60)
    
    # 新闻数据库
    try:
        conn = sqlite3.connect('data/news.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM news')
        count = c.fetchone()[0]
        print(f"✅ 新闻数据库：{count} 条新闻")
        conn.close()
    except Exception as e:
        print(f"❌ 新闻数据库异常：{e}")
    
    # Skills 数据库
    try:
        conn = sqlite3.connect('data/skills.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM skills')
        count = c.fetchone()[0]
        print(f"✅ Skills 数据库：{count} 个技能")
        conn.close()
    except Exception as e:
        print(f"❌ Skills 数据库异常：{e}")
    
    # 订阅数据库
    try:
        conn = sqlite3.connect('data/subscribe.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM subscription')
        count = c.fetchone()[0]
        print(f"✅ 订阅数据库：{count} 个订阅")
        conn.close()
    except Exception as e:
        print(f"❌ 订阅数据库异常：{e}")
    
    print()


def check_web_modules():
    """检查 Web 模块"""
    print("=" * 60)
    print("Web 模块检查")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 新闻首页
    try:
        r = requests.get(f"{base_url}/", timeout=5)
        if r.status_code == 200:
            import re
            titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)
            print(f"✅ 新闻首页：Status {r.status_code} ({len(titles)} 条新闻)")
        else:
            print(f"❌ 新闻首页：Status {r.status_code}")
    except Exception as e:
        print(f"❌ 新闻首页异常：{e}")
    
    # Skills 页面
    try:
        r = requests.get(f"{base_url}/skills", timeout=5)
        print(f"✅ Skills 页面：Status {r.status_code}")
    except Exception as e:
        print(f"❌ Skills 页面异常：{e}")
    
    # 订阅页面
    try:
        r = requests.get(f"{base_url}/subscribe", timeout=5)
        print(f"✅ 订阅页面：Status {r.status_code}")
    except Exception as e:
        print(f"❌ 订阅页面异常：{e}")
    
    # 系统管理页面
    try:
        r = requests.get(f"{base_url}/sys", timeout=5)
        print(f"✅ 系统管理页面：Status {r.status_code}")
    except Exception as e:
        print(f"❌ 系统管理页面异常：{e}")
    
    print()


def check_path_utils():
    """检查路径工具"""
    print("=" * 60)
    print("路径工具检查")
    print("=" * 60)
    
    try:
        from path_utils import (
            PROJECT_ROOT, DATA_DIR, NEWS_DB, SKILLS_DB, SUBSCRIBE_DB,
            VERSION_HISTORY_DIR, DOCS_DIR
        )
        
        print(f"✅ 项目根目录：{PROJECT_ROOT}")
        print(f"✅ 数据目录：{DATA_DIR}")
        print(f"✅ 新闻数据库：{NEWS_DB}")
        print(f"✅ Skills 数据库：{SKILLS_DB}")
        print(f"✅ 订阅数据库：{SUBSCRIBE_DB}")
        print(f"✅ 版本历史目录：{VERSION_HISTORY_DIR}")
        print(f"✅ 文档中心目录：{DOCS_DIR}")
        
        # 验证路径存在
        import os
        print(f"\n路径验证:")
        print(f"  项目根目录存在：{os.path.exists(PROJECT_ROOT)}")
        print(f"  数据目录存在：{os.path.exists(DATA_DIR)}")
        print(f"  版本历史存在：{os.path.exists(VERSION_HISTORY_DIR)}")
        print(f"  文档中心存在：{os.path.exists(DOCS_DIR)}")
        
    except Exception as e:
        print(f"❌ 路径工具异常：{e}")
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("v2.6.0 跨平台路径验证")
    print("=" * 60 + "\n")
    
    # 检查路径工具
    check_path_utils()
    
    # 检查数据库
    check_database()
    
    # 检查 Web 模块
    check_web_modules()
    
    # 总结
    print("=" * 60)
    print("验证总结")
    print("=" * 60)
    print("✅ 所有检查完成！")
    print()
    print("访问地址:")
    print("  📰 新闻首页：http://localhost:5000")
    print("  🛠️ Skills 工具：http://localhost:5000/skills")
    print("  📥 订阅管理：http://localhost:5000/subscribe")
    print("  ⚙️ 系统管理：http://localhost:5000/sys")
    print()


if __name__ == '__main__':
    main()
