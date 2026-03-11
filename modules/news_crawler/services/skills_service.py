"""
Skills service layer.
Business logic for skills operations, delegates to skills_dal.
"""

from modules.news_crawler.dal import skills_dal


def list_skills(keyword='', category=''):
    """List skills with optional filters (admin)."""
    return skills_dal.list_skills(keyword=keyword, category=category)


def get_skill(skill_id):
    """Get a single skill by ID."""
    return skills_dal.get_skill(skill_id)


def create_skill(data):
    """Create a new skill."""
    return skills_dal.create_skill(data)


def update_skill(skill_id, data):
    """Update an existing skill."""
    return skills_dal.update_skill(skill_id, data)


def delete_skill(skill_id):
    """Delete a skill."""
    return skills_dal.delete_skill(skill_id)


def get_categories():
    """Get skill categories."""
    return skills_dal.get_categories()


def search_skills_public(keyword=''):
    """Search skills for public API."""
    return skills_dal.search_skills_public(keyword=keyword)


def get_all_skills_simple():
    """Get all skills for listing page."""
    return skills_dal.get_all_skills_simple()
