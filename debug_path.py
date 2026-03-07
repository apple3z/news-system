import os

VERSION_HISTORY_DIR = '/home/zhang/.copaw/news_system/版本历史/'
filename = 'v2.4/PRD.md'
version_prefix = 'v2.4'
filename_only = 'PRD.md'

# Test path
test_path = os.path.join(VERSION_HISTORY_DIR, version_prefix, filename_only)
print(f'Checking path: {test_path}')
print(f'Exists: {os.path.exists(test_path)}')

# List all files in VERSION_HISTORY_DIR
print(f'\nFiles in {VERSION_HISTORY_DIR}:')
for root, dirs, files in os.walk(VERSION_HISTORY_DIR):
    for f in files:
        print(f'  {os.path.join(root, f)}')
