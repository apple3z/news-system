@echo off
chcp 65001 >nul 2>&1
title News System v4.0

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║       News System 启动脚本 v4.0          ║
echo   ╚══════════════════════════════════════════╝
echo.

REM ========== 1. 检查 Python ==========
python --version >nul 2>&1
if errorlevel 1 (
    echo   [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM ========== 2. 切换到脚本所在目录 ==========
cd /d "%~dp0"

REM ========== 3. 检查端口占用 ==========
netstat -ano | findstr ":5000 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo   [警告] 端口 5000 已被占用！
    echo.
    echo   可能是上次的服务未关闭，是否强制关闭？
    set /p choice="   输入 Y 关闭旧进程，N 退出 [Y/N]: "
    if /i "%choice%"=="Y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 " ^| findstr "LISTENING"') do (
            taskkill /PID %%a /F >nul 2>&1
        )
        echo   已关闭旧进程
        timeout /t 2 /nobreak >nul
    ) else (
        echo   退出启动
        pause
        exit /b 1
    )
)

REM ========== 4. 检查依赖 ==========
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo   [提示] 正在安装必要依赖...
    pip install flask feedparser requests beautifulsoup4 lxml
    echo.
)

REM ========== 5. 初始化数据库 ==========
if not exist "data" mkdir data
if not exist "data\news.db" (
    echo   [初始化] 首次运行，正在创建数据库...
    python scripts\init_db.py
    echo.
)

REM ========== 6. 启动服务 ==========
echo   ┌──────────────────────────────────────────┐
echo   │  前端首页:  http://localhost:5000         │
echo   │  后台管理:  http://localhost:5000/sys     │
echo   │  API文档:   http://localhost:5000/api/... │
echo   │  默认账号:  admin / admin123              │
echo   └──────────────────────────────────────────┘
echo.
echo   按 Ctrl+C 停止服务
echo   ──────────────────────────────────────────
echo.

REM 延迟2秒后自动打开浏览器
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

python app.py

echo.
echo   服务已停止
pause
