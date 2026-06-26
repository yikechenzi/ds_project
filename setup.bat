@echo off
chcp 65001 >nul
echo ========================================
echo    淘宝自动上架助手 - 环境安装
echo ========================================
echo.
echo 正在安装依赖包...
pip install -r requirements.txt
echo.
echo 正在安装 Chromium 浏览器...
python -m playwright install chromium
echo.
echo ========================================
echo    安装完成！运行 python main.py 启动
echo ========================================
pause
