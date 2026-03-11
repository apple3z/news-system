#!/usr/bin/env python3
"""
测试脚本 - 验证系统功能
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test(name, url, expected_status=200, check_json=True):
    """测试单个接口"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    print('-'*60)
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"❌ 失败: 期望状态码 {expected_status}, 实际 {response.status_code}")
            return False
        
        if check_json:
            try:
                data = response.json()
                print(f"JSON响应: {json.dumps(data, ensure_ascii=False)[:500]}...")
                
                if data.get('code') == 200 or data.get('code') == 0:
                    print(f"✅ 通过")
                    return True
                else:
                    print(f"❌ 失败: API返回错误 {data.get('code')}")
                    return False
            except:
                print(f"⚠️ 警告: 响应不是JSON格式")
                print(f"内容: {response.text[:200]}...")
        
        print(f"✅ 通过")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_post(name, url, data=None, expected_status=200):
    """测试POST请求"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    print(f"数据: {data}")
    print('-'*60)
    try:
        if data:
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.post(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"❌ 失败: 期望状态码 {expected_status}, 实际 {response.status_code}")
            return False
        
        try:
            result = response.json()
            print(f"JSON响应: {json.dumps(result, ensure_ascii=False)[:500]}...")
            print(f"✅ 通过")
            return True
        except:
            print(f"⚠️ 警告: 响应不是JSON格式")
            print(f"内容: {response.text[:200]}...")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def main():
    print("="*60)
    print("新闻系统功能测试")
    print("="*60)
    
    results = []
    
    # 1. 测试新闻首页
    results.append(test("新闻首页", f"{BASE_URL}/"))
    
    # 2. 测试新闻筛选 - 关键词搜索
    results.append(test("新闻搜索 - 关键词", f"{BASE_URL}/?keyword=AI"))
    
    # 3. 测试新闻筛选 - 分类
    results.append(test("新闻筛选 - 分类", f"{BASE_URL}/?category=科技"))
    
    # 4. 测试新闻筛选 - 排序
    results.append(test("新闻筛选 - 排序", f"{BASE_URL}/?sort_by=hot_score"))
    
    # 5. 测试新闻 API - 搜索
    results.append(test("新闻API - 搜索", f"{BASE_URL}/api/news/search?keyword=AI"))
    
    # 6. 测试新闻 API - 分类列表
    results.append(test("新闻API - 分类列表", f"{BASE_URL}/api/news/categories"))
    
    # 7. 测试新闻 API - 来源列表
    results.append(test("新闻API - 来源列表", f"{BASE_URL}/api/news/sources"))
    
    # 8. 测试系统管理首页
    results.append(test("系统管理首页", f"{BASE_URL}/sys"))
    
    # 9. 测试系统管理 API - 爬虫日志
    results.append(test("系统管理API - 爬虫日志", f"{BASE_URL}/api/admin/crawl-logs"))
    
    # 10. 测试版本历史列表
    results.append(test("版本历史列表", f"{BASE_URL}/api/v2/doc/list?path=版本历史"))
    
    # 11. 测试文档中心列表
    results.append(test("文档中心列表", f"{BASE_URL}/api/v2/doc/list?path=文档中心"))
    
    # 12. 测试读取文档
    results.append(test("读取文档", f"{BASE_URL}/api/v2/doc/read?path=文档中心/SYS_ARCH.md"))
    
    # 13. 测试保存文档
    results.append(test_post("保存文档", f"{BASE_URL}/api/v2/doc/save", {
        "path": "文档中心/测试文档.md",
        "content": "# 测试文档\n\n这是测试内容",
        "author": "测试"
    }))
    
    # 14. 测试新建文档
    results.append(test_post("新建文档", f"{BASE_URL}/api/v2/doc/create", {
        "path": "文档中心/测试新建.md",
        "content": "# 新建测试",
        "author": "测试"
    }))
    
    # 15. 测试删除文档
    results.append(test_post("删除文档", f"{BASE_URL}/api/v2/doc/delete", {
        "path": "文档中心/测试新建.md"
    }))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过!")
    else:
        print(f"❌ 有 {total - passed} 个测试失败")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
