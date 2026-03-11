"""
Centralized configuration module.
Re-exports path constants from path_utils and adds Flask settings.
"""

import os
from path_utils import (
    PROJECT_ROOT, DATA_DIR, NEWS_DB, SKILLS_DB, SUBSCRIBE_DB,
    VERSION_HISTORY_DIR, DOCS_DIR, get_project_root, get_db_path
)

SECRET_KEY = 'news-system-secret-key'
DEBUG = False
