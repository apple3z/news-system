"""
CrawlerPlugin 基类

所有采集插件必须继承此基类并实现抽象方法
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class FetchResult:
    """采集结果"""
    success: bool = False
    items: List[Dict] = field(default_factory=list)
    error: str = None
    metadata: Dict = field(default_factory=dict)


class CrawlerPlugin(ABC):
    """
    爬虫插件抽象基类

    使用方式:
    1. 继承此类，实现 fetch() 和 store() 方法
    2. 可选重写 parse(), validate(), normalize() 方法
    3. 在 CrawlerKernel 中注册插件
    """

    name: str = "base"
    supported_types: List[str] = []

    def __init__(self):
        self._stats = {'fetch': 0, 'parse': 0, 'store': 0}

    @abstractmethod
    def fetch(self, source: Dict, config: Dict) -> FetchResult:
        """
        从数据源采集原始数据

        Args:
            source: 数据源信息 {id, name, url, config}
            config: 采集配置参数

        Returns:
            FetchResult: 包含 items 列表
        """
        pass

    def parse(self, result: FetchResult, config: Dict) -> FetchResult:
        """
        解析采集结果，提取结构化数据

        默认实现直接返回原结果，子类可重写
        """
        self._stats['parse'] += 1
        return result

    def validate(self, result: FetchResult, config: Dict) -> FetchResult:
        """
        验证数据有效性

        默认实现过滤无标题或标题过短的数据
        """
        if result.items:
            result.items = [
                item for item in result.items
                if item.get('title') and len(str(item.get('title', ''))) > 5
            ]
        return result

    def normalize(self, result: FetchResult, config: Dict) -> FetchResult:
        """
        标准化数据格式

        默认实现为空，子类可重写统一字段名称、格式
        """
        return result

    @abstractmethod
    def store(self, result: FetchResult, config: Dict) -> Dict:
        """
        存储解析后的数据到数据库

        Args:
            result: FetchResult 对象
            config: 存储配置

        Returns:
            Dict: {total, new, updated}
        """
        pass

    def get_stats(self) -> Dict:
        """获取插件统计"""
        return self._stats.copy()

    def reset_stats(self):
        """重置统计"""
        self._stats = {'fetch': 0, 'parse': 0, 'store': 0}
