"""
Skills API routes.
Public: /api/skills/search, /api/skills/categories
Admin: /api/admin/skills CRUD, /api/admin/skills/categories, /api/admin/skills/crawl
"""

from flask import jsonify, request
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import skills_service, crawler_service
from utils.auth import login_required


# ========== Public Skills API ==========

@news_crawler_bp.route('/api/skills/search')
def api_skills_search():
    """Search skills (public)."""
    keyword = request.args.get('keyword', '')
    data = skills_service.search_skills_public(keyword=keyword)
    return jsonify({'code': 200, 'data': data})


@news_crawler_bp.route('/api/skills/categories')
def api_skills_categories_public():
    """Get skill categories (public)."""
    categories = skills_service.get_categories()
    return jsonify({'code': 200, 'data': categories})


@news_crawler_bp.route('/api/skills/<int:skill_id>')
def api_skills_detail(skill_id):
    """Get single skill detail (public, no login required)."""
    skill = skills_service.get_skill(skill_id)
    if not skill:
        return jsonify({'code': 404, 'message': 'Skill not found'})
    return jsonify({'code': 200, 'data': skill})


@news_crawler_bp.route('/api/skills/rankings')
def api_skills_rankings():
    """Get skills ranking by stars (public)."""
    limit = request.args.get('limit', 20, type=int)
    data = skills_service.get_skill_rankings(limit=limit)
    return jsonify({'code': 200, 'data': data})


# ========== Admin Skills API ==========

@news_crawler_bp.route('/api/admin/skills')
@login_required
def api_admin_skills_list():
    """Get skills list (admin)."""
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    rows = skills_service.list_skills(keyword=keyword, category=category)
    return jsonify({'code': 200, 'data': rows, 'total': len(rows)})


@news_crawler_bp.route('/api/admin/skills/categories')
@login_required
def api_admin_skills_categories():
    """Get skill categories (admin)."""
    cats = skills_service.get_categories()
    return jsonify({'code': 200, 'data': cats})


@news_crawler_bp.route('/api/admin/skills/<int:skill_id>')
@login_required
def api_admin_skills_get(skill_id):
    """Get single skill detail."""
    skill = skills_service.get_skill(skill_id)
    if not skill:
        return jsonify({'code': 404, 'message': 'Skill not found'})
    return jsonify({'code': 200, 'data': skill})


@news_crawler_bp.route('/api/admin/skills', methods=['POST'])
@login_required
def api_admin_skills_create():
    """Create a new skill."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'code': 400, 'message': 'Name is required'})

    new_id = skills_service.create_skill(data)
    return jsonify({'code': 200, 'message': 'Created', 'id': new_id})


@news_crawler_bp.route('/api/admin/skills/<int:skill_id>', methods=['PUT'])
@login_required
def api_admin_skills_update(skill_id):
    """Update an existing skill."""
    data = request.get_json()
    found = skills_service.update_skill(skill_id, data)
    if not found:
        return jsonify({'code': 404, 'message': 'Skill not found'})
    return jsonify({'code': 200, 'message': 'Updated'})


@news_crawler_bp.route('/api/admin/skills/<int:skill_id>', methods=['DELETE'])
@login_required
def api_admin_skills_delete(skill_id):
    """Delete a skill."""
    skills_service.delete_skill(skill_id)
    return jsonify({'code': 200, 'message': 'Deleted'})


@news_crawler_bp.route('/api/admin/skills/crawl', methods=['POST'])
@login_required
def api_admin_skills_crawl():
    """Trigger skills crawler."""
    try:
        crawler_service.start_skills_crawl()
        return jsonify({'code': 200, 'message': 'Skills crawler started'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})
