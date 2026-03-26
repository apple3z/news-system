"""
SkillsPlugin - Skills采集插件

复用 fetch_skills.py 的采集逻辑，适配插件接口
"""

import logging
from typing import Dict
from modules.news_crawler.kernel.plugins.base import CrawlerPlugin, FetchResult

logger = logging.getLogger(__name__)


class SkillsPlugin(CrawlerPlugin):
    """Skills采集插件"""

    name = "skills"
    supported_types = ["skills"]

    def fetch(self, source: Dict, config: Dict) -> FetchResult:
        """
        从Skills源采集数据

        Args:
            source: {id, name, url, config, gh_owner, gh_repo}
            config: 采集配置 {batch_size, ...}

        Returns:
            FetchResult: 包含采集到的Skills列表
        """
        try:
            items = self._fetch_single_skill(source)

            self._stats['fetch'] += 1
            return FetchResult(
                success=True,
                items=items,
                metadata={'source': source.get('name'), 'count': len(items)}
            )

        except Exception as e:
            logger.error(f"SkillsPlugin fetch error: {source.get('name')}: {e}")
            return FetchResult(success=False, error=str(e))

    def _fetch_single_skill(self, source: Dict) -> list:
        """采集单个Skill"""
        from modules.news_crawler.crawlers.fetch_skills import (
            fetch_github_meta,
            fetch_readme,
            classify_skill
        )
        import requests

        gh_owner = source.get('gh_owner') or source.get('config', {}).get('gh_owner')
        gh_repo = source.get('gh_repo') or source.get('config', {}).get('gh_repo')

        if not gh_owner or not gh_repo:
            # 尝试从URL解析
            url = source.get('url', '')
            if 'github.com' in url:
                parts = url.rstrip('/').split('/')
                gh_owner = parts[-2] if len(parts) >= 2 else None
                gh_repo = parts[-1] if len(parts) >= 1 else None

        if not gh_owner or not gh_repo:
            return []

        # 获取GitHub元数据
        meta = fetch_github_meta(gh_owner, gh_repo)
        if not meta:
            return []

        # 获取README
        readme = fetch_readme(gh_owner, gh_repo)
        if readme == "404: Not Found":
            readme = ""

        # 构建Skill数据
        skill = {
            'name': source.get('name', ''),
            'owner': gh_owner,
            'title': meta.get('name') or source.get('name', ''),
            'description': meta.get('description', ''),
            'url': source.get('url', f'https://github.com/{gh_owner}/{gh_repo}'),
            'github_url': f'https://github.com/{gh_owner}/{gh_repo}',
            'stars': meta.get('stars', 0),
            'forks': meta.get('forks', 0),
            'topics': ','.join(meta.get('topics', [])),
            'language': meta.get('language', ''),
            'readme_content': readme,
            'skill_level': classify_skill(meta.get('topics', []), meta.get('stars', 0))
        }

        return [skill]

    def store(self, result: FetchResult, config: Dict) -> Dict:
        """
        存储Skills到数据库

        Returns:
            Dict: {total, new, updated}
        """
        from modules.news_crawler.dal.skills_dal import upsert_skill

        total = 0
        new_count = 0
        updated_count = 0

        for item in result.items:
            try:
                skill_id = upsert_skill(item)
                total += 1
                if skill_id and skill_id > 0:
                    new_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.warning(f"Failed to store skill: {item.get('name', '')}: {e}")

        self._stats['store'] += total

        return {
            'total': total,
            'new': new_count,
            'updated': updated_count
        }
