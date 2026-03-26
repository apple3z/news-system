"""
NewsPlugin - 新闻采集插件

复用 fetch_news.py 的采集逻辑，适配插件接口
"""

import logging
from typing import Dict
from modules.news_crawler.kernel.plugins.base import CrawlerPlugin, FetchResult

logger = logging.getLogger(__name__)


class NewsPlugin(CrawlerPlugin):
    """新闻采集插件"""

    name = "news"
    supported_types = ["news"]

    def fetch(self, source: Dict, config: Dict) -> FetchResult:
        """
        从新闻源采集数据

        Args:
            source: {id, name, url, config}
            config: 采集配置 {max_items_per_source, ...}

        Returns:
            FetchResult: 包含采集到的新闻列表
        """
        try:
            source_type = source.get('type', '')
            url = source.get('url', '')

            if not url:
                return FetchResult(success=False, error='URL为空')

            items = []

            if source_type == 'rss' or 'rss' in source.get('config', '').get('rss', False):
                # RSS 采集
                items = self._fetch_rss(source)
            else:
                # HTML 采集
                items = self._fetch_html(source)

            self._stats['fetch'] += 1
            return FetchResult(
                success=True,
                items=items,
                metadata={'source': source.get('name'), 'count': len(items)}
            )

        except Exception as e:
            logger.error(f"NewsPlugin fetch error: {source.get('name')}: {e}")
            return FetchResult(success=False, error=str(e))

    def _fetch_rss(self, source: Dict) -> list:
        """通过RSS采集新闻"""
        from modules.news_crawler.crawlers.fetch_news import fetch_from_rss

        url = source.get('url', '')
        name = source.get('name', '')

        result = fetch_from_rss(url, name, priority=source.get('priority', 10))

        if result and 'items' in result:
            return result['items']
        return []

    def _fetch_html(self, source: Dict) -> list:
        """通过HTML采集新闻"""
        # 对于HTML源，暂时返回空列表
        # 完整实现需要根据不同的源调用不同的采集函数
        return []

    def store(self, result: FetchResult, config: Dict) -> Dict:
        """
        存储新闻到数据库

        Returns:
            Dict: {total, new, updated}
        """
        from modules.news_crawler.dal.news_dal import upsert_news

        total = 0
        new_count = 0
        updated_count = 0

        for item in result.items:
            try:
                news_id = upsert_news(item)
                total += 1
                if news_id and news_id > 0:
                    # 新增
                    new_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.warning(f"Failed to store news: {item.get('title', '')}: {e}")

        self._stats['store'] += total

        return {
            'total': total,
            'new': new_count,
            'updated': updated_count
        }
