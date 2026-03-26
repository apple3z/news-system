"""
Analyzer Service - 分析服务

提供词云生成、趋势计算、数据分析功能
"""

import re
import logging
from collections import Counter
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalyzerService:
    """
    分析服务

    功能:
    1. 词云生成 - 从文本提取高频词
    2. 趋势计算 - 按时间统计内容量
    3. 实体提取 - 识别人名/公司/产品
    4. 摘要生成 - 生成内容摘要
    """

    # 中文停用词
    CN_STOPWORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
        '自己', '这', '那', '么', '什么', '怎么', '如何', '为什么', '吗', '呢', '吧', '啊',
        '但', '却', '因为', '所以', '如果', '虽然', '然后', '而且', '并且', '或者',
        '以及', '对于', '关于', '通过', '使用', '进行', '能够', '可以', '已经',
        '我们', '你们', '他们', '她们', '它们', '这个', '那个', '这些', '那些',
        '还是', '只是', '只有', '都是', '同时', '此外', '另外', '总之', '因此'
    }

    # 英文停用词
    EN_STOPWORDS = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'when',
        'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here',
        'there', 'then', 'once', 'if', 'or', 'and', 'but', 'in', 'at', 'on',
        'by', 'with', 'about', 'against', 'between', 'into', 'through', 'during'
    }

    STOPWORDS = CN_STOPWORDS | EN_STOPWORDS

    def generate_wordcloud_data(self, items: List[Dict], top_n: int = 50) -> Dict:
        """
        从内容生成词云数据

        Args:
            items: 内容列表 [{title, summary, content}, ...]
            top_n: 返回前N个高频词

        Returns:
            Dict: {words: [{text, size}, ...]}
        """
        word_counter = Counter()

        for item in items:
            text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
            words = self._extract_words(text)

            for word in words:
                if word and len(word) > 1:
                    word_counter[word] += 1

        # 取最高频的词
        common = word_counter.most_common(top_n)

        # 计算字体大小（基于频率）
        max_count = common[0][1] if common else 1
        min_count = common[-1][1] if common else 1

        words_data = []
        for word, count in common:
            # 归一化大小到 14-72 范围
            if max_count > min_count:
                normalized = (count - min_count) / (max_count - min_count)
                size = int(14 + normalized * 58)
            else:
                size = 36

            words_data.append({
                'text': word,
                'size': size,
                'count': count
            })

        return {'words': words_data}

    def calculate_trend(self, items: List[Dict]) -> Dict:
        """
        计算内容热度趋势

        Args:
            items: 内容列表 [{published_at, ...}, ...]

        Returns:
            Dict: {dates: [...], counts: [...], peak_date: str}
        """
        # 按日期统计
        date_counter = Counter()
        peak_date = None
        peak_count = 0

        for item in items:
            published_at = item.get('published_at')
            if not published_at:
                continue

            try:
                # 解析日期
                if isinstance(published_at, str):
                    if ' ' in published_at:
                        date_str = published_at.split(' ')[0]
                    else:
                        date_str = published_at[:10]
                else:
                    date_str = str(published_at)[:10]

                if date_str and len(date_str) >= 10:
                    date_counter[date_str] += 1

                    if date_counter[date_str] > peak_count:
                        peak_count = date_counter[date_str]
                        peak_date = date_str
            except:
                continue

        # 生成时间序列（最近30天）
        today = datetime.now()
        dates = []
        counts = []

        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            dates.append(date_str)
            counts.append(date_counter.get(date_str, 0))

        return {
            'dates': dates,
            'counts': counts,
            'peak_date': peak_date,
            'peak_count': peak_count,
            'total': sum(counts)
        }

    def extract_entities(self, items: List[Dict]) -> Dict:
        """
        从内容中提取实体

        Args:
            items: 内容列表

        Returns:
            Dict: {companies: [...], products: [...], persons: [...]}
        """
        companies = Counter()
        products = Counter()
        persons = Counter()

        for item in items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"

            # 简单模式匹配（可升级为NER模型）

            # 公司名检测
            company_patterns = [
                r'([A-Z][a-zA-Z]+(?:AI|Inc|Labs|Corp|Ltd|Co|Company))',
                r'([\u4e00-\u9fff]{2,8}(?:公司|集团|企业|实验室|研究院))'
            ]

            for pattern in company_patterns:
                for match in re.finditer(pattern, text):
                    name = match.group(1).strip()
                    if len(name) > 2:
                        companies[name] += 1

            # 产品名检测
            product_patterns = [
                r'([A-Z][a-z]+(?:GPT|LLM|Claude|Gemini|Sora|o1|4|5|6|7))',
                r'([\u4e00-\u9fff]{2,10}(?:产品|工具|平台|系统|服务))'
            ]

            for pattern in product_patterns:
                for match in re.finditer(pattern, text):
                    name = match.group(1).strip()
                    if len(name) > 2:
                        products[name] += 1

        # 返回前10个
        return {
            'companies': [{'name': n, 'count': c} for n, c in companies.most_common(10)],
            'products': [{'name': n, 'count': c} for n, c in products.most_common(10)],
            'persons': [{'name': n, 'count': c} for n, c in persons.most_common(10)]
        }

    def generate_summary(self, items: List[Dict], max_length: int = 500) -> str:
        """
        生成内容摘要

        Args:
            items: 内容列表
            max_length: 最大摘要长度

        Returns:
            str: 摘要文本
        """
        if not items:
            return "暂无相关数据"

        # 收集所有标题和摘要
        summaries = []
        for item in items[:10]:  # 取前10条
            title = item.get('title', '')
            summary = item.get('summary', '')
            if title:
                summaries.append(f"【{title}】{summary[:100]}")

        combined = ' '.join(summaries)

        # 截断到最大长度
        if len(combined) > max_length:
            combined = combined[:max_length] + '...'

        return combined

    def _extract_words(self, text: str) -> List[str]:
        """从文本中提取有意义的词"""
        # 提取中文词
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,6}', text)

        # 提取英文词
        en_words = re.findall(r'[a-zA-Z]{3,20}', text)

        # 过滤停用词
        cn_filtered = [w for w in cn_words if w not in self.STOPWORDS]
        en_filtered = [w.lower() for w in en_words if w.lower() not in self.STOPWORDS]

        return cn_filtered + en_filtered

    def get_source_distribution(self, items: List[Dict]) -> List[Dict]:
        """
        获取来源分布统计

        Args:
            items: 内容列表

        Returns:
            List[Dict]: [{source: str, count: int}, ...]
        """
        source_counter = Counter()

        for item in items:
            source = item.get('source_name', 'Unknown')
            source_counter[source] += 1

        return [
            {'source': s, 'count': c}
            for s, c in source_counter.most_common(20)
        ]
