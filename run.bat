@echo off
title OCR文字识别工具

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo Python未安装，请先运行install.bat进行安装配置！
    pause
    exit
)

:: 检查依赖是否安装
python -c "import keyboard, PIL, cv2, easyocr, pytesseract, aip, win32gui, pyperclip, pystray" > nul 2>&1
if errorlevel 1 (
    echo 缺少必要的依赖，正在安装...
    python -m pip install keyboard pillow opencv-python easyocr pytesseract baidu-aip pywin32 pyperclip pystray
)

:: 运行程序
pythonw "%~dp0ocr_app.py"
if errorlevel 1 (
    echo 程序运行出错！
    echo 请尝试运行install.bat重新安装环境
    pause
) 