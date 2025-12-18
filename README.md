# 📚 BookAgent2025 - 智能书籍推广系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![AI Models](https://img.shields.io/badge/AI-Multi--Model-purple.svg)

*基于多AI模型的智能书籍介绍PPT生成、播客制作和个性化推荐系统*

[🚀 快速开始](#-快速开始) • [📖 功能特性](#-功能特性) • [🛠️ 技术栈](#️-技术栈) • [📋 API文档](#-api文档)

</div>

## 🌟 项目简介

BookAgent2025 是一个创新的AI驱动书籍推广平台，集成了多种先进的AI模型，为用户提供：

- 🎨 **智能PPT生成** - 基于书籍内容自动生成精美的介绍PPT
- 🎙️ **播客音频制作** - 双AI对话式播客内容生成
- 🎯 **个性化推荐** - 基于用户偏好的智能书籍推荐
- 🔍 **OCR书籍识别** - 通过封面图片识别书籍信息
- 🎬 **视频导出** - 将PPT转换为视频格式

## 📖 核心功能

### 🎨 智能PPT生成系统
- 书籍信息智能提取和分析
- 多方法论PPT结构设计（董宇辉式、罗振宇式等）
- 苹果发布会风格演讲稿生成
- 响应式HTML PPT渲染
- 讯飞TTS语音合成
- FFmpeg视频导出

### 🎙️ 播客生成系统
- 双AI角色对话生成
- 自然语音合成
- 播客内容管理

### 🎯 智能推荐引擎
- 基于用户浏览历史
- 分类偏好分析
- 协同过滤算法

## 🛠️ 技术栈

- **后端**: FastAPI + Python 3.8+
- **数据库**: SQLite3
- **AI模型**: 百度文心、通义千问、Google Gemini、OpenAI GPT
- **语音合成**: 讯飞TTS WebSocket API
- **图像处理**: 百度OCR API
- **视频生成**: FFmpeg + Selenium

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置API密钥
创建 `credentials.json` 文件并配置你的API密钥。

### 启动应用
```bash
python app.py
# 或
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 访问应用
```
http://localhost:8000
```

## 📋 文档

- [📖 技术架构说明](ARCHITECTURE.md)
- [📖 播客系统文档](PODCAST_SYSTEM_README.md)
- [📖 分类系统文档](CATEGORY_SYSTEM_README.md)
- [📖 OCR功能文档](OCR_FEATURE_README.md)

## 📞 联系我们

- 🐛 Issues: [GitHub Issues](https://github.com/BarryYin/bookagent2025/issues)

---

Made with ❤️ by BookAgent2025 Team
