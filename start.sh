#!/bin/bash
# News System 快速启动脚本 (Linux/Mac)
# 前后端分离架构 v4.0

echo "=================================================="
echo "  News System 启动脚本 (v4.0)"
echo "=================================================="

# 检查数据库
if [ ! -f "data/news.db" ]; then
    echo "检测到数据库不存在，正在初始化..."
    python3 scripts/init_db.py
fi

# 启动应用
echo ""
echo "正在启动 News System 服务..."
echo "前端 SPA：http://localhost:5000"
echo "系统管理：http://localhost:5000/sys"
echo "API：http://localhost:5000/api/..."
echo ""
echo "按 Ctrl+C 停止服务"
echo "=================================================="

python3 app.py
