#!/bin/bash
# News System 启动脚本 v4.0 (Ubuntu / Debian)

set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║    News System 启动脚本 v4.0 (Ubuntu)    ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# ========== 1. 检查 Python 3 ==========
if command -v python3 &>/dev/null; then
    PYTHON=python3
    PIP=pip3
elif command -v python &>/dev/null; then
    PYTHON=python
    PIP=pip
else
    echo "  [错误] 未检测到 Python"
    echo "  请执行: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
echo "  [检查] $PY_VERSION"

# ========== 2. 检查并创建虚拟环境 ==========
if [ ! -d "venv" ]; then
    echo "  [初始化] 创建 Python 虚拟环境..."
    $PYTHON -m venv venv 2>/dev/null || {
        echo "  [提示] 缺少 python3-venv，正在安装..."
        sudo apt install -y python3-venv
        $PYTHON -m venv venv
    }
    echo "  虚拟环境已创建: ./venv/"
fi

# 激活虚拟环境
source venv/bin/activate
echo "  [检查] 虚拟环境已激活"

# ========== 3. 检查端口占用 ==========
PORT=5000
if ss -tlnp 2>/dev/null | grep -q ":${PORT} "; then
    echo ""
    echo "  [警告] 端口 ${PORT} 已被占用！"
    # 显示占用进程
    ss -tlnp 2>/dev/null | grep ":${PORT} " | head -3
    echo ""
    read -p "  输入 Y 关闭旧进程，N 退出 [Y/N]: " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        fuser -k ${PORT}/tcp 2>/dev/null || {
            # fuser 不可用时用 lsof
            kill $(lsof -ti :${PORT}) 2>/dev/null || true
        }
        echo "  已关闭旧进程"
        sleep 2
    else
        echo "  退出启动"
        exit 1
    fi
fi

# ========== 4. 安装依赖 ==========
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  [安装] 正在安装 Python 依赖..."

    # 检查系统依赖（lxml 编译需要）
    if ! dpkg -s libxml2-dev &>/dev/null || ! dpkg -s libxslt1-dev &>/dev/null; then
        echo "  [系统] 安装编译依赖..."
        sudo apt install -y libxml2-dev libxslt1-dev python3-dev build-essential
    fi

    pip install flask feedparser requests beautifulsoup4 lxml
    echo ""
fi

# ========== 5. 初始化数据库 ==========
mkdir -p data
if [ ! -f "data/news.db" ]; then
    echo "  [初始化] 首次运行，正在创建数据库..."
    python scripts/init_db.py
    echo ""
fi

# ========== 6. 启动服务 ==========
echo ""
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

# 尝试打开浏览器（桌面环境下）
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    (sleep 2 && xdg-open http://localhost:5000 2>/dev/null) &
fi

# 捕获 Ctrl+C 优雅退出
trap 'echo ""; echo "  服务已停止"; deactivate 2>/dev/null; exit 0' INT TERM

python app.py

echo ""
echo "  服务已停止"
deactivate 2>/dev/null
