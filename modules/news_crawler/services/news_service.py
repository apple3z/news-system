"""
News service layer.
Business logic for news operations, delegates to news_dal.
"""

from modules.news_crawler.dal import news_dal


def search_news(keyword='', category='', source='', date_from='', date_to='',
                sort_by='time', sort_order='desc', page=1, per_page=20):
    """Search news with filters and pagination."""
    return news_dal.search_news(
        keyword=keyword, category=category, source=source,
        date_from=date_from, date_to=date_to,
        sort_by=sort_by, sort_order=sort_order,
        page=page, per_page=per_page
    )


def get_news_by_id(news_id):
    """Get a single news item by ID."""
    return news_dal.get_news_by_id(news_id)


def get_categories():
    """Get all news categories."""
    return news_dal.get_categories()


def get_sources():
    """Get all news sources."""
    return news_dal.get_sources()


def get_crawl_logs(page=1, per_page=10):
    """Get crawl log history."""
    return news_dal.get_crawl_logs(page=page, per_page=per_page)


def search_by_keywords(keywords):
    """Search news by keyword list. Registered with proxy for cross-module use."""
    return news_dal.search_by_keywords(keywords)


def get_daily_stats(days=30):
    """Get daily news count stats."""
    return news_dal.get_daily_stats(days)


def get_daily_stats_by_type(days=30):
    """Get daily stats grouped by source type (news/rss)."""
    return news_dal.get_daily_stats_by_type(days)


def get_crawl_daily_stats(days=30):
    """Get daily crawl stats."""
    return news_dal.get_crawl_daily_stats(days)
