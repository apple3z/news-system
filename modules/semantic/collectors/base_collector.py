"""
Base Collector - 采集器基类

定义采集器的接口规范
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseCollector(ABC):
    """
    采集器基类

    所有采集器必须继承此类并实现 fetch 方法
    """

    name: str = "base"
    source_type: str = "base"

    def __init__(self):
        self.stats = {
            'requests': 0,
            'items': 0,
            'errors': 0
        }

    @abstractmethod
    def fetch(self, keywords: List[str], config: dict = None) -> List[Dict]:
        """
        根据关键词采集内容

        Args:
            keywords: 搜索关键词列表
            config: 采集配置 {max_items: int, ...}

        Returns:
            List[Dict]: 采集到的内容列表
            [{
                title: str,
                summary: str,
                content: str,
                url: str,
                source_name: str,
                source_url: str,
                published_at: str
            }, ...]
        """
        pass

    def get_stats(self) -> Dict:
        """获取采集统计"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'requests': 0,
            'items': 0,
            'errors': 0
        }
