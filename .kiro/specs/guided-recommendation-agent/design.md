# 引导式书籍推荐智能体设计文档

## 系统架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   认证中间件    │    │   大语言模型    │
│  (React/HTML)   │◄──►│   (JWT验证)     │◄──►│  (OpenAI/Gemini)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   推荐API       │    │   用户数据      │    │   对话管理      │
│  (FastAPI)      │◄──►│  (SQLite)       │◄──►│  (Session)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 核心组件

#### 1. 认证集成模块 (AuthenticationIntegration)
- **职责**：与现有JWT认证系统集成
- **接口**：
  - `verify_user_token(token: str) -> UserInfo`
  - `get_current_user(request: Request) -> User`
  - `require_authentication(endpoint) -> decorator`

#### 2. 用户画像分析器 (UserProfileAnalyzer)
- **职责**：分析用户阅读历史，生成个性化画像
- **接口**：
  - `analyze_reading_patterns(user_id: int) -> UserProfile`
  - `update_profile_from_conversation(user_id: int, conversation: List[Message])`
  - `get_recommendation_context(user_id: int) -> RecommendationContext`

#### 3. AI对话引擎 (AIConversationEngine)
- **职责**：管理与大语言模型的交互
- **接口**：
  - `generate_response(context: ConversationContext) -> AsyncGenerator[str]`
  - `extract_book_recommendations(response: str) -> List[BookRecommendation]`
  - `build_system_prompt(user_profile: UserProfile) -> str`

#### 4. 对话状态管理器 (ConversationStateManager)
- **职责**：管理对话历史和状态
- **接口**：
  - `save_message(session_id: str, message: Message)`
  - `get_conversation_history(session_id: str) -> List[Message]`
  - `create_new_session(user_id: int) -> str`
  - `compress_history_if_needed(session_id: str)`

#### 5. 推荐生成器 (RecommendationGenerator)
- **职责**：从AI回复中提取和格式化推荐
- **接口**：
  - `parse_recommendations_from_text(text: str) -> List[BookRecommendation]`
  - `enrich_recommendations(recommendations: List[BookRecommendation]) -> List[EnrichedRecommendation]`
  - `validate_recommendations(recommendations: List[BookRecommendation]) -> List[BookRecommendation]`

## 数据模型

### 用户相关
```python
@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: datetime

@dataclass
class UserProfile:
    user_id: int
    reading_frequency: str  # "高频", "中频", "低频"
    preferred_categories: List[str]
    current_life_stage: str  # "职场新人", "中年转型", "退休生活"
    emotional_needs: List[str]  # "成长指导", "心理治愈", "知识拓展"
    cognitive_level: str  # "入门", "进阶", "专家"
    last_updated: datetime
```

### 对话相关
```python
@dataclass
class Message:
    id: str
    session_id: str
    user_id: int
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConversationSession:
    id: str
    user_id: int
    created_at: datetime
    last_activity: datetime
    status: str  # "active" | "completed" | "archived"
    context: Dict[str, Any]
```

### 推荐相关
```python
@dataclass
class BookRecommendation:
    title: str
    author: str
    category: str
    description: str
    reason: str
    confidence_score: float
    difficulty_level: str
    emotional_tone: str
    reading_time: str

@dataclass
class RecommendationContext:
    user_profile: UserProfile
    conversation_history: List[Message]
    current_mood: Optional[str]
    specific_requests: List[str]
```

## API设计

### 认证相关端点
```
GET  /api/user/profile          # 获取当前用户信息
POST /api/user/reading-history  # 添加阅读记录
```

### 推荐对话端点
```
POST /api/recommendation/start           # 开始新的推荐会话
POST /api/recommendation/chat            # 发送消息并获取AI回复
GET  /api/recommendation/session/{id}    # 获取会话信息
POST /api/recommendation/feedback        # 提交推荐反馈
```

### 流式响应格式
```json
{
  "event": "message_chunk",
  "data": {
    "content": "这是AI回复的一部分...",
    "is_complete": false
  }
}

{
  "event": "recommendations",
  "data": {
    "books": [
      {
        "title": "乌合之众",
        "author": "古斯塔夫·勒庞",
        "reason": "基于你的职场阅读背景..."
      }
    ]
  }
}

{
  "event": "complete",
  "data": {
    "session_id": "session_123",
    "message_id": "msg_456"
  }
}
```

