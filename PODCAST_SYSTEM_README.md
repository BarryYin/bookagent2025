# 播客系统使用指南

## 🎙️ 系统概述

播客系统是Fogsight项目的一个重要功能模块，允许用户通过深度访谈的方式创建个性化的读后感播客。系统采用双AI协作架构，提供智能化的访谈体验和高质量的播客生成。

## 🚀 核心功能

### 1. 播客集合页面
- **访问地址**: `http://127.0.0.1:8001/podcasts`
- **功能**: 展示所有已生成的播客，支持在线播放和下载
- **特色**: 现代化的卡片式布局，响应式设计

### 2. 智能访谈系统
- **访问地址**: `http://127.0.0.1:8001/interview`
- **功能**: 通过5个深度问题引导用户分享读后感
- **特色**: 双AI协作，个性化问题生成

### 3. 播客数据库
- **数据库文件**: `podcasts.db`
- **功能**: 存储播客元数据、音频文件路径、用户回答等
- **特色**: SQLite数据库，轻量级且可靠

## 📋 使用流程

### 创建播客的完整流程：

1. **访问播客集合页面**
   ```
   http://127.0.0.1:8001/podcasts
   ```

2. **点击"制作我的播客"按钮**
   - 输入书名（必填）
   - 输入作者（可选）
   - 点击"开始制作"

3. **进入访谈页面**
   - 系统会自动跳转到访谈页面
   - AI会引导你回答5个深度问题
   - 每个问题都针对你选择的书籍个性化生成

4. **完成访谈**
   - 回答完所有问题后，点击"生成播客"
   - 系统会调用AI生成播客内容和音频
   - 播客会自动保存到数据库

5. **查看和分享**
   - 返回播客集合页面查看你的播客
   - 支持在线播放和下载
   - 可以分享给其他用户

## 🛠️ 技术架构

### 后端组件
- **appbook.py**: 主应用服务器，提供API接口
- **dual_ai_interview_engine.py**: 双AI协作访谈引擎
- **podcast_database.py**: 播客数据库管理
- **podcast_audio/**: 音频文件存储目录

### 前端组件
- **templates/podcast_gallery.html**: 播客集合页面
- **templates/interview.html**: 访谈页面
- **static/**: 静态资源文件

### 数据库结构
```sql
CREATE TABLE podcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE,
    book_title TEXT NOT NULL,
    book_author TEXT,
    description TEXT,
    script_content TEXT,
    audio_url TEXT,
    audio_file_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);
```

## 🔧 开发和测试

### 运行测试
```bash
python test_podcast_system.py
```

### 启动服务器
```bash
python appbook.py
```

### 访问页面
- 播客集合: `http://127.0.0.1:8001/podcasts`
- 访谈页面: `http://127.0.0.1:8001/interview`
- 主页: `http://127.0.0.1:8001/`

## 📁 文件结构

```
fogsight/
├── appbook.py                      # 主应用服务器
├── dual_ai_interview_engine.py     # 双AI访谈引擎
├── podcast_database.py             # 播客数据库管理
├── test_podcast_system.py          # 系统测试脚本
├── podcasts.db                     # 播客数据库文件
├── podcast_audio/                  # 音频文件目录
│   ├── *.mp3                      # 生成的播客音频文件
├── templates/
│   ├── podcast_gallery.html       # 播客集合页面
│   └── interview.html             # 访谈页面
└── static/                        # 静态资源
    └── style.css                  # 样式文件
```

## 🎯 功能特色

### 1. 智能访谈
- **个性化问题**: 根据书籍内容生成针对性问题
- **自然对话**: 模拟真实的读书交流体验
- **深度引导**: 5个维度全面挖掘读后感

### 2. 高质量播客
- **AI生成**: 使用先进的AI技术生成播客内容
- **音频合成**: 自动生成高质量的音频文件
- **内容丰富**: 包含完整的播客脚本和音频

### 3. 用户体验
- **响应式设计**: 支持桌面和移动设备
- **现代化UI**: 美观的毛玻璃效果和渐变设计
- **便捷操作**: 一键播放、下载和分享

## 🔮 未来规划

### 短期目标
- [ ] 添加用户认证和个人播客管理
- [ ] 支持播客分类和标签
- [ ] 优化音频质量和生成速度

### 长期目标
- [ ] 多语言支持
- [ ] 社区功能和播客推荐
- [ ] 高级编辑和后处理功能

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进播客系统！

### 开发环境设置
1. 克隆项目
2. 安装依赖: `pip install -r requirements.txt`
3. 运行测试: `python test_podcast_system.py`
4. 启动服务: `python appbook.py`

---

**享受你的播客创作之旅！** 🎉