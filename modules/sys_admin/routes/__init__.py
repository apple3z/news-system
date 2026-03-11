from flask import Blueprint

sys_admin_bp = Blueprint('sys_admin', __name__)

from . import doc_api
