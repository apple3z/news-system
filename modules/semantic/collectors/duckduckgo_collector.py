"""
DuckDuckGo Collector - DuckDuckGo搜索采集器

通过DuckDuckGo搜索发现相关网站和内容
无需API key，免费使用
"""

import requests
import re
import logging
from typing import List, Dict
from datetime import datetime
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class DuckDuckGoCollector(BaseCollector):
    """
    DuckDuckGo 搜索采集器

    功能:
    - 搜索关键词，获取相关结果
    - 抓取搜索结果摘要
    - 自动发现相关网站
    """

    name = "duckduckgo"
    source_type = "duckduckgo"

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def fetch(self, keywords: List[str], config: dict = None) -> List[Dict]:
        """
        通过DuckDuckGo搜索采集内容

        Args:
            keywords: 搜索关键词列表
            config: {max_items: int} 最多采集数量

        Returns:
            List[Dict]: 搜索结果列表
        """
        max_items = config.get('max_items', 30) if config else 30
        results = []

        for keyword in keywords[:5]:  # 最多搜5个关键词
            if len(results) >= max_items:
                break

            try:
                items = self._search(keyword, max_items - len(results))
                results.extend(items)
                self.stats['requests'] += 1
            except Exception as e:
                logger.error(f"DuckDuckGo搜索失败 [{keyword}]: {e}")
                self.stats['errors'] += 1

        # 去重（按URL）
        seen_urls = set()
        unique_results = []
        for item in results:
            if item['url'] and item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_results.append(item)

        self.stats['items'] = len(unique_results)
        return unique_results[:max_items]

    def _search(self, keyword: str, max_results: int = 30) -> List[Dict]:
        """
        执行DuckDuckGo搜索

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            List[Dict]: 搜索结果
        """
        results = []

        try:
            # DuckDuckGo HTML搜索
            url = f"https://html.duckduckgo.com/html/"
            params = {'q': keyword}

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 解析HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # 搜索结果在 .result 类中
            for result in soup.select('.result')[:max_results]:
                try:
                    # 标题和链接
                    link_elem = result.select_one('.result__a')
                    if not link_elem:
                        continue

                    title = link_elem.get_text(strip=True)
                    url = link_elem.get('href', '')

                    # 摘要
                    snippet = result.select_one('.result__snippet')
                    summary = snippet.get_text(strip=True) if snippet else ''

                    # 清理摘要中的额外空白
                    summary = re.sub(r'\s+', ' ', summary)

                    results.append({
                        'title': title,
                        'summary': summary,
                        'content': '',
                        'url': url,
                        'source_name': f'DuckDuckGo: {keyword}',
                        'source_url': f'https://duckduckgo.com/?q={keyword}',
                        'published_at': None  # 搜索结果无发布时间
                    })

                except Exception as e:
                    logger.warning(f"解析搜索结果失败: {e}")
                    continue

        except requests.RequestException as e:
            logger.error(f"DuckDuckGo请求失败: {e}")
            raise

        return results


# 便捷函数
def search_duckduckgo(keywords: List[str], max_items: int = 30) -> List[Dict]:
    """
    使用DuckDuckGo搜索关键词

    Args:
        keywords: 关键词列表
        max_items: 最大结果数

    Returns:
        List[Dict]: 搜索结果
    """
    collector = DuckDuckGoCollector()
    return collector.fetch(keywords, {'max_items': max_items})
