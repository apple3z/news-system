#!/usr/bin/env python3
import shutil
import os

src_dir = '/home/zhang/.copaw/news_system/doc'
dst_base = '/home/zhang/.copaw/news_system'

# Copy v1.0
for f in os.listdir(f'{src_dir}/v1.0'):
    src = f'{src_dir}/v1.0/{f}'
    dst = f'{dst_base}/版本历史/v1.0/{f}'
    shutil.copy2(src, dst)
    print(f'Copied v1.0/{f}')

# Copy v2.4
for f in os.listdir(f'{src_dir}/v2.4'):
    src = f'{src_dir}/v2.4/{f}'
    dst = f'{dst_base}/版本历史/v2.4/{f}'
    shutil.copy2(src, dst)
    print(f'Copied v2.4/{f}')

# Copy v2.5
for f in os.listdir(f'{src_dir}/v2.5'):
    src = f'{src_dir}/v2.5/{f}'
    dst = f'{dst_base}/版本历史/v2.5/{f}'
    shutil.copy2(src, dst)
    print(f'Copied v2.5/{f}')

# Copy docs to 文档中心
for f in os.listdir(f'{src_dir}/docs'):
    src = f'{src_dir}/docs/{f}'
    dst = f'{dst_base}/文档中心/{f}'
    shutil.copy2(src, dst)
    print(f'Copied 文档中心/{f}')

print('Done!')