## 大语言模型集成

### 系统提示词设计
```python
def build_system_prompt(user_profile: UserProfile) -> str:
    return f"""
你是一位专业的私人阅读顾问，具有丰富的图书推荐经验。你的任务是通过智能对话引导用户发现真正适合的书籍。

用户画像：
- 阅读频率：{user_profile.reading_frequency}
- 偏好类别：{', '.join(user_profile.preferred_categories)}
- 生活阶段：{user_profile.current_life_stage}
- 情感需求：{', '.join(user_profile.emotional_needs)}

对话原则：
1. 采用引导式对话，通过提问了解用户真实需求
2. 不要急于推荐，先理解用户的当前状态和困扰
3. 推荐时要给出具体理由，结合用户的个人情况
4. 保持温暖、专业的语调，像朋友一样关心用户
5. 如果决定推荐书籍，请在回复末尾用以下格式：

**推荐书籍：**
- 《书名》 - 作者名 | 类别 | 推荐理由

请开始与用户的对话。
"""
```

### 模型配置
```python
class AIConfig:
    model_name: str = "gpt-4"  # 或 "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = True
    
    # 针对推荐场景的特殊配置
    recommendation_trigger_keywords = [
        "推荐", "建议", "什么书", "读什么", "书单"
    ]
    
    max_conversation_length = 20  # 最大对话轮数
    context_compression_threshold = 15  # 超过此轮数开始压缩历史
```

## 错误处理策略

### 降级机制
1. **AI服务不可用**：切换到预设的引导式对话模板
2. **网络超时**：显示重试选项，保存用户输入
3. **认证失败**：重定向到登录页面，保存对话状态
4. **数据库错误**：使用内存缓存，异步重试

### 错误类型和处理
```python
class RecommendationError(Exception):
    pass

class AIServiceError(RecommendationError):
    """AI服务相关错误"""
    pass

class AuthenticationError(RecommendationError):
    """认证相关错误"""
    pass

class DataError(RecommendationError):
    """数据访问错误"""
    pass

# 错误处理装饰器
def handle_recommendation_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AIServiceError:
            # 切换到备用推荐逻辑
            return await fallback_recommendation(*args, **kwargs)
        except AuthenticationError:
            # 返回认证错误响应
            raise HTTPException(status_code=401, detail="Authentication required")
        except DataError:
            # 使用缓存数据或默认数据
            return await get_cached_or_default_data(*args, **kwargs)
    return wrapper
```

## 性能优化

### 缓存策略
1. **用户画像缓存**：Redis缓存，TTL 1小时
2. **对话历史缓存**：内存缓存最近10轮对话
3. **推荐结果缓存**：相似用户画像的推荐结果缓存

### 流式响应优化
1. **分块传输**：AI回复按句子分块传输
2. **并行处理**：推荐解析与内容生成并行进行
3. **连接池**：复用HTTP连接减少延迟

## 安全考虑

### 数据安全
1. **敏感信息过滤**：过滤用户输入中的敏感信息
2. **对话内容加密**：存储时加密对话历史
3. **访问控制**：严格的用户权限验证

### API安全
1. **请求限制**：每用户每分钟最多10次对话请求
2. **输入验证**：严格验证所有用户输入
3. **CSRF保护**：使用CSRF token保护状态变更操作

## 监控和日志

### 关键指标
1. **响应时间**：AI回复平均延迟
2. **成功率**：对话完成率和推荐接受率
3. **用户满意度**：基于反馈的满意度评分
4. **系统可用性**：服务可用时间百分比

### 日志记录
```python
import logging

logger = logging.getLogger("recommendation_agent")

# 记录关键事件
logger.info(f"User {user_id} started new recommendation session")
logger.info(f"AI generated {len(recommendations)} recommendations for user {user_id}")
logger.error(f"AI service error for user {user_id}: {error_message}")
```

这个设计确保了系统的可扩展性、可靠性和用户体验，同时与现有系统保持良好的集成。