# 双AI协作访谈系统

## 🤖 系统概述

本系统实现了双AI协作的读后感访谈功能，由两个专门的AI智能体协同工作：

1. **对话AI** - 使用Qwen大语言模型，负责引导用户回答3-5个读后感问题
2. **播客AI** - 使用星火大模型API，负责根据用户回答生成个性化播客

## 🔄 工作流程

### 第一阶段：对话AI引导访谈
- 用户访问 `http://127.0.0.1:8001/interview?book_title=书名&book_author=作者`
- 对话AI自动生成个性化开场白
- 逐步引导用户回答5个核心问题：
  1. **开场问题** - 整体感受和印象
  2. **细节问题** - 具体内容和共鸣点
  3. **情感问题** - 情感体验和联想
  4. **反思问题** - 收获和成长
  5. **创意问题** - 创意想法和建议

### 第二阶段：播客AI生成内容
- 用户完成5个问题后，自动显示"生成播客"按钮
- 播客AI整理用户所有回答
- 调用星火API生成完整的播客音频和脚本
- 提供下载和分享功能

## 📁 核心文件

### 1. 双AI引擎 (`dual_ai_interview_engine.py`)
```python
# 主要类
- DualAIInterviewEngine: 双AI协作引擎
- ChatAI: 对话AI，负责问题生成和引导
- PodcastAI: 播客AI，负责调用API生成播客
- DualAISession: 会话状态管理
```

### 2. API路由更新 (`appbook.py`)
```python
# 更新的API端点
@app.post("/api/interview/start")      # 开始双AI协作访谈
@app.post("/api/interview/message")    # 处理对话AI交互
@app.post("/api/interview/generate-podcast")  # 播客AI生成
@app.get("/api/interview/session/{id}") # 获取会话状态
```

### 3. 前端界面 (`templates/interview.html`)
- 实时进度显示：`💬 对话AI：第X个问题（共5个）`
- 智能响应处理：区分问题、完成、错误类型
- 播客展示：音频播放器 + 脚本内容 + 下载分享

## 🛠️ 技术特点

### 对话AI (Qwen)
- **智能问题生成**：根据书籍和对话历史生成个性化问题
- **上下文理解**：保持对话连贯性和深度
- **进度管理**：精确跟踪访谈进度
- **降级机制**：API失败时使用预定义模板

### 播客AI (星火)
- **内容整理**：智能提取和组织用户回答
- **音频生成**：调用星火API生成高质量语音
- **本地保存**：自动下载并保存音频文件
- **错误处理**：完整的异常处理和用户反馈

## 🚀 使用方法

### 1. 启动系统
```bash
# 确保已安装依赖
pip install openai requests fastapi uvicorn

# 启动服务
uvicorn appbook:app --reload --host 0.0.0.0 --port 8001
```

### 2. 访问访谈页面
```
http://127.0.0.1:8001/interview?book_title=三体&book_author=刘慈欣
```

### 3. 进行访谈
1. 页面自动初始化双AI系统
2. 对话AI提出第一个问题
3. 用户回答，对话AI提出下一个问题
4. 重复至5个问题完成
5. 点击"生成播客"，播客AI开始工作
6. 获得完整的播客音频和脚本

## 🧪 测试

运行测试脚本验证整个流程：
```bash
python test_dual_ai_system.py
```

测试覆盖：
- 访谈初始化
- 对话AI问答循环
- 播客AI生成
- 会话状态管理

## 📊 系统架构

```
用户界面 (interview.html)
    ↓
API路由 (appbook.py)
    ↓
双AI引擎 (dual_ai_interview_engine.py)
    ↓
┌─────────────────┬─────────────────┐
│   对话AI        │    播客AI       │
│   (Qwen)       │   (星火API)     │
│   问题生成      │   音频生成      │
│   对话引导      │   内容整理      │
└─────────────────┴─────────────────┘
```

## 🎯 优势特点

1. **专业分工**：两个AI各司其职，专业化程度高
2. **流程自动化**：全程自动引导，用户体验流畅
3. **内容质量**：Qwen深度对话 + 星火高质量音频
4. **错误处理**：完整的降级机制和异常处理
5. **进度可视**：实时显示访谈进度和AI工作状态

## 🔧 配置说明

### Qwen API配置
```python
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
```

### 星火API配置
```python
api_config = {
    "headers": {
        "Authorization": "Bearer f2d4b9650c13355fc8286ac3fc34bf6e:NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
    },
    "url": "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions",
    "flow_id": "7362488342038495234"
}
```

## 📝 更新记录

- **v1.0**: 实现双AI协作访谈系统
- 对话AI：5问题引导 + 智能生成
- 播客AI：星火API集成 + 音频生成
- 前端：进度显示 + 智能响应处理
- 测试：完整流程验证脚本

## 🤝 协作流程示例

```
用户: 访问 /interview?book_title=三体&book_author=刘慈欣

对话AI: 你好！很高兴你选择分享对《三体》的读后感...
       首先，能简单分享一下你对《三体》的整体感受吗？

用户: 这本书让我对宇宙有了全新的认识...

对话AI: 你觉得《三体》中哪个角色或情节最能引起你的共鸣？

用户: 叶文洁这个角色很复杂...

[继续3个问题...]

对话AI: 太棒了！我们的访谈已经完成了...
       现在点击"生成播客"按钮开始制作吧！

用户: [点击生成播客]

播客AI: 📻 播客AI正在为您制作个人读后感播客...
       🎉 播客生成成功！[音频播放器 + 下载链接]
```

这就是完整的双AI协作访谈系统，实现了您要求的功能！
