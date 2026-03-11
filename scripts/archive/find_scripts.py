#!/usr/bin/env python3
import re
with open('/home/zhang/.copaw/news_system/app.py', 'r') as f:
    content = f.read()
    
# Find all script tags
matches = list(re.finditer(r'<script', content))
print(f"Found {len(matches)} script tags")
for m in matches:
    line_num = content[:m.start()].count('\n') + 1
    print(f"Line {line_num}")
    
# Find end script tags
end_matches = list(re.finditer(r'</script>', content))
print(f"\nFound {len(end_matches)} end script tags")
for m in end_matches:
    line_num = content[:m.start()].count('\n') + 1
    print(f"Line {line_num}")
