# 📚 BookAgent2025 - 智能书籍推广系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![AI Models](https://img.shields.io/badge/AI-Multi--Model-purple.svg)

*基于多AI模型的智能书籍介绍PPT生成、播客制作和个性化推荐系统*

[🚀 快速开始](#-快速开始) • [📖 功能特性](#-功能特性) • [🛠️ 技术栈](#️-技术栈) • [📋 API文档](#-api文档) • [🤝 贡献指南](#-贡献指南)

</div>

## 🌟 项目简介

BookAgent2025 是一个创新的AI驱动书籍推广平台，集成了多种先进的AI模型，为用户提供：

- 🎨 **智能PPT生成** - 基于书籍内容自动生成精美的介绍PPT
- 🎙️ **播客音频制作** - 双AI对话式播客内容生成
- 🎯 **个性化推荐** - 基于用户偏好的智能书籍推荐
- 🔍 **OCR书籍识别** - 通过封面图片识别书籍信息
- 🎬 **视频导出** - 将PPT转换为视频格式

## 🎯 核心亮点

### 🤖 多AI模型支持
- **百度文心 (ERNIE)** - 中文内容生成优势
- **阿里通义千问 (Qwen)** - 代码理解和逻辑推理
- **Google Gemini** - 多模态内容处理
- **OpenAI GPT** - 通用语言理解

### 🎨 多种内容风格
- **董宇辉式文学介绍** - 温暖人文的表达方式
- **罗振宇式效率提升** - 实用主义的内容结构
- **经典商务风格** - 专业正式的展示方式
- **现代科技风格** - 简约时尚的视觉设计

### 🔄 完整工作流程
```
书籍输入 → AI分析 → PPT生成 → 音频合成 → 视频导出 → 个性化推荐
```

## 📖 功能特性

### 🎨 智能PPT生成系统
- **Step1**: 书籍信息智能提取和分析
- **Step2**: 多方法论PPT结构设计
- **Step3**: 苹果发布会风格演讲稿生成
- **Step4**: 响应式HTML PPT渲染
- **Step5**: 讯飞TTS语音合成
- **Step6**: FFmpeg视频导出

### 🎙️ 播客生成系统
- 双AI角色对话生成
- 自然语音合成
- 播客内容管理
- 音频质量优化

### 🎯 智能推荐引擎
- 基于用户浏览历史
- 分类偏好分析
- 协同过滤算法
- 实时推荐更新

### 👤 用户管理系统
- JWT认证机制
- 用户偏好记录
- 浏览历史追踪
- 个人作品管理

### 📚 图书馆系统
- 分类管理
- 搜索筛选
- 封面OCR识别
- 书籍信息维护

## 🛠️ 技术栈

### 后端技术
- **框架**: FastAPI (异步Web框架)
- **Python**: 3.8+
- **数据库**: SQLite3
- **异步处理**: asyncio, aiohttp, aiofiles

### AI服务集成
- **LLM模型**: 百度文心、通义千问、Google Gemini、OpenAI GPT
- **语音合成**: 讯飞TTS WebSocket API
- **图像处理**: 百度OCR API
- **视频生成**: FFmpeg + Selenium

### 前端技术
- **模板引擎**: Jinja2
- **UI框架**: HTML5 + CSS3 + 原生JavaScript
- **实时通信**: Server-Sent Events (SSE)

## 🚀 快速开始

### 📋 环境要求
- Python 3.8+
- Node.js (可选，用于前端开发)
- FFmpeg (用于视频导出)

### 🔧 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/bookagent2025.git
cd bookagent2025
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置你的API密钥
```

4. **配置示例**
```bash
# 至少配置一个AI模型服务
GEMINI_API_KEY=your_gemini_api_key_here
# 或
OPENAI_API_KEY=sk-your_openai_api_key_here
# 或
BAIDU_API_KEY=your_baidu_api_key_here
# 或
QWEN_API_KEY=your_qwen_api_key_here

# 可选：语音服务
XUNFEI_APP_ID=your_xunfei_app_id
XUNFEI_API_SECRET=your_xunfei_api_secret
XUNFEI_API_KEY=your_xunfei_api_key

# 可选：OCR服务
BAIDU_OCR_API_KEY=your_baidu_ocr_api_key
BAIDU_OCR_SECRET_KEY=your_baidu_ocr_secret_key
```

5. **启动应用**
```bash
# 开发模式
python app.py

# 或使用uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

6. **访问应用**
```
http://localhost:8000
```

### 🐳 Docker部署

```bash
# 使用docker-compose
docker-compose up -d
```

## 📋 API文档

### 🔑 认证接口
```http
POST /api/auth/register    # 用户注册
POST /api/auth/login       # 用户登录
POST /api/auth/logout      # 用户登出
GET  /api/auth/me          # 获取当前用户信息
```

### 📚 书籍处理接口
```http
POST /api/book/generate              # 生成书籍PPT
GET  /api/book/ppts                  # 获取用户PPT列表
POST /api/export-video               # 导出视频
POST /generate-book-introduction     # 生成书籍介绍
```

### 🎙️ 播客接口
```http
GET  /api/latest-podcasts           # 获取最新播客
POST /api/podcast/generate          # 生成播客内容
```

### 🎯 推荐接口
```http
POST /api/recommendation/start      # 开始推荐对话
GET  /api/recommendation/books      # 获取推荐书籍
```

### 📖 图书馆接口
```http
GET  /api/library/books             # 获取书籍列表
GET  /api/library/categories        # 获取分类列表
POST /api/library/search            # 搜索书籍
```

## 🎨 使用示例

### 生成书籍PPT
```python
import requests

# 生成PPT
response = requests.post('http://localhost:8000/api/book/generate', 
    json={
        "book_title": "人类简史",
        "methodology": "dongyu_literature",
        "style": "modern_presentation"
    },
    headers={"Authorization": "Bearer your_jwt_token"}
)

ppt_data = response.json()
```

### 获取个性化推荐
```python
# 获取推荐
response = requests.post('http://localhost:8000/api/recommendation/start',
    json={"user_message": "我喜欢科幻小说"},
    headers={"Authorization": "Bearer your_jwt_token"}
)
```

## 🏗️ 项目结构

```
bookagent2025/
├── 📁 static/                    # 静态资源
├── 📁 templates/                 # HTML模板
├── 📁 outputs/                   # PPT输出目录
├── 📁 covers/                    # 书籍封面
├── 📁 podcast_audio/             # 播客音频
├── 📁 ppt_audio/                # PPT音频
├── 📄 app.py                    # 主应用入口
├── 📄 appbook.py               # 书籍处理核心
├── 📄 models.py                # 数据模型
├── 📄 config.py                # 配置管理
├── 📄 auth_middleware.py       # 认证中间件
├── 📄 podcast_audio_generator.py # 播客生成
├── 📄 enhanced_recommendation_engine.py # 推荐引擎
├── 📄 book_category_manager.py # 分类管理
├── 📄 dual_ai_interview_engine.py # 双AI面试
└── 📄 requirements.txt         # 依赖列表
```

## 🔧 配置说明

### 环境变量配置
详细配置说明请参考：
- [📖 SETUP_GUIDE.md](SETUP_GUIDE.md) - 快速配置指南
- [🔄 CONFIG_MIGRATION_GUIDE.md](CONFIG_MIGRATION_GUIDE.md) - 配置迁移指南

### 支持的AI模型
| 服务商 | 模型 | 用途 | 配置变量 |
|--------|------|------|----------|
| 百度 | ERNIE-4.5-Turbo | 中文内容生成 | `BAIDU_API_KEY` |
| 阿里 | Qwen3-Coder | 代码和逻辑 | `QWEN_API_KEY` |
| Google | Gemini-2.0 | 多模态处理 | `GEMINI_API_KEY` |
| OpenAI | GPT-4 | 通用语言 | `OPENAI_API_KEY` |

## 🎯 使用场景

### 📚 教育培训
- 课程内容PPT制作
- 教学音频生成
- 学习资料推荐

### 📖 出版营销
- 新书推广PPT
- 书籍介绍视频
- 读者画像分析

### 🎙️ 内容创作
- 读书播客制作
- 书评视频生成
- 个性化推荐

### 📱 个人使用
- 读书笔记整理
- 分享内容制作
- 阅读计划推荐

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题
- 使用 [GitHub Issues](https://github.com/your-username/bookagent2025/issues)
- 提供详细的错误信息和复现步骤

### 💡 功能建议
- 在 Issues 中标记为 `enhancement`
- 详细描述功能需求和使用场景

### 🔧 代码贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 📝 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的类型注解
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢以下开源项目和服务：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [OpenAI](https://openai.com/) - GPT模型API
- [百度智能云](https://cloud.baidu.com/) - 文心大模型和OCR服务
- [阿里云](https://www.aliyun.com/) - 通义千问模型
- [Google AI](https://ai.google/) - Gemini模型
- [讯飞开放平台](https://www.xfyun.cn/) - 语音合成服务

## 📞 联系我们

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/bookagent2025/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/bookagent2025/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个星标！**

Made with ❤️ by BookAgent2025 Team

</div>