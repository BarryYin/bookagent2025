# 技术架构说明文档

## 项目概述

**bookagent2025** 是一个基于AI的智能书籍推广系统，提供书籍介绍PPT生成、播客音频生成、个性化推荐等功能。

## 技术栈

### 后端技术
- **框架**: FastAPI (异步Web框架)
- **Python版本**: 3.8+
- **数据库**: SQLite3
- **异步处理**: asyncio, aiohttp, aiofiles

### AI服务
- **LLM模型**: 
  - 百度文心 (ERNIE)
  - 通义千问 (Qwen)
  - Google Gemini
  - OpenAI GPT (通过OpenRouter)
- **语音合成**: 讯飞TTS (WebSocket)
- **图像处理**: 百度OCR

### 前端技术
- **模板引擎**: Jinja2
- **静态资源**: HTML5, CSS3, JavaScript
- **UI交互**: 原生JavaScript + 动态HTML生成

### 其他工具
- **认证**: JWT (PyJWT)
- **视频生成**: FFmpeg + Selenium/Playwright
- **时区处理**: pytz

## 系统架构

### 1. 核心模块

```
bookagent_baidu/
├── app.py                    # 主应用入口
├── appbook.py               # 书籍处理核心逻辑
├── models.py                # 数据模型定义
├── processors.py            # 处理器组件
├── config.py                # 配置管理
└── auth_middleware.py       # 认证中间件
```

### 2. 功能模块

#### 2.1 书籍介绍生成系统
- **入口**: `appbook.py`
- **流程**: 
  1. Step1: 书籍信息收集 (LLM分析)
  2. Step2: PPT结构生成 (支持多种方法论)
  3. Step3: 演讲稿生成
  4. Step4: HTML渲染
  5. Step5: 音频生成 (讯飞TTS)
  6. Step6: 视频导出 (FFmpeg)

#### 2.2 播客生成系统
- **模块**: `podcost.py`, `podcast_audio_generator.py`
- **数据库**: `podcasts.db`
- **功能**: 双AI对话式播客生成

#### 2.3 推荐系统
- **模块**: 
  - `simple_recommendation_api.py` (需认证)
  - `standalone_recommendation_api.py` (独立版)
  - `enhanced_recommendation_engine.py`
- **算法**: 基于用户浏览历史和分类偏好的协同推荐

#### 2.4 用户认证系统
- **模块**: `models.py` (UserManager)
- **功能**: 注册、登录、Session管理
- **数据库表**: users, sessions, ppts

#### 2.5 图书馆系统
- **模块**: `book_category_manager.py`
- **数据**: `book_categories.json`
- **功能**: 分类管理、搜索、筛选

### 3. 数据模型

#### 核心数据类
```python
@dataclass
class BookInfo:           # 书籍基本信息
@dataclass
class ProcessContext:     # 处理上下文
@dataclass
class Slide:             # PPT幻灯片
@dataclass
class SpeechScript:      # 演讲稿
@dataclass
class StyleConfig:       # 样式配置
```

#### 数据库表结构
- **users**: 用户信息
- **sessions**: 会话管理
- **ppts**: PPT记录 (关联用户、分类、浏览统计)
- **podcasts**: 播客记录

### 4. API路由

#### 主要端点
```
POST /generate                          # 生成动画
POST /generate-book-introduction        # 生成书籍介绍
POST /api/book/generate                 # 生成书籍PPT
GET  /api/book/ppts                     # 获取用户PPT列表
POST /api/export-video                  # 导出视频
GET  /api/latest-podcasts               # 获取最新播客
POST /api/recommendation/start          # 推荐对话
GET  /api/library/books                 # 图书馆书籍列表
```

#### 认证端点
```
POST /api/auth/register                 # 用户注册
POST /api/auth/login                    # 用户登录
POST /api/auth/logout                   # 用户登出
GET  /api/auth/me                       # 获取当前用户
```

### 5. 处理流程

#### 书籍PPT生成流程
```
用户输入 → Step1(信息收集) → Step2(PPT结构) → Step3(演讲稿) 
→ Step4(HTML渲染) → Step5(音频生成) → Step6(视频导出)
```

#### 推荐系统流程
```
用户请求 → 获取浏览历史 → 分析偏好 → 生成推荐列表 
→ 过滤已有书籍 → 返回个性化推荐
```

### 6. 方法论系统

支持多种内容生成方法论:
- **dongyu_literature**: 董宇辉式文学作品介绍
- **dongyu_autobiography**: 董宇辉式自传体介绍
- **luozhenyu_efficiency**: 罗振宇式效率提升类介绍
- **通用方法论**: 标准书籍介绍

### 7. 视频风格

支持三种PPT视觉风格:
- **classic_ppt**: 经典商务风格
- **storytelling**: 故事化温暖风格
- **modern_presentation**: 现代科技风格

## 部署架构

### 开发环境
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 生产环境
- **Web服务器**: Nginx (反向代理)
- **应用服务器**: Uvicorn + Gunicorn
- **进程管理**: systemd
- **容器化**: Docker + docker-compose

### 配置文件
- `credentials.json`: API密钥配置
- `xunfei_config.json`: 讯飞TTS配置
- `nginx.conf`: Nginx配置
- `systemd.service`: 系统服务配置

## 数据流

### 1. 用户请求流
```
浏览器 → Nginx → FastAPI → 业务逻辑 → 数据库/AI服务 → 响应
```

### 2. AI处理流
```
用户输入 → LLM API → 流式响应 → 前端实时渲染
```

### 3. 文件存储
```
outputs/                    # PPT输出目录
  └── {session_id}/
      ├── presentation.html
      ├── data.json
      └── enhanced_config.json
ppt_audio/                  # 音频文件
covers/                     # 书籍封面
podcast_audio/              # 播客音频
```

## 安全机制

1. **认证**: JWT Token + Session管理
2. **密码**: SHA256哈希存储
3. **CORS**: 配置跨域访问控制
4. **输入验证**: Pydantic模型验证
5. **错误处理**: 统一异常处理机制

## 性能优化

1. **异步处理**: 全面使用async/await
2. **流式响应**: SSE (Server-Sent Events)
3. **数据库索引**: session_id, user_id
4. **静态资源**: FastAPI StaticFiles挂载
5. **缓存策略**: 浏览器缓存控制

## 扩展性

### 智能体系统
- **exploration**: 书籍探索智能体
- **recommendation**: 引导推荐智能体
- **interview**: 读后感访谈智能体

### 插件化设计
- 处理器模式 (BaseProcessor)
- 流程编排器 (ProcessOrchestrator)
- 可扩展的方法论配置

## 监控与日志

- **日志系统**: Python logging模块
- **日志级别**: INFO, WARNING, ERROR
- **日志文件**: `appbook.log`, `server.log`

## 依赖管理

核心依赖 (requirements.txt):
```
fastapi
uvicorn
pydantic
openai
jinja2
pytz
google-genai
requests
PyJWT
python-multipart
aiohttp
aiofiles
```

## 开发规范

1. **代码风格**: PEP 8
2. **类型注解**: 使用typing模块
3. **文档字符串**: 函数和类添加docstring
4. **错误处理**: try-except + 日志记录
5. **异步优先**: 优先使用异步函数

## 未来规划

1. 支持更多LLM模型
2. 增强推荐算法
3. 实现实时协作功能
4. 移动端适配
5. 多语言支持
6. 云存储集成

---

**文档版本**: 1.0  
**最后更新**: 2025年  
**维护者**: bookagent2025团队
