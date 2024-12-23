@echo off
title 打包OCR文字识别工具
echo 正在安装打包工具...
pip install pyinstaller

echo 正在打包程序...
pyinstaller --noconfirm --onefile --windowed ^
    --add-data "README.md;." ^
    --icon "icon.ico" ^
    --name "OCR文字识别工具" ^
    --hidden-import "PIL._tkinter_finder" ^
    ocr_app.py

echo 正在复制必要文件...
copy README.md "dist\"
copy install.bat "dist\"
copy run.bat "dist\"

echo 打包完成！程序位于dist文件夹中
pause 