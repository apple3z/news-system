from flask import Blueprint

news_crawler_bp = Blueprint('news_crawler', __name__)

from . import news_api, skills_api, subscribe_api, crawl_api, datasource_api
