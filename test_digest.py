#!/usr/bin/env python3
"""
测试订阅摘要页面权重显示
"""
import requests

print("测试 API 返回的数据")
print("=" * 80)

try:
    # 测试源列表 API
    res = requests.get("http://localhost:5000/api/subscribe/sources")
    if res.status_code == 200:
        data = res.json()
        print(f"\n✓ 源列表 API 正常")
        print(f"  返回数据：{data}")
        
        if data.get('code') == 200:
            sources = data.get('data', [])
            print(f"  源数量：{len(sources)}")
            if sources:
                print(f"  第一个源：{sources[0]}")
    else:
        print(f"✗ HTTP {res.status_code}")
        
except Exception as e:
    print(f"✗ 错误：{e}")

print("\n" + "=" * 80)
