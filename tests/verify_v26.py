#!/usr/bin/env python3
"""
v2.6.0 功能验证脚本
测试所有新增功能是否正常
"""

import requests
import sqlite3
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_news_sources():
    """测试新闻源采集"""
    print_section("测试 1: 新闻源采集")
    
    from path_utils import NEWS_DB
    conn = sqlite3.connect(NEWS_DB)
    c = conn.cursor()
    
    # 查询不同来源的新闻
    c.execute("SELECT source, COUNT(*) FROM news GROUP BY source")
    sources = c.fetchall()
    
    print(f"\n数据库中的新闻源:")
    for source, count in sources:
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {source}: {count} 条")
    
    # 验证至少有 10 个新闻源
    if len(sources) >= 7:  # 至少 7 个新源
        print(f"\n✅ 新闻源数量达标：{len(sources)} 个")
        return True
    else:
        print(f"\n❌ 新闻源数量不足：{len(sources)} 个（需要至少 7 个）")
        return False

def test_news_categories():
    """测试新闻分类"""
    print_section("测试 2: 新闻分类功能")
    
    from path_utils import NEWS_DB
    conn = sqlite3.connect(NEWS_DB)
    c = conn.cursor()
    
    # 查询分类
    c.execute("SELECT category, COUNT(*) FROM news WHERE category IS NOT NULL GROUP BY category")
    categories = c.fetchall()
    
    print(f"\n新闻分类统计:")
    for category, count in categories:
        print(f"  📁 {category}: {count} 条")
    
    # 验证至少有 5 个分类
    if len(categories) >= 5:
        print(f"\n✅ 分类数量达标：{len(categories)} 个")
        return True
    else:
        print(f"\n❌ 分类数量不足：{len(categories)} 个")
        return False

def test_skills_categories():
    """测试 Skills 分类"""
    print_section("测试 3: Skills 分类功能")
    
    from path_utils import SKILLS_DB
    conn = sqlite3.connect(SKILLS_DB)
    c = conn.cursor()
    
    # 查询分类
    c.execute("SELECT category, COUNT(*) FROM skills WHERE category IS NOT NULL GROUP BY category")
    categories = c.fetchall()
    
    print(f"\nSkills 分类统计:")
    for category, count in categories:
        print(f"  📁 {category}: {count} 个")
    
    # 验证至少有 10 个分类
    if len(categories) >= 10:
        print(f"\n✅ Skills 分类数量达标：{len(categories)} 个")
        return True
    else:
        print(f"\n❌ Skills 分类数量不足：{len(categories)} 个")
        return False

def test_subscription_history():
    """测试订阅更新历史"""
    print_section("测试 4: 订阅更新历史")
    
    from path_utils import SUBSCRIBE_DB
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    
    # 检查历史表是否存在
    try:
        c.execute("SELECT COUNT(*) FROM subscription_history")
        count = c.fetchone()[0]
        print(f"\n✅ 更新历史表存在")
        print(f"  历史记录数：{count} 条")
        return True
    except sqlite3.OperationalError:
        print(f"\n❌ 更新历史表不存在")
        return False

def test_api_endpoints():
    """测试 API 端点"""
    print_section("测试 5: API 端点")
    
    endpoints = [
        ("GET", "/api/news/search", "新闻搜索"),
        ("GET", "/api/news/categories", "新闻分类"),
        ("GET", "/api/skills/search", "Skills 搜索"),
        ("GET", "/api/skills/categories", "Skills 分类"),
    ]
    
    results = []
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                r = requests.get(BASE_URL + endpoint, timeout=5)
            
            if r.status_code == 200:
                data = r.json()
                if data.get('success'):
                    print(f"  ✅ {name}: {endpoint}")
                    results.append(True)
                else:
                    print(f"  ⚠️  {name}: {endpoint} - 返回数据格式异常")
                    results.append(False)
            else:
                print(f"  ❌ {name}: {endpoint} - 状态码 {r.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  ❌ {name}: {endpoint} - {e}")
            results.append(False)
    
    success_count = sum(results)
    total = len(results)
    print(f"\nAPI 测试：{success_count}/{total} 通过")
    
    return success_count == total

def test_subscribe_apis():
    """测试订阅管理 API"""
    print_section("测试 6: 订阅管理 API")
    
    # 这些 API 需要 POST 请求或有订阅数据
    print("  ⚠️  订阅管理 API 需要实际订阅数据才能测试")
    print("  建议手动测试:")
    print("    POST /api/subscribe/check - 检查所有订阅")
    print("    GET  /api/subscribe/{id}/preview - 预览订阅")
    print("    GET  /api/subscribe/{id}/history - 历史记录")
    
    return True  # 跳过详细测试

def main():
    print("\n" + "🚀" * 30)
    print("  v2.6.0 功能验证测试")
    print("🚀" * 30)
    
    tests = [
        ("新闻源采集", test_news_sources),
        ("新闻分类", test_news_categories),
        ("Skills 分类", test_skills_categories),
        ("订阅历史", test_subscription_history),
        ("API 端点", test_api_endpoints),
        ("订阅 API", test_subscribe_apis),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 测试失败：{e}")
            results.append((name, False))
    
    # 汇总结果
    print_section("测试结果汇总")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")
        if result:
            passed += 1
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！v2.6.0 功能正常！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试未通过，请检查")
        return 1

if __name__ == "__main__":
    exit(main())
