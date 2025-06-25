@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ##########run_watermark_remover.bat: Windows启动脚本 ##################
REM # 变更记录: [2025-06-25] @李祥光 [创建Windows启动脚本]########
REM # 输入: [用户选择] | 输出: [启动对应的Python程序]###############

title 视频去水印工具 - 启动菜单

echo.
echo ========================================
echo           视频去水印工具 v1.0
echo ========================================
echo.
echo 请选择要使用的版本:
echo.
echo 1. 基础版 (video_watermark_remover.py)
echo 2. 增强版 (enhanced_watermark_remover.py) [推荐]
echo 3. 运行测试
echo 4. 安装项目依赖
echo 5. 退出
echo.

:menu
set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 启动基础版视频去水印工具...
    python video_watermark_remover.py
    goto end
) else if "%choice%"=="2" (
    echo.
    echo 启动增强版视频去水印工具...
    python enhanced_watermark_remover.py
    goto end
) else if "%choice%"=="3" (
    echo.
    echo 运行基础功能测试...
    python test/test_basic.py
    goto end
) else if "%choice%"=="4" (
    echo.
    echo 安装项目依赖...
    pip install -r requirements.txt
    echo.
    echo 依赖安装完成！
    pause
    goto menu
) else if "%choice%"=="5" (
    echo.
    echo 程序退出
    goto end
) else (
    echo.
    echo 无效选择，请重新输入
    goto menu
)

:end
echo.
echo 按任意键退出...
pause >nul