"""
统一采集服务层
管理新闻、Skills、RSS的采集调度
"""

import sys
from threading import Thread
from config import PROJECT_ROOT
from modules.news_crawler.dal.datasource_dal import (
    create_crawl_log, update_crawl_log
)


def start_news_crawl():
    """启动新闻采集（后台线程）"""
    def run_crawl():
        try:
            from modules.news_crawler.crawlers.fetch_news import fetch_news
            fetch_news()
        except Exception as e:
            print(f"News crawl failed: {e}")

    thread = Thread(target=run_crawl, daemon=True)
    thread.start()


def start_skills_crawl():
    """启动Skills采集（后台线程）"""
    def run_crawl():
        try:
            from modules.news_crawler.crawlers.fetch_skills import fetch_skills
            fetch_skills()
        except Exception as e:
            print(f"Skills crawl failed: {e}")

    thread = Thread(target=run_crawl, daemon=True)
    thread.start()


def start_rss_crawl():
    """启动RSS订阅检查（后台线程）"""
    def run_crawl():
        try:
            if PROJECT_ROOT not in sys.path:
                sys.path.insert(0, PROJECT_ROOT)
            from subscribe_manager import check_all_subscriptions
            check_all_subscriptions()
        except Exception as e:
            print(f"RSS crawl failed: {e}")

    thread = Thread(target=run_crawl, daemon=True)
    thread.start()


def start_unified_crawl(crawl_type='full'):
    """
    统一采集入口
    crawl_type: full / news / skill / rss
    """
    if crawl_type not in ('full', 'news', 'skill', 'rss'):
        return {'code': 400, 'message': '无效的采集类型'}

    log_id = create_crawl_log(crawl_type)

    def run_unified():
        total = 0
        new_count = 0
        updated = 0
        detail = {}
        try:
            if crawl_type in ('full', 'news'):
                try:
                    from modules.news_crawler.crawlers.fetch_news import fetch_news
                    result = fetch_news() or {}
                    total += result.get('total', 0)
                    new_count += result.get('new', 0)
                    updated += result.get('updated', 0)
                    detail['news'] = 'completed'
                    detail['news_detail'] = result.get('detail', [])
                except Exception as e:
                    detail['news'] = f'failed: {e}'

            if crawl_type in ('full', 'skill'):
                try:
                    from modules.news_crawler.crawlers.fetch_skills import fetch_skills
                    skill_result = fetch_skills() or {}
                    total += skill_result.get('total', 0)
                    new_count += skill_result.get('new', 0)
                    updated += skill_result.get('updated', 0)
                    detail['skill'] = 'completed'
                except Exception as e:
                    detail['skill'] = f'failed: {e}'

            if crawl_type in ('full', 'rss'):
                try:
                    if PROJECT_ROOT not in sys.path:
                        sys.path.insert(0, PROJECT_ROOT)
                    from subscribe_manager import check_all_subscriptions
                    check_all_subscriptions()
                    detail['rss'] = 'completed'
                except Exception as e:
                    detail['rss'] = f'failed: {e}'

            update_crawl_log(log_id, 'completed', total, new_count, updated, detail)
        except Exception as e:
            update_crawl_log(log_id, 'failed', total, new_count, updated,
                             {'error': str(e), **detail})

    thread = Thread(target=run_unified, daemon=True)
    thread.start()

    type_names = {'full': '全量采集', 'news': '新闻采集', 'skill': 'Skills采集', 'rss': 'RSS采集'}
    return {'code': 200, 'message': f'{type_names[crawl_type]}已启动', 'log_id': log_id}
