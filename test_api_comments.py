#!/usr/bin/env python3
"""
测试 API 是否返回 comments 字段
"""
import requests

print("测试 API 返回的 comments 字段")
print("=" * 80)

try:
    # 测试列表 API
    res = requests.get("http://localhost:5000/api/subscribe/feed?per_page=5")
    if res.status_code == 200:
        data = res.json()
        if data.get('code') == 200 and data.get('data'):
            print("\n✓ 列表 API 正常")
            first = data['data'][0]
            print(f"\n第一个条目字段：{list(first.keys())}")
            print(f"  comments: {first.get('comments', 'N/A')}")
            
            # 测试详情 API
            first_id = first['id']
            res_detail = requests.get(f"http://localhost:5000/api/subscribe/{first_id}")
            if res_detail.status_code == 200:
                detail = res_detail.json()
                if detail.get('code') == 200:
                    print(f"\n✓ 详情 API 正常")
                    print(f"  comments: {detail['data'].get('comments', 'N/A')}")
        else:
            print(f"✗ API 返回错误：{data}")
    else:
        print(f"✗ HTTP {res.status_code}")
        
except Exception as e:
    print(f"✗ 错误：{e}")

print("\n" + "=" * 80)
