#!/usr/bin/env python3
import json

# 读取现有版本文件
with open('/home/zhang/.copaw/news_system/doc/.versions.json', 'r') as f:
    versions = json.load(f)

# 添加V2.4文档
versions['v2.4/PRD.md'] = {
    'major': 1,
    'minor': 0,
    'patch': 1,
    'history': [
        {'version': '1.0.1', 'time': '2026-03-03 21:20:00', 'action': '创建'}
    ],
    'locked': False,
    'last_update': '2026-03-03 21:20:00'
}

versions['v2.4/ARCH.md'] = {
    'major': 1,
    'minor': 0,
    'patch': 1,
    'history': [
        {'version': '1.0.1', 'time': '2026-03-03 21:21:00', 'action': '创建'}
    ],
    'locked': False,
    'last_update': '2026-03-03 21:21:00'
}

versions['v2.4/TDD.md'] = {
    'major': 1,
    'minor': 0,
    'patch': 1,
    'history': [
        {'version': '1.0.1', 'time': '2026-03-03 21:21:00', 'action': '创建'}
    ],
    'locked': False,
    'last_update': '2026-03-03 21:21:00'
}

versions['v2.4/更新介绍.md'] = {
    'major': 1,
    'minor': 0,
    'patch': 1,
    'history': [
        {'version': '1.0.1', 'time': '2026-03-03 21:22:00', 'action': '创建'}
    ],
    'locked': False,
    'last_update': '2026-03-03 21:22:00'
}

# 保存
with open('/home/zhang/.copaw/news_system/doc/.versions.json', 'w') as f:
    json.dump(versions, f, indent=2, ensure_ascii=False)

print('已添加V2.4文档到版本管理')
