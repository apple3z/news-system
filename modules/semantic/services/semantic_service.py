"""
Semantic Service - 语义爬虫核心服务

整合意图分析、数据采集、相关性评分、分析展示
"""

import threading
import logging
from typing import Dict, List
from datetime import datetime

from modules.semantic.dal import semantic_dal as dal
from modules.semantic.engine.intent_analyzer import IntentAnalyzer, KeywordGenerator, RelevanceScorer
from modules.semantic.collectors.duckduckgo_collector import DuckDuckGoCollector
from modules.semantic.collectors.rss_collector import RSSCollector
from modules.semantic.collectors.wikipedia_collector import WikipediaCollector
from modules.semantic.services.analyzer_service import AnalyzerService

logger = logging.getLogger(__name__)


class SemanticEngine:
    """
    语义爬虫核心引擎

    功能:
    1. 创建和管理语义任务
    2. 执行语义分析（意图分析 + 数据采集 + 相关性过滤）
    3. 生成分析结果（词云、趋势等）
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.analyzer = IntentAnalyzer()
            self.keyword_gen = KeywordGenerator()
            self.analyzer_service = AnalyzerService()
            logger.info("SemanticEngine initialized")

    # ===== 任务管理 =====

    def create_task(self, name: str, user_query: str, config: dict = None) -> int:
        """
        创建语义任务

        Args:
            name: 任务名称
            user_query: 用户查询
            config: 任务配置

        Returns:
            int: 任务ID
        """
        config = config or {}
        task_id = dal.create_task(name, user_query, config)
        logger.info(f"Created semantic task {task_id}: {name}")
        return task_id

    def get_task(self, task_id: int) -> Dict:
        """获取任务"""
        return dal.get_task(task_id)

    def list_tasks(self, status: str = None, limit: int = 50) -> List[Dict]:
        """列出任务"""
        return dal.list_tasks(status, limit)

    def delete_task(self, task_id: int) -> Dict:
        """删除任务"""
        try:
            dal.delete_task(task_id)
            return {'code': 200, 'message': '删除成功'}
        except Exception as e:
            return {'code': 500, 'message': str(e)}

    # ===== 任务执行 =====

    def execute_task(self, task_id: int, async_mode: bool = True) -> Dict:
        """
        执行语义任务

        Args:
            task_id: 任务ID
            async_mode: 是否异步执行

        Returns:
            Dict: 执行结果
        """
        task = self.get_task(task_id)
        if not task:
            return {'code': 404, 'message': '任务不存在'}

        if task['status'] == 'running':
            return {'code': 409, 'message': '任务正在执行中'}

        if async_mode:
            thread = threading.Thread(
                target=self._execute,
                args=(task_id,),
                daemon=True
            )
            thread.start()
            return {'code': 200, 'message': '任务已启动', 'task_id': task_id}
        else:
            return self._execute(task_id)

    def _execute(self, task_id: int) -> Dict:
        """执行任务（内部调用）"""
        logger.info(f"Starting semantic task {task_id}")

        # 更新状态
        dal.update_task(task_id, {
            'status': 'running',
            'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        try:
            task = self.get_task(task_id)
            config = task.get('task_config', {}) or {}

            # Phase 1: 意图分析
            self._update_progress(task_id, 5, '分析用户意图...')
            intent_result = self.analyzer.analyze(task['user_query'])

            # 生成扩展关键词
            keywords = self.keyword_gen.generate(
                intent_result.get('keywords', []),
                intent_result.get('intent')
            )

            # 保存意图分析结果
            dal.update_task(task_id, {
                'generated_keywords': keywords,
                'intent_analysis': intent_result
            })
            self._update_progress(task_id, 10, '意图分析完成')

            # Phase 2: 数据采集
            sources_config = config.get('sources', ['duckduckgo', 'rss'])
            max_items = config.get('max_items', 100)
            items = []

            self._update_progress(task_id, 15, '开始采集数据...')

            # DuckDuckGo 采集
            if 'duckduckgo' in sources_config:
                self._update_progress(task_id, 20, 'DuckDuckGo搜索...')
                collector = DuckDuckGoCollector()
                ddg_items = collector.fetch(keywords, {'max_items': max_items // 2})
                items.extend(ddg_items)
                logger.info(f"DuckDuckGo: {len(ddg_items)} items")

                # 保存DuckDuckGo来源
                source_id = dal.save_source(task_id, 'duckduckgo', 'DuckDuckGo Search')

                # 保存采集内容
                for item in ddg_items:
                    item['relevance_score'] = RelevanceScorer(keywords).score(
                        item.get('title', ''),
                        item.get('summary', '')
                    )
                dal.save_items_batch(task_id, source_id, ddg_items)

            # RSS 采集
            if 'rss' in sources_config:
                self._update_progress(task_id, 40, 'RSS订阅采集...')
                collector = RSSCollector()
                rss_items = collector.fetch(keywords, {'max_items': max_items // 2})
                items.extend(rss_items)
                logger.info(f"RSS: {len(rss_items)} items")

                # 保存RSS来源
                source_id = dal.save_source(task_id, 'rss', 'RSS Feeds')

                # 保存采集内容
                for item in rss_items:
                    item['relevance_score'] = RelevanceScorer(keywords).score(
                        item.get('title', ''),
                        item.get('summary', '')
                    )
                dal.save_items_batch(task_id, source_id, rss_items)

            # Wikipedia 采集（可选）
            if 'wikipedia' in sources_config:
                self._update_progress(task_id, 60, 'Wikipedia知识补充...')
                collector = WikipediaCollector()
                wiki_items = collector.fetch(keywords, {'max_items': 20})
                items.extend(wiki_items)
                logger.info(f"Wikipedia: {len(wiki_items)} items")

                if wiki_items:
                    source_id = dal.save_source(task_id, 'wikipedia', 'Wikipedia')
                    for item in wiki_items:
                        item['relevance_score'] = RelevanceScorer(keywords).score(
                            item.get('title', ''),
                            item.get('summary', '')
                        )
                    dal.save_items_batch(task_id, source_id, wiki_items)

            self._update_progress(task_id, 75, f'采集完成，共{len(items)}条')

            # Phase 3: 相关性过滤
            self._update_progress(task_id, 80, '计算相关性...')
            relevance_threshold = config.get('relevance_threshold', 0.3)

            # 更新相关性分数
            for item in items:
                scorer = RelevanceScorer(keywords)
                item['relevance_score'] = scorer.score(
                    item.get('title', ''),
                    item.get('summary', ''),
                    item.get('content', '')
                )
                # 提取实体
                text = f"{item.get('title', '')} {item.get('summary', '')}"
                item['entities'] = scorer.extract_entities(text)
                item['keywords'] = keywords[:10]

            # 保存高相关内容
            relevant_items = [i for i in items if i['relevance_score'] >= relevance_threshold]
            self._update_progress(task_id, 85, f'筛选出{len(relevant_items)}条相关内容')

            # Phase 4: 生成分析结果
            self._update_progress(task_id, 90, '生成分析结果...')

            # 词云
            wordcloud = self.analyzer_service.generate_wordcloud_data(items, top_n=50)
            dal.save_result(task_id, 'wordcloud', wordcloud)

            # 趋势
            trend = self.analyzer_service.calculate_trend(items)
            dal.save_result(task_id, 'trend', trend)

            # 实体
            entities = self.analyzer_service.extract_entities(items)
            dal.save_result(task_id, 'entities', entities)

            # 来源分布
            sources_dist = self.analyzer_service.get_source_distribution(items)
            dal.save_result(task_id, 'sources', sources_dist)

            # 摘要
            summary = self.analyzer_service.generate_summary(relevant_items)
            dal.save_result(task_id, 'summary', {'text': summary})

            # 更新任务状态
            dal.update_task(task_id, {
                'status': 'completed',
                'progress': 100,
                'total_items': len(items),
                'relevant_items': len(relevant_items),
                'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            logger.info(f"Semantic task {task_id} completed: {len(items)} items, {len(relevant_items)} relevant")

            return {
                'code': 200,
                'task_id': task_id,
                'total_items': len(items),
                'relevant_items': len(relevant_items)
            }

        except Exception as e:
            logger.error(f"Semantic task {task_id} failed: {e}")
            dal.update_task(task_id, {
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            return {'code': 500, 'message': str(e)}

    def _update_progress(self, task_id: int, progress: int, message: str = ''):
        """更新任务进度"""
        dal.update_task(task_id, {'progress': progress})

    # ===== 结果获取 =====

    def get_results(self, task_id: int) -> Dict:
        """获取任务的分析结果"""
        results = dal.get_results(task_id)

        # 整理成结构化格式
        formatted = {
            'task_id': task_id,
            'wordcloud': None,
            'trend': None,
            'entities': None,
            'sources': None,
            'summary': None
        }

        for r in results:
            result_type = r.get('result_type')
            data = r.get('data')
            if result_type == 'wordcloud':
                formatted['wordcloud'] = data
            elif result_type == 'trend':
                formatted['trend'] = data
            elif result_type == 'entities':
                formatted['entities'] = data
            elif result_type == 'sources':
                formatted['sources'] = data
            elif result_type == 'summary':
                formatted['summary'] = data

        return formatted

    def get_sources(self, task_id: int) -> List[Dict]:
        """获取任务的来源列表"""
        return dal.get_sources(task_id)

    def get_items(self, task_id: int, min_relevance: float = 0, limit: int = 100) -> List[Dict]:
        """获取任务的内容列表"""
        return dal.get_items(task_id, min_relevance, limit)
