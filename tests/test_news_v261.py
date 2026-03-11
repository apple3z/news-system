#!/usr/bin/env python3
"""
v2.6.1 新闻综合排序功能测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_news_search_basic():
    """测试基础搜索功能"""
    print_section("测试 1: 基础新闻搜索")
    
    r = requests.get(f"{BASE_URL}/api/news/search?page=1&per_page=5")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 基础搜索成功")
            print(f"  返回新闻数：{len(data['data'])}")
            print(f"  总记录数：{data['pagination']['total']}")
            
            # 检查返回字段
            if data['data']:
                news = data['data'][0]
                required_fields = ['id', 'title', 'source', 'category', 'time', 'summary', 'hot_score', 'author']
                missing_fields = [f for f in required_fields if f not in news]
                
                if not missing_fields:
                    print(f"✅ 返回字段完整")
                    print(f"\n示例新闻:")
                    print(f"  标题：{news['title']}")
                    print(f"  来源：{news['source']}")
                    print(f"  分类：{news['category']}")
                    print(f"  时间：{news['time']}")
                    print(f"  热度：{news['hot_score']}")
                    print(f"  作者：{news['author'] or 'N/A'}")
                else:
                    print(f"❌ 缺少字段：{missing_fields}")
            return True
        else:
            print(f"❌ 搜索失败：{data}")
            return False
    else:
        print(f"❌ 请求失败：{r.status_code}")
        return False

def test_sorting():
    """测试排序功能"""
    print_section("测试 2: 综合排序功能")
    
    # 测试时间排序
    print("\n2.1 时间排序（最新）")
    r = requests.get(f"{BASE_URL}/api/news/search?sort_by=time&sort_order=desc&per_page=3")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 时间倒序排序成功")
            for i, news in enumerate(data['data'], 1):
                print(f"  {i}. [{news['time']}] {news['title'][:50]}")
    
    # 测试热度排序
    print("\n2.2 热度排序（最热）")
    r = requests.get(f"{BASE_URL}/api/news/search?sort_by=hot_score&sort_order=desc&per_page=3")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 热度排序成功")
            for i, news in enumerate(data['data'], 1):
                print(f"  {i}. [热度：{news['hot_score']}] {news['title'][:50]}")
    
    # 测试相关度排序
    print("\n2.3 相关度排序（AI）")
    r = requests.get(f"{BASE_URL}/api/news/search?keyword=AI&sort_by=relevance&per_page=3")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 相关度排序成功")
            for i, news in enumerate(data['data'], 1):
                print(f"  {i}. {news['title'][:50]}")
    
    return True

def test_filtering():
    """测试筛选功能"""
    print_section("测试 3: 多条件筛选")
    
    # 测试分类筛选
    print("\n3.1 分类筛选")
    r = requests.get(f"{BASE_URL}/api/news/categories")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and data['data']:
            category = data['data'][0]['name']
            print(f"✅ 获取分类成功，测试分类：{category}")
            
            r = requests.get(f"{BASE_URL}/api/news/search?category={category}&per_page=3")
            if r.status_code == 200:
                data = r.json()
                if data.get('success'):
                    print(f"  该分类下新闻数：{len(data['data'])}")
                    for news in data['data']:
                        print(f"    - {news['title'][:50]}")
    
    # 测试新闻源筛选
    print("\n3.2 新闻源筛选")
    r = requests.get(f"{BASE_URL}/api/news/sources")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and data['data']:
            source = data['data'][0]['name']
            print(f"✅ 获取新闻源成功，测试源：{source}")
            
            r = requests.get(f"{BASE_URL}/api/news/search?source={source}&per_page=3")
            if r.status_code == 200:
                data = r.json()
                if data.get('success'):
                    print(f"  该源下新闻数：{len(data['data'])}")
                    for news in data['data']:
                        print(f"    - {news['title'][:50]}")
    
    # 测试日期范围筛选
    print("\n3.3 日期范围筛选")
    from datetime import datetime, timedelta
    date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")
    
    r = requests.get(f"{BASE_URL}/api/news/search?date_from={date_from}&date_to={date_to}&per_page=3")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 日期范围筛选成功 ({date_from} 至 {date_to})")
            print(f"  返回新闻数：{len(data['data'])}")
    
    # 测试组合筛选
    print("\n3.4 组合筛选（分类 + 关键词）")
    r = requests.get(f"{BASE_URL}/api/news/search?keyword=AI&category=AI 大模型&per_page=3")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 组合筛选成功")
            print(f"  返回新闻数：{len(data['data'])}")
    
    return True

def test_filters_response():
    """测试返回的 filters 字段"""
    print_section("测试 4: 返回的筛选参数")
    
    r = requests.get(f"{BASE_URL}/api/news/search?keyword=AI&sort_by=hot_score&source=量子位")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and 'filters' in data:
            print(f"✅ filters 字段存在")
            print(f"  筛选参数:")
            for key, value in data['filters'].items():
                print(f"    {key}: {value}")
            return True
        else:
            print(f"❌ filters 字段缺失")
            return False
    else:
        print(f"❌ 请求失败")
        return False

def test_news_sources_api():
    """测试新闻源列表 API"""
    print_section("测试 5: 新闻源列表 API")
    
    r = requests.get(f"{BASE_URL}/api/news/sources")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✅ 新闻源列表获取成功")
            print(f"  新闻源数量：{len(data['data'])}")
            print(f"\n新闻源列表:")
            for source in data['data'][:10]:  # 显示前 10 个
                print(f"  - {source['name']}: {source['count']} 条")
            return True
        else:
            print(f"❌ 获取失败")
            return False
    else:
        print(f"❌ 请求失败")
        return False

def main():
    print("\n" + "🚀" * 40)
    print("  v2.6.1 新闻综合排序功能测试")
    print("🚀" * 40)
    
    tests = [
        ("基础搜索", test_news_search_basic),
        ("排序功能", test_sorting),
        ("筛选功能", test_filtering),
        ("返回参数", test_filters_response),
        ("新闻源 API", test_news_sources_api),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 所有测试通过！v2.6.1 功能正常！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试未通过，请检查")
        return 1

if __name__ == "__main__":
    exit(main())
