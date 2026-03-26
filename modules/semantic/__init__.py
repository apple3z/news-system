"""
Semantic Crawler - 语义爬虫模块

功能:
- 语义理解：AI大模型分析用户意图
- 全网爬虫：自动发现和采集相关内容
- 数据分析：词云 + 热度趋势图

使用方式:
1. 创建任务: POST /api/semantic/tasks
2. 查询状态: GET /api/semantic/tasks/<id>/status
3. 获取结果: GET /api/semantic/tasks/<id>/results
"""

from modules.semantic.services.semantic_service import SemanticEngine

__version__ = "2.8.0"


def get_engine():
    """获取语义引擎单例"""
    return SemanticEngine()
