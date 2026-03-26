"""
Crawler Kernel - 爬虫内核模块

核心组件:
- CrawlerKernel: 单例，管理任务和插件
- TaskScheduler: 基于APScheduler的调度器
- CrawlerPlugin: 插件基类

默认任务模板:
- 每日全量采集 (cron: 8:30)
- 每小时RSS更新 (interval: 3600s)
- 每日Skills同步 (cron: 9:00)
"""

from modules.news_crawler.kernel.core import CrawlerKernel

# 默认任务模板
DEFAULT_TASKS = [
    {
        'name': '每日全量采集',
        'task_type': 'news',
        'trigger_type': 'cron',
        'trigger_config': {'hour': 8, 'minute': 30},
        'pipeline': ['fetch', 'parse', 'store'],
        'config': {'max_items_per_source': 50},
        'enabled': True
    },
    {
        'name': '每小时RSS更新',
        'task_type': 'rss',
        'trigger_type': 'interval',
        'trigger_config': {'seconds': 3600},
        'pipeline': ['fetch', 'parse', 'store'],
        'config': {},
        'enabled': True
    },
    {
        'name': '每日Skills同步',
        'task_type': 'skills',
        'trigger_type': 'cron',
        'trigger_config': {'hour': 9, 'minute': 0},
        'pipeline': ['fetch', 'parse', 'store'],
        'config': {'batch_size': 15},
        'enabled': True
    }
]


def init_kernel():
    """初始化爬虫内核"""
    kernel = CrawlerKernel()
    return kernel


def get_kernel():
    """获取内核单例"""
    return CrawlerKernel()
