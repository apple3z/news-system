"""
Wikipedia Collector - Wikipedia API采集器

从Wikipedia获取背景知识和相关实体
"""

import requests
import re
import logging
from typing import List, Dict
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class WikipediaCollector(BaseCollector):
    """
    Wikipedia API 采集器

    功能:
    - 搜索相关页面
    - 获取页面摘要
    - 提取相关链接
    """

    name = "wikipedia"
    source_type = "wikipedia"

    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'NewsSystemBot/1.0 (Semantic Crawler)',
            'Accept': 'application/json'
        }

    def fetch(self, keywords: List[str], config: dict = None) -> List[Dict]:
        """
        从Wikipedia获取相关内容

        Args:
            keywords: 关键词列表
            config: {max_items: int} 最大数量

        Returns:
            List[Dict]: Wikipedia页面列表
        """
        max_items = config.get('max_items', 20) if config else 20
        results = []

        for keyword in keywords[:5]:  # 最多搜5个关键词
            if len(results) >= max_items:
                break

            try:
                items = self._search_wikipedia(keyword, max_items - len(results))
                results.extend(items)
                self.stats['requests'] += 1
            except Exception as e:
                logger.warning(f"Wikipedia搜索失败 [{keyword}]: {e}")
                self.stats['errors'] += 1

        # 去重
        seen_titles = set()
        unique_results = []
        for item in results:
            if item['title'] and item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_results.append(item)

        self.stats['items'] = len(unique_results)
        return unique_results[:max_items]

    def _search_wikipedia(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """搜索Wikipedia"""
        results = []

        try:
            # 搜索API
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': keyword,
                'srlimit': max_results,
                'format': 'json'
            }

            response = requests.get(
                self.API_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            search_results = data.get('query', {}).get('search', [])

            for item in search_results:
                # 获取摘要
                summary = self._get_summary(item['pageid'])

                results.append({
                    'title': item['title'],
                    'summary': summary or item.get('snippet', ''),
                    'content': '',
                    'url': f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                    'source_name': 'Wikipedia',
                    'source_url': self.API_URL,
                    'published_at': None,
                    'page_id': item['pageid'],
                    'word_count': item.get('wordcount', 0)
                })

        except requests.RequestException as e:
            logger.error(f"Wikipedia API请求失败: {e}")
            raise

        return results

    def _get_summary(self, page_id: int) -> str:
        """获取页面摘要"""
        try:
            params = {
                'action': 'query',
                'pageids': page_id,
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'exsentences': 3,
                'format': 'json'
            }

            response = requests.get(
                self.API_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            if page_id in pages:
                return pages[page_id].get('extract', '')

        except Exception as e:
            logger.warning(f"获取Wikipedia摘要失败 [{page_id}]: {e}")

        return ''


# 便捷函数
def fetch_wikipedia(keywords: List[str], max_items: int = 20) -> List[Dict]:
    """从Wikipedia获取相关内容"""
    collector = WikipediaCollector()
    return collector.fetch(keywords, {'max_items': max_items})
