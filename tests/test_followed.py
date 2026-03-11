#!/usr/bin/env python3
"""测试关注新闻 API"""

import requests
import json

url = "http://localhost:5000/api/admin/followed-news"
data = {
    "title": "AI大模型",
    "keywords": ["AI", "大模型", "GPT"],
    "description": "关注AI大模型相关新闻"
}

response = requests.post(url, json=data)
print("响应状态码:", response.status_code)
print("响应内容:", json.dumps(response.json(), indent=2, ensure_ascii=False))

# 获取列表
print("\n--- 获取关注新闻列表 ---")
response = requests.get(url)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
