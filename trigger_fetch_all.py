#!/usr/bin/env python3
"""
触发所有订阅源的重新采集
"""
import sys
sys.path.insert(0, '.')

from subscribe_manager import check_for_updates, get_subscriptions

print("=" * 80)
print("触发所有订阅源重新采集")
print("=" * 80)

subs = get_subscriptions()
print(f"\n共 {len(subs)} 个活跃订阅源\n")

success = 0
failed = 0
skipped = 0

for sub in subs:
    sub_id, name, url, sub_type, check_interval, last_check, last_content, is_active, created_at = sub
    print(f"\n{'-' * 80}")
    print(f"[{sub_id}] {name} ({sub_type})")
    
    try:
        result = check_for_updates(sub_id)
        if result:
            success += 1
            print(f"  ✓ 采集成功")
        else:
            skipped += 1
            print(f"  ⊘ 无更新")
    except Exception as e:
        failed += 1
        print(f"  ✗ 采集失败：{e}")

print(f"\n{'=' * 80}")
print(f"完成：成功 {success} 个，跳过 {skipped} 个，失败 {failed} 个")
print(f"{'=' * 80}")
