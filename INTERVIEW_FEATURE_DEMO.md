# 读后感访谈智能体功能演示

## 🎯 功能概述

读后感访谈智能体是一个完整的AI驱动的读后感播客生成系统，能够：

1. **智能对话引导** - 基于用户画像进行个性化访谈
2. **内容结构化整理** - 使用LLM提取关键洞察和观点
3. **播客自动生成** - 生成完整的播客脚本和音频
4. **多阶段访谈流程** - 破冰→深挖→碰撞→创作四个阶段

## 🚀 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
# 使用启动脚本（推荐）
python start_fogsight.py

# 或者手动启动
uvicorn appbook:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问应用
打开浏览器访问：http://127.0.0.1:8000

## 📝 使用流程

### 第一步：输入书籍信息
1. 在首页输入框中输入：`书名 作者`（例如：`三体 刘慈欣`）
2. 点击"读后感访谈"按钮

### 第二步：进行访谈对话
1. 系统会自动初始化访谈会话
2. 根据AI引导进行对话交流
3. 对话会经历四个阶段：
   - **破冰阶段**：建立信任，了解初步感受
   - **深挖阶段**：深入探讨书籍内容
   - **碰撞阶段**：引入不同视角，激发思考
   - **创作阶段**：引导创造性表达

### 第三步：生成播客
1. 对话6轮后会出现"生成播客"按钮
2. 点击按钮生成完整的播客内容
3. 系统会生成：
   - 播客脚本
   - 音频文件（使用Fish Audio或系统TTS）
   - 播客元数据

## 🛠️ 技术架构

### 核心模块

1. **interview_user_model.py** - 用户状态识别与建模
   - 用户画像分析
   - 访谈会话管理
   - 阶段状态跟踪

2. **interview_dialogue.py** - 智能对话引导系统
   - 基于LLM的对话生成
   - 个性化回复策略
   - 多阶段对话管理

3. **interview_content_processor.py** - 内容结构化整理
   - 智能洞察提取
   - 播客结构生成
   - 内容组织优化

4. **podcast_audio_generator.py** - 播客音频生成
   - Fish Audio集成
   - 系统TTS降级
   - 音频文件合并

### AI模型集成

- **对话模型**: Qwen 2.5 480B (ModelScope)
- **音频生成**: Fish Audio + macOS系统TTS
- **内容分析**: Qwen 2.5 480B

## 🎨 界面特色

### 访谈页面
- 左右分栏布局
- 左侧：对话区域
- 右侧：书籍信息展示
- 阶段指示器显示当前进度
- 实时加载动画

### 消息类型
- 用户消息（蓝色气泡）
- AI回复（绿色气泡）
- 系统消息（灰色气泡）
- 阶段标签显示

### 播客展示
- 播客脚本完整显示
- 音频播放器集成
- 下载功能支持
- 时长和元数据显示

## 🔧 配置说明

### 环境变量
```bash
# Fish Audio配置（可选）
FISH_API_KEY=your_fish_api_key
FISH_REFERENCE_ID=your_reference_id

# Qwen模型配置
QWEN_BASE_URL=https://api-inference.modelscope.cn/v1/
QWEN_API_KEY=your_modelscope_token
```

### 依赖项
- FastAPI - Web框架
- Uvicorn - ASGI服务器
- OpenAI - AI客户端
 Jinja2 - 模板引擎
- Pydantic - 数据验证
- Fish Audio SDK - 音频生成（可选）

## 📊 测试验证

运行测试脚本验证功能：
```bash
python test_interview_modules.py
```

预期输出：
```
正在测试访谈模块...
✅ interview_user_model 模块导入成功
✅ interview_dialogue 模块导入成功
✅ interview_content_processor 模块导入成功
✅ podcast_audio_generator 模块导入成功
✅ 创建测试会话成功: interview_xxx
   用户画像: teenager, student
   当前阶段: ice_break
✅ 对话引擎初始化成功

🎉 所有访谈功能模块测试通过！
```

## 🎯 核心特色

### 1. 个性化定制
- 根据用户年龄、职业、表达风格调整对话策略
- 智能识别用户认知模式和情感倾向
- 生成符合个人特点的播客内容

### 2. 智能化对话
- 真正的LLM对话，而非模板回复
- 基于对话历史的上下文理解
- 多阶段深度引导

### 3. 完整性流程
- 从对话到播客的完整内容创作流程
- 支持音频播放、脚本下载等多种输出形式
- 自动化的内容结构化整理

### 4. 可用性设计
- 优雅的用户界面
- 实时的加载反馈
- 降级的音频生成方案

## 🚀 部署说明

### 本地部署
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 启动应用：`python start_fogsight.py`
4. 访问：http://127.0.0.1:8000

### Docker部署
```bash
docker build -t fogsight .
docker run -p 8000:8000 fogsight
```

## 📈 未来扩展

1. **多语言支持** - 增加英语、日语等语言
2. **更多音频模型** - 集成更多TTS服务
3. **用户系统** - 添加用户登录和历史记录
4. **分享功能** - 支持播客分享到社交媒体
5. **模板系统** - 提供更多播客模板选择

## 🎉 总结

读后感访谈智能体功能已经完全实现，包含：

- ✅ 智能对话引导系统
- ✅ 内容结构化整理
- ✅ 播客生成功能
- ✅ 用户界面优化
- ✅ 完整的用户流程

用户现在可以完整体验从输入书名到生成个性化播客的全流程了！