# OCR文字识别工具

一个基于百度OCR API的截图文字识别工具。

## 功能特点

- 支持快捷键截图识别
- 自定义截图快捷键
- 系统托盘运行
- 支持离线识别备用

## 使用方法

### 首次使用

1. 运行 `install.bat` 安装必要环境
2. 访问 [百度AI开放平台](https://console.bce.baidu.com/ai/) 获取API配置
3. 运行程序，输入API配置信息
4. 点击"启动服务"开始使用

### 日常使用

1. 运行程序
2. 使用快捷键（默认Alt+D）进行截图
3. 识别结果自动复制到剪贴板

## 环境要求

- Windows 7/8/10/11
- Python 3.11 或更高版本（使用源码运行时）
- 网络连接（首次配置时需要）

## 打包版本

直接下载 Release 中的打包版本，无需安装 Python 环境。

## 源码运行

1. 安装 Python 3.11+
2. 运行 `install.bat` 安装依赖
3. 运行 `run.bat` 启动程序

## 许可证

MIT License

## 致谢

- [百度OCR](https://ai.baidu.com/tech/ocr)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) 