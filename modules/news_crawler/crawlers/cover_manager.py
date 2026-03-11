#!/usr/bin/env python3
"""
封面图管理模块
- 默认封面图库
- 封面图获取策略
"""

# 默认封面图URL（高质量免费图库）
DEFAULT_COVERS = {
    # 科技风 - 电路板/芯片图案
    'tech': [
        'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800',
        'https://images.unsplash.com/photo-1526374965328-7f61d7dc42f9?w=800',
    ],
    # AI风 - 神经网络/机器人
    'ai': [
        'https://images.unsplash.com/photo-1677442136019-21785ec2d986?w=800',
        'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800',
        'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800',
    ],
    # 未来风 - 城市/星空
    'future': [
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
        'https://images.unsplash.com/photo-1419242902214-272b3f66ee3a?w=800',
        'https://images.unsplash.com/photo-1534794158-375d0c73d1bc?w=800',
    ]
}

import random
import requests
import os

def get_random_cover(category=None):
    """获取随机默认封面图"""
    if category and category in DEFAULT_COVERS:
        covers = DEFAULT_COVERS[category]
    else:
        # 随机选择分类
        covers = []
        for c in DEFAULT_COVERS.values():
            covers.extend(c)
    
    return random.choice(covers)

def download_default_covers():
    """下载所有默认封面到本地"""
    save_dir = '/home/zhang/.copaw/news_system/data/covers'
    os.makedirs(save_dir, exist_ok=True)
    
    downloaded = []
    for category, urls in DEFAULT_COVERS.items():
        for i, url in enumerate(urls):
            try:
                # 下载图片
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    # 保存
                    filename = f"{category}_{i+1}.jpg"
                    filepath = os.path.join(save_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(resp.content)
                    downloaded.append(filepath)
                    print(f"下载成功: {filename}")
            except Exception as e:
                print(f"下载失败 {url}: {e}")
    
    return downloaded

def get_cover_with_fallback(article_image=None, og_image=None):
    """
    智能获取封面图
    优先级: 文章图片 > og:image > 默认图
    """
    # 1. 优先使用文章图片
    if article_image and is_valid_image(article_image):
        return article_image
    
    # 2. 其次使用og:image
    if og_image and is_valid_image(og_image):
        return og_image
    
    # 3. 返回随机默认图
    return get_random_cover()

def is_valid_image(url):
    """验证图片URL是否有效"""
    if not url:
        return False
    
    # 检查是否是有效的图片URL
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return any(url.lower().endswith(ext) for ext in valid_extensions) or 'image' in url.lower()

if __name__ == "__main__":
    print("下载默认封面图...")
    download_default_covers()
    print("完成!")
