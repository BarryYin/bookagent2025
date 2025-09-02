# Bookagent - AI 书籍介绍系统

一个基于 AI 的智能书籍介绍和演示生成系统，能够自动生成精美的书籍介绍 PPT、播客和互动访谈。

## 🌟 主要功能

### 📚 智能书籍分析
- **多方法论支持**：董宇辉式文学解读、罗振宇式效率提升等不同风格
- **自动分类**：智能识别书籍类型（文学类、效率提升类、虚构类等）
- **封面搜索**：自动搜索并下载书籍封面图片

### 🎨 PPT 演示生成
- **4步骤流程**：书籍数据提取 → PPT结构设计 → 解说词生成 → HTML输出
- **多种视觉风格**：经典商务、现代演示、故事叙述等
- **交互式播放**：支持自动播放、手动导航、语音解说

### 🎙️ 语音和播客
- **语音合成**：为每页PPT生成专业解说音频
- **播客生成**：基于访谈内容生成完整播客节目
- **多语音风格**：专业风格、亲切风格等

### 🎬 视频导出
- **自动录制**：将PPT演示录制为MP4视频
- **音画同步**：解说词与画面完美同步
- **后台处理**：异步生成，不影响其他功能使用

### 💬 智能访谈
- **双AI协作**：访谈官和总结官协同工作
- **深度对话**：基于书籍内容进行个性化访谈
- **读后感生成**：自动整理访谈内容为播客

### 👤 用户系统
- **个人书架**：保存和管理生成的PPT作品
- **阅读画像**：分析用户阅读偏好和习惯
- **智能推荐**：基于用户历史推荐相关书籍

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js (可选，用于前端开发)

### 安装步骤

1. 正确的文件路径

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置 API 密钥**

创建 `credentials.json` 文件：
```json
{
    "API_KEY": "your-api-key-here",
    "BASE_URL": "https://api-inference.modelscope.cn/v1/"
}
```

支持的 API 提供商：
- **ModelScope**：使用 ModelScope Token
- **OpenAI**：使用 OpenAI API Key
- **OpenRouter**：使用 OpenRouter API Key

4. **创建必要目录**
```bash
mkdir -p outputs covers static templates ppt_audio podcast_audio
```

5. **启动应用**
```bash
python appbook.py
```

应用将在 `http://localhost:8001` 启动

## 📖 使用指南

### 基础使用

1. **访问主页**：打开浏览器访问 `http://localhost:8001`

2. **生成书籍介绍**：
   - 输入书名和作者
   - 选择介绍方法论（董宇辉式、罗振宇式等）
   - 选择语音和视频风格
   - 点击生成，等待AI处理

3. **查看结果**：
   - 在线预览生成的PPT演示
   - 下载HTML文件离线使用
   - 导出为MP4视频文件

### 高级功能

#### 个人书架
- 注册/登录账户
- 访问 `/bookshelf` 查看个人作品
- 管理和分类已生成的PPT

#### 智能推荐
- 访问 `/recommendations` 获取个性化推荐
- 基于阅读历史和偏好推荐新书籍

#### 读后感访谈
- 访问 `/interview` 开始智能访谈
- 与AI进行深度对话
- 生成个人播客节目

## 🛠️ 技术架构

### 后端技术栈
- **FastAPI**：高性能 Web 框架
- **SQLite**：轻量级数据库
- **OpenAI/Qwen**：大语言模型
- **Jinja2**：模板引擎

### 前端技术栈
- **HTML5/CSS3/JavaScript**：现代Web技术
- **响应式设计**：支持多设备访问
- **Server-Sent Events**：实时流式更新

### AI 模型
- **Qwen-Coder-480B**：主要推理模型
- **多方法论引擎**：不同风格的内容生成
- **双AI协作系统**：访谈和总结分工

## 📁 项目结构

```
fogsight/
├── appbook.py              # 主应用文件
├── models.py               # 数据模型
├── processors.py           # 处理器模块
├── requirements.txt        # Python依赖
├── credentials.json        # API配置
├── templates/              # HTML模板
│   ├── index.html         # 主页
│   ├── library.html       # 图书馆
│   ├── bookshelf.html     # 个人书架
│   └── interview.html     # 访谈页面
├── static/                 # 静态资源
│   ├── style.css          # 样式文件
│   └── script.js          # 脚本文件
├── outputs/                # 生成的PPT文件
├── covers/                 # 书籍封面图片
├── ppt_audio/             # PPT语音文件
├── podcast_audio/         # 播客音频文件
└── create/                # 创建工具
    ├── methodology_config.py
    └── ppt_voice_generator.py
```

## 🔧 配置选项

### 方法论配置
- `dongyu_literature`：董宇辉式文学作品解读
- `dongyu_autobiography`：董宇辉式自传体解读
- `luozhenyu_efficiency`：罗振宇式效率提升解读

### 语音风格
- `professional_style`：专业播音风格
- `friendly_style`：亲切对话风格
- `storytelling_style`：故事叙述风格

### 视频风格
- `classic_ppt`：经典商务PPT
- `modern_presentation`：现代演示风格
- `storytelling`：故事化展示

## 🚀 部署指南

### 本地开发
```bash
python appbook.py
```

### 生产部署
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn appbook:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# 使用 Docker
docker build -t fogsight .
docker run -p 8001:8001 fogsight
```

### Nginx 配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/fogsight/static/;
    }
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 🎉 初始版本发布
- ✨ 支持多方法论书籍介绍生成
- 🎨 精美的PPT演示界面
- 🎙️ 语音合成和播客功能
- 👤 用户系统和个人书架

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- OpenAI 提供的强大语言模型
- ModelScope 提供的模型推理服务
- FastAPI 团队提供的优秀框架
- 所有贡献者和用户的支持

## 📞 联系我们


---

**Bookagent** - 让每本书都有自己的故事 📚✨