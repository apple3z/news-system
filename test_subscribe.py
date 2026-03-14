import requests

# 测试订阅列表API
r = requests.get('http://localhost:5000/api/subscribe/feed?page=1&per_page=3')
data = r.json()

print('订阅列表API:')
for item in data.get('data', [])[:3]:
    print(f"  {item['id']}: {item.get('title')[:30] if item.get('title') else 'No title'}")

first_id = data.get('data', [{}])[0].get('id')

print(f'\n详情页API (ID {first_id}):')
r2 = requests.get(f'http://localhost:5000/api/subscribe/{first_id}')
d = r2.json()
print('Keys:', list(d.get('data', {}).keys()))
content = d.get('data', {}).get('content', '')
print('Content length:', len(content) if content else 'No content')
if content:
    print('Content preview:', content[:200])
