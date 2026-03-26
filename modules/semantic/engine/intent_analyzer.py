"""
Intent Analyzer - 意图分析器

使用AI大模型分析用户查询意图
支持 OpenAI API 调用，无API时使用基于规则的降级方案
"""

import os
import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class IntentAnalyzer:
    """
    意图分析器

    功能:
    1. 分析用户查询意图（主题、类型、范围）
    2. 生成搜索关键词
    3. 推荐数据来源

    使用LLM API时：
    - 调用 OpenAI API 进行语义分析
    - 无API时使用基于规则的分析
    """

    # 默认的停用词（用于关键词过滤）
    STOP_WORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
        '自己', '这', '那', '么', '什么', '怎么', '如何', '为什么', '吗', '呢', '吧', '啊',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it'
    }

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.use_llm = bool(self.api_key)

    def analyze(self, query: str) -> Dict:
        """
        分析用户查询意图

        Args:
            query: 用户输入的自然语言查询

        Returns:
            Dict: {
                intent: str,          # 意图类型 (research/news/tech/product)
                keywords: List[str],  # 生成的关键词
                entities: List[str],  # 识别的实体
                suggested_sources: List[str],  # 建议的数据源
                analysis: str         # 意图分析描述
            }
        """
        if self.use_llm:
            return self._analyze_with_llm(query)
        else:
            return self._analyze_fallback(query)

    def _analyze_with_llm(self, query: str) -> Dict:
        """使用LLM进行意图分析"""
        try:
            import openai

            prompt = f"""分析以下查询的意图，并生成搜索关键词。

查询: {query}

请以JSON格式返回:
{{
    "intent": "意图类型 (research/news/tech/product/general)",
    "keywords": ["关键词1", "关键词2", ...],
    "entities": ["实体1", "实体2", ...],
    "suggested_sources": ["源类型1", "源类型2"],
    "analysis": "一句话描述用户意图"
}}

要求:
- keywords 至少5个，最多10个
- 包含原始查询的核心主题词
- 添加相关的下位词和同义词"""

            response = openai.OpenAI(api_key=self.api_key).chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.warning(f"LLM分析失败，回退到规则分析: {e}")
            return self._analyze_fallback(query)

    def _analyze_fallback(self, query: str) -> Dict:
        """基于规则的意图分析（无API时使用）"""
        # 提取中文和英文词
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', query)

        # 过滤停用词
        keywords = [w for w in words if len(w) > 1 and w.lower() not in self.STOP_WORDS]

        # 如果没有提取到词，使用原始查询
        if not keywords:
            keywords = [query[:10]]

        # 识别意图类型
        query_lower = query.lower()
        if any(k in query_lower for k in ['新闻', '最新', '最近', '动态', 'news']):
            intent = 'news'
        elif any(k in query_lower for k in ['产品', '工具', '软件', 'app', 'product']):
            intent = 'product'
        elif any(k in query_lower for k in ['技术', '原理', '架构', '如何', 'tech']):
            intent = 'tech'
        else:
            intent = 'research'

        # 推荐数据源
        sources = ['duckduckgo', 'rss']
        if intent in ['news', 'research']:
            sources.append('wikipedia')

        return {
            'intent': intent,
            'keywords': keywords[:10],  # 最多10个
            'entities': keywords[:5],   # 实体取前5个
            'suggested_sources': sources,
            'analysis': f'用户想要了解关于"{query}"的{intent}类型信息'
        }


class KeywordGenerator:
    """
    关键词生成器

    从基础关键词扩展出更多相关搜索词
    """

    # 关键词扩展映射（简化版，实际可接入词向量或LLM）
    EXPANSION_PAIRS = {
        'AI': ['人工智能', '机器学习', '深度学习', '神经网络'],
        '人工智能': ['AI', '机器学习', '深度学习'],
        '大模型': ['LLM', 'GPT', 'ChatGPT', '语言模型'],
        'GPT': ['ChatGPT', 'OpenAI', '语言模型', '大模型'],
        '芯片': ['GPU', 'AI芯片', '半导体', 'NVIDIA'],
        '自动驾驶': ['无人车', '智能驾驶', 'Tesla', 'Waymo'],
    }

    def generate(self, base_keywords: List[str], intent: str = None) -> List[str]:
        """
        生成扩展关键词列表

        Args:
            base_keywords: 基础关键词列表
            intent: 意图类型

        Returns:
            List[str]: 扩展后的关键词列表
        """
        expanded = set(base_keywords)

        # 扩展每个关键词
        for kw in base_keywords:
            # 添加英文翻译（如果存在）
            for cn, en_list in self.EXPANSION_PAIRS.items():
                if cn in kw:
                    expanded.update(en_list)
                for en in en_list:
                    if en.lower() in kw.lower():
                        expanded.add(cn)
                        expanded.update(en_list)

        # 添加意图特定的词
        if intent == 'news':
            expanded.update(['最新', '新闻', '动态', '2024', '2025', '2026'])
        elif intent == 'product':
            expanded.update(['工具', '软件', '产品', '评测', '对比'])

        # 清理并返回
        result = [k for k in expanded if len(k) > 1]
        return result[:20]  # 最多20个关键词


class RelevanceScorer:
    """
    相关性评分器

    评估内容与查询的相关程度
    """

    def __init__(self, keywords: List[str]):
        self.keywords = keywords
        self.keyword_set = set(k.lower() for k in keywords)

    def score(self, title: str, summary: str = '', content: str = '') -> float:
        """
        计算内容与查询的相关性评分

        Args:
            title: 内容标题
            summary: 内容摘要
            content: 内容正文

        Returns:
            float: 相关性评分 (0-1)
        """
        if not title:
            return 0.0

        # 合并所有文本
        text = f"{title} {summary} {content}".lower()

        # 计算关键词出现次数
        matches = 0
        for kw in self.keyword_set:
            if kw.lower() in text:
                matches += 1

        # 基础分数 = 匹配关键词数 / 总关键词数
        if not self.keyword_set:
            return 0.5

        base_score = matches / len(self.keyword_set)

        # 标题命中加权
        title_matches = sum(1 for kw in self.keyword_set if kw.lower() in title.lower())
        title_bonus = title_matches * 0.1

        # 综合评分（0-1范围）
        score = min(1.0, base_score + title_bonus)

        return score

    def extract_entities(self, text: str) -> List[Dict]:
        """
        从文本中提取实体

        Args:
            text: 文本内容

        Returns:
            List[Dict]: 实体列表 [{"name": "实体名", "type": "类型"}, ...]
        """
        entities = []

        # 简单模式匹配（可升级为NER模型）
        # 公司名模式
        company_patterns = [
            r'([A-Z][a-zA-Z]+(?:AI|Inc|Labs|Corp|Ltd))',
            r'([\u4e00-\u9fff]{2,10}(?:公司|集团|实验室|研究院))'
        ]

        # 产品名模式
        product_patterns = [
            r'([A-Z][a-z]+(?:GPT|LLM|Claude|Gemini))',
            r'([\u4e00-\u9fff]{2,10}(?:产品|工具|平台|系统))'
        ]

        for pattern in company_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'name': match.group(1),
                    'type': 'ORG'
                })

        for pattern in product_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'name': match.group(1),
                    'type': 'PRODUCT'
                })

        # 去重
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e['name'], e['type'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)

        return unique_entities[:20]  # 最多20个实体
