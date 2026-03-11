@echo off
REM News System 快速启动脚本 (Windows)
REM 前后端分离架构 v4.0

echo ==================================================
echo   News System 启动脚本 (v4.0)
echo ==================================================
echo.

REM 检查数据库
if not exist "data\news.db" (
    echo 检测到数据库不存在，正在初始化...
    python scripts\init_db.py
    echo.
)

REM 启动应用
echo 正在启动 News System 服务...
echo 前端 SPA：http://localhost:5000
echo 系统管理：http://localhost:5000/sys
echo API：http://localhost:5000/api/...
echo.
echo 按 Ctrl+C 停止服务
echo ==================================================
echo.

python app.py
