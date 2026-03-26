"""
RSS Collector - RSS订阅采集器

从高质量RSS源采集内容，过滤与主题相关的条目
"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    """
    RSS 订阅采集器

    功能:
    - 从预定义的高质量RSS源采集
    - 按关键词过滤相关内容
    - 支持时间范围过滤
    """

    name = "rss"
    source_type = "rss"

    # 高质量RSS源列表
    DEFAULT_FEEDS = [
        # AI/科技
        {'name': 'HackerNews', 'url': 'https://hnrss.org/frontpage', 'keywords': ['AI', 'tech', 'startup']},
        {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/', 'keywords': ['startup', 'tech']},
        {'name': 'Ars Technica', 'url': 'https://feeds.arstechnica.com/arstechnica/index', 'keywords': ['tech', 'science']},
        {'name': 'The Verge', 'url': 'https://www.theverge.com/rss/index.xml', 'keywords': ['tech', 'gadgets']},
        {'name': 'MIT Tech Review', 'url': 'https://www.technologyreview.com/feed/', 'keywords': ['AI', 'tech']},
        # 中文科技
        {'name': '36kr', 'url': 'https://36kr.com/feed', 'keywords': ['科技', '创业', 'AI']},
        {'name': '机器之心', 'url': 'https://RSSHub', 'keywords': ['AI', '机器学习']},
        {'name': '量子位', 'url': 'https://RSSHub', 'keywords': ['AI', '量子']},
    ]

    def __init__(self, feeds: List[Dict] = None):
        super().__init__()
        self.feeds = feeds or self.DEFAULT_FEEDS

    def fetch(self, keywords: List[str], config: dict = None) -> List[Dict]:
        """
        从RSS源采集并过滤相关内容

        Args:
            keywords: 关键词列表（用于过滤）
            config: {max_items: int, days: int} 最大数量和时间范围

        Returns:
            List[Dict]: 相关内容列表
        """
        max_items = config.get('max_items', 50) if config else 50
        days = config.get('days', 7) if config else 7  # 默认7天内
        keyword_set = set(k.lower() for k in keywords)

        results = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for feed in self.feeds:
            if len(results) >= max_items:
                break

            try:
                items = self._fetch_feed(feed['url'], feed['name'], keyword_set, cutoff_date)
                results.extend(items)
                self.stats['requests'] += 1
            except Exception as e:
                logger.warning(f"RSS采集失败 [{feed['name']}]: {e}")
                self.stats['errors'] += 1

        # 按发布时间排序
        results.sort(key=lambda x: x.get('published_at') or '', reverse=True)

        self.stats['items'] = len(results)
        return results[:max_items]

    def _fetch_feed(self, url: str, feed_name: str, keyword_set: set,
                   cutoff_date: datetime) -> List[Dict]:
        """获取并过滤单个RSS源"""
        results = []

        try:
            import feedparser

            feed = feedparser.parse(url)

            for entry in feed.entries[:30]:  # 每源最多30条
                try:
                    # 提取标题和摘要
                    title = getattr(entry, 'title', '') or ''
                    summary = getattr(entry, 'summary', '') or ''
                    content = getattr(entry, 'content', [{}])[0].get('value', '') if hasattr(entry, 'content') else ''

                    # 清理HTML标签
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                    # 提取发布时间
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            from time import mktime
                            pub_dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                            published_at = pub_dt.strftime('%Y-%m-%d %H:%M:%S')

                            # 时间过滤
                            if pub_dt < cutoff_date:
                                continue
                        except:
                            pass

                    # 关键词匹配
                    text = f"{title} {summary}".lower()
                    matches = sum(1 for kw in keyword_set if kw in text)

                    if matches == 0 and keyword_set:
                        continue  # 没有匹配的关键词，跳过

                    # 计算相关性分数
                    relevance = matches / len(keyword_set) if keyword_set else 0.5

                    results.append({
                        'title': title.strip(),
                        'summary': summary.strip(),
                        'content': content[:2000] if content else '',
                        'url': getattr(entry, 'link', ''),
                        'source_name': feed_name,
                        'source_url': url,
                        'published_at': published_at,
                        'relevance_score': min(1.0, relevance + 0.3)  # 基础分0.3
                    })

                except Exception as e:
                    logger.warning(f"解析RSS条目失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"RSS解析失败 [{url}]: {e}")
            raise

        return results


# 便捷函数
def fetch_rss(keywords: List[str], max_items: int = 50) -> List[Dict]:
    """从RSS源采集相关内容"""
    collector = RSSCollector()
    return collector.fetch(keywords, {'max_items': max_items})
