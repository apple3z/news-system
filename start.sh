#!/bin/bash
# News System 启动脚本 v4.0

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║       News System 启动脚本 v4.0          ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 1. 检查 Python
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "  [错误] 未检测到 Python，请先安装 Python 3.8+"
    exit 1
fi

# 2. 检查端口占用
if lsof -i :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  [警告] 端口 5000 已被占用！"
    read -p "  输入 Y 关闭旧进程，N 退出 [Y/N]: " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        kill $(lsof -i :5000 -sTCP:LISTEN -t) 2>/dev/null
        echo "  已关闭旧进程"
        sleep 2
    else
        echo "  退出启动"
        exit 1
    fi
fi

# 3. 检查依赖
$PYTHON -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  [提示] 正在安装必要依赖..."
    pip install flask feedparser requests beautifulsoup4 lxml
    echo ""
fi

# 4. 初始化数据库
mkdir -p data
if [ ! -f "data/news.db" ]; then
    echo "  [初始化] 首次运行，正在创建数据库..."
    $PYTHON scripts/init_db.py
    echo ""
fi

# 5. 启动服务
echo "  ┌──────────────────────────────────────────┐"
echo "  │  前端首页:  http://localhost:5000         │"
echo "  │  后台管理:  http://localhost:5000/sys     │"
echo "  │  API文档:   http://localhost:5000/api/... │"
echo "  │  默认账号:  admin / admin123              │"
echo "  └──────────────────────────────────────────┘"
echo ""
echo "  按 Ctrl+C 停止服务"
echo "  ──────────────────────────────────────────"
echo ""

# 延迟打开浏览器
(sleep 2 && open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null) &

$PYTHON app.py

echo ""
echo "  服务已停止"
