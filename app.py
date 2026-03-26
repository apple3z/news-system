#!/usr/bin/env python3
"""
Web服务主入口 - 前后端分离架构 (v4.0)
Backend: Flask API via modular blueprints (modules/)
Frontend: Vue 3 SPA (frontend/)
"""

import os
import sys

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datetime import timedelta
from flask import Flask, send_from_directory

# 创建 Flask 应用
app = Flask(__name__)
app.secret_key = 'news-system-secret-key'
app.permanent_session_lifetime = timedelta(minutes=30)

# ========== 初始化模块（触发 proxy 注册） ==========
import modules.news_crawler  # noqa: registers news.search_by_keywords with proxy
import modules.sys_admin      # noqa

# ========== 注册 API 蓝图 ==========
from modules.news_crawler.routes import news_crawler_bp
from modules.sys_admin.routes import sys_admin_bp
from modules.news_crawler.kernel.api.kernel_api import kernel_bp
from modules.semantic.routes.semantic_api import semantic_bp

app.register_blueprint(news_crawler_bp)
app.register_blueprint(sys_admin_bp)
app.register_blueprint(kernel_bp)
app.register_blueprint(semantic_bp)

# ========== 初始化表结构 ==========
from modules.news_crawler.dal.subscribe_dal import ensure_tables as ensure_subscribe_tables
from modules.sys_admin.dal.auth_dal import ensure_tables as ensure_auth_tables
from modules.news_crawler.dal.datasource_dal import ensure_tables as ensure_ds_tables
from modules.news_crawler.dal.datasource_dal import seed_default_sources
from modules.news_crawler.kernel.dal.task_dal import ensure_kernel_tables
ensure_subscribe_tables()
ensure_auth_tables()
ensure_ds_tables()
seed_default_sources()
ensure_kernel_tables()

# ========== 初始化语义爬虫 ==========
from modules.semantic.dal.semantic_dal import ensure_tables as ensure_semantic_tables
ensure_semantic_tables()
print("[Semantic] 语义爬虫模块已就绪")

# ========== 初始化爬虫内核 ==========
from modules.news_crawler.kernel.dal.task_dal import list_tasks
from modules.news_crawler.kernel import DEFAULT_TASKS, init_kernel

# 检查是否已有任务，没有则创建默认任务
existing_tasks = list_tasks()
if not existing_tasks:
    print("[Kernel] 初始化默认任务...")
    kernel = init_kernel()
    for task_template in DEFAULT_TASKS:
        kernel.create_task(task_template)
    print(f"[Kernel] 已创建 {len(DEFAULT_TASKS)} 个默认任务")
else:
    print(f"[Kernel] 发现 {len(existing_tasks)} 个已存在任务，跳过初始化")

# 启动内核调度器
kernel = init_kernel()
print("[Kernel] 爬虫内核已启动")

# ========== 前端静态资源 ==========
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')


@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)


# ========== SPA catch-all ==========
@app.route('/')
@app.route('/news/<path:path>')
@app.route('/skills')
@app.route('/skill/<path:path>')
@app.route('/subscribe')
@app.route('/sys')
@app.route('/sys/<path:path>')
def spa_catch_all(path=''):
    return send_from_directory(FRONTEND_DIR, 'index.html')


# ========== 启动服务 ==========
if __name__ == "__main__":
    print("=" * 50)
    print("Web服务 v4.0 启动! (前后端分离架构)")
    print("前端 SPA: http://localhost:5000")
    print("API: http://localhost:5000/api/...")
    print("后台管理: http://localhost:5000/sys")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
