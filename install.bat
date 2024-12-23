@echo off
title OCR文字识别工具 - 环境配置
echo 正在检查 Python 安装...

:: 检查 Python 是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo Python未安装！
    echo 请访问 https://www.python.org/downloads/ 下载并安装Python 3.11或更高版本
    echo 安装时请勾选"Add Python to PATH"选项
    pause
    exit
)

:: 获取Python安装路径
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i

echo 正在安装/更新必要的依赖...
python -m pip install --upgrade pip
python -m pip install keyboard pillow opencv-python easyocr pytesseract baidu-aip pywin32 pyperclip pystray

echo 正在下载Tesseract-OCR...
:: 下载并安装Tesseract
powershell -Command "& {Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe' -OutFile 'tesseract-installer.exe'}"
if exist tesseract-installer.exe (
    echo 正在安装Tesseract-OCR...
    tesseract-installer.exe /S
    del tesseract-installer.exe
) else (
    echo Tesseract-OCR下载失败，请手动安装：
    echo https://github.com/UB-Mannheim/tesseract/wiki
)

echo 安装完成！
pause 