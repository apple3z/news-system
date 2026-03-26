"""
RSSPlugin - RSS订阅采集插件

复用 subscribe_manager.py 的采集逻辑，适配插件接口
"""

import logging
from typing import Dict
from modules.news_crawler.kernel.plugins.base import CrawlerPlugin, FetchResult

logger = logging.getLogger(__name__)


class RSSPlugin(CrawlerPlugin):
    """RSS订阅采集插件"""

    name = "rss"
    supported_types = ["rss"]

    def fetch(self, source: Dict, config: Dict) -> FetchResult:
        """
        从RSS源采集数据

        Args:
            source: {id, name, url, sub_type, config}
            config: 采集配置

        Returns:
            FetchResult: 包含采集到的订阅内容列表
        """
        try:
            sub_type = source.get('sub_type', 'rss')
            url = source.get('url', '')

            if not url:
                return FetchResult(success=False, error='URL为空')

            items = []

            if sub_type == 'rss' or 'rss' in source.get('config', {}).get('rss', True):
                # 使用feedparser解析
                items = self._parse_rss(source)
            elif sub_type == 'website':
                # 网站HTML抓取（简化实现）
                items = self._fetch_website(source)
            else:
                # 默认尝试RSS解析
                items = self._parse_rss(source)

            self._stats['fetch'] += 1
            return FetchResult(
                success=True,
                items=items,
                metadata={'source': source.get('name'), 'count': len(items)}
            )

        except Exception as e:
            logger.error(f"RSSPlugin fetch error: {source.get('name')}: {e}")
            return FetchResult(success=False, error=str(e))

    def _parse_rss(self, source: Dict) -> list:
        """使用feedparser解析RSS"""
        from modules.news_crawler.crawlers.subscribe_manager import parse_rss_feed

        url = source.get('url', '')
        name = source.get('name', '')

        items = parse_rss_feed(url)

        # 标准化格式
        result = []
        for item in items:
            result.append({
                'sub_id': source.get('id'),
                'sub_name': name,
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'summary': item.get('summary', ''),
                'content': item.get('content', ''),
                'author': item.get('author', ''),
                'thumbnail': item.get('thumbnail', ''),
                'detected_at': item.get('detected_at', '')
            })

        return result

    def _fetch_website(self, source: Dict) -> list:
        """抓取网站内容（简化实现）"""
        # 简化实现：返回空列表
        # 完整实现需要参考 subscribe_manager.py 的网站抓取逻辑
        return []

    def store(self, result: FetchResult, config: Dict) -> Dict:
        """
        存储订阅内容到数据库

        Returns:
            Dict: {total, new, updated}
        """
        from modules.news_crawler.dal.subscribe_dal import save_subscription_history

        total = 0
        new_count = 0
        updated_count = 0

        for item in result.items:
            try:
                saved = save_subscription_history(item)
                total += 1
                if saved:
                    new_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.warning(f"Failed to store subscription: {item.get('title', '')}: {e}")

        self._stats['store'] += total

        return {
            'total': total,
            'new': new_count,
            'updated': updated_count
        }
