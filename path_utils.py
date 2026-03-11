#!/usr/bin/env python3
"""
跨平台路径工具模块
统一处理 Windows/Linux 路径适配
"""

import os
import platform


def get_project_root():
    """
    智能获取项目根目录，自动适配 Windows/Linux
    
    策略：
    1. 优先使用脚本所在目录（最准确）
    2. 检测是否有版本历史/文档中心目录
    3. 检查 Linux 部署路径
    4. 默认使用当前工作目录
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # 方法 1: 使用当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查当前目录是否有版本历史/文档中心
    if os.path.exists(os.path.join(current_dir, '版本历史')) or \
       os.path.exists(os.path.join(current_dir, '文档中心')):
        return current_dir
    
    # 方法 2: 检查是否在 Linux 环境且有指定路径
    if platform.system() == 'Linux':
        linux_paths = [
            '/home/zhang/news_system',
            '/opt/news_system',
            '/var/www/news_system'
        ]
        for path in linux_paths:
            if os.path.exists(path):
                return path
    
    # 默认返回当前目录
    return current_dir


def get_data_dir():
    """
    获取数据目录路径
    
    Returns:
        str: 数据目录的绝对路径
    """
    return os.path.join(get_project_root(), 'data')


def get_db_path(db_name):
    """
    获取数据库文件路径
    
    Args:
        db_name (str): 数据库文件名（如 'news.db'）
    
    Returns:
        str: 数据库文件的绝对路径
    """
    return os.path.join(get_data_dir(), db_name)


def ensure_data_dir():
    """
    确保数据目录存在，不存在则创建
    
    Returns:
        str: 数据目录的绝对路径
    """
    data_dir = get_data_dir()
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_version_history_dir():
    """
    获取版本历史目录路径
    
    Returns:
        str: 版本历史目录的绝对路径
    """
    return os.path.join(get_project_root(), '版本历史')


def get_docs_dir():
    """
    获取文档中心目录路径
    
    Returns:
        str: 文档中心目录的绝对路径
    """
    return os.path.join(get_project_root(), '文档中心')


# 预定义常用路径
PROJECT_ROOT = get_project_root()
DATA_DIR = get_data_dir()
VERSION_HISTORY_DIR = get_version_history_dir()
DOCS_DIR = get_docs_dir()

# 数据库路径
NEWS_DB = get_db_path('news.db')
SKILLS_DB = get_db_path('skills.db')
SUBSCRIBE_DB = get_db_path('subscribe.db')


if __name__ == '__main__':
    """测试路径工具"""
    print("=" * 50)
    print("跨平台路径工具测试")
    print("=" * 50)
    print(f"操作系统：{platform.system()} {platform.release()}")
    print(f"项目根目录：{PROJECT_ROOT}")
    print(f"数据目录：{DATA_DIR}")
    print(f"版本历史目录：{VERSION_HISTORY_DIR}")
    print(f"文档中心目录：{DOCS_DIR}")
    print(f"新闻数据库：{NEWS_DB}")
    print(f"Skills 数据库：{SKILLS_DB}")
    print(f"订阅数据库：{SUBSCRIBE_DB}")
    print("=" * 50)
    
    # 验证路径
    print("\n路径验证:")
    print(f"  项目根目录存在：{os.path.exists(PROJECT_ROOT)}")
    print(f"  数据目录存在：{os.path.exists(DATA_DIR)}")
    print(f"  版本历史存在：{os.path.exists(VERSION_HISTORY_DIR)}")
    print(f"  文档中心存在：{os.path.exists(DOCS_DIR)}")
