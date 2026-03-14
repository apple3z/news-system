import requests

r = requests.get('http://localhost:5000/api/skills/search')
data = r.json()
skills = data.get('data', [])

below_50 = [s for s in skills if not s.get('stars') or s.get('stars') <= 50]
print(f'Stars <= 50 or None: {len(below_50)}')
if below_50:
    for s in below_50[:10]:
        print(f"{s['name']}: {s.get('stars')}")
else:
    print('All skills have stars > 50')

print(f'\nTotal skills: {len(skills)}')
print(f'All have stars: {all(s.get("stars") for s in skills)}')
