import requests

# 读取测试报告内容
with open('/home/zhang/.copaw/news_system/doc/docs/测试报告_v2.4.md', 'r') as f:
    content = f.read()

# 保存文档
r = requests.post('http://localhost:5000/api/wiki/测试报告_v2.4.md', json={'content': content, 'locked': False})
print(f"保存结果: {r.json()}")

# 检查版本
r2 = requests.get('http://localhost:5000/api/wiki/meta/测试报告_v2.4.md')
print(f"版本: {r2.json()}")
