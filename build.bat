@echo off
chcp 65001
title 打包OCR文字识别工具

:: 检查必要文件
if not exist "icon.ico" (
    echo 错误：缺少图标文件 icon.ico
    pause
    exit /b 1
)

:: 安装依赖
echo 正在安装打包工具...
pip install pyinstaller

:: 生成版本文件
echo 正在生成版本信息...
python -c "from version import VERSION; print(VERSION)" > temp_version.txt
set /p VERSION=<temp_version.txt
del temp_version.txt

:: 打包程序
echo 正在打包程序 v%VERSION%...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --icon="icon.ico" ^
    --version-file="version_info.txt" ^
    --name="OCR-Tool" ^
    --add-data="README.md;." ^
    --add-data="icon.ico;." ^
    --hidden-import="PIL._tkinter_finder" ^
    ocr_app.py

:: 复制必要文件
echo 正在复制相关文件...
copy README.md "dist\"
copy install.bat "dist\"
copy run.bat "dist\"
copy icon.ico "dist\"

:: 重命名可执行文件
ren "dist\OCR-Tool.exe" "OCR文字识别工具.exe"

echo 打包完成！v%VERSION%
echo 程序位于 dist 文件夹中
pause 