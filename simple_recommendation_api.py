"""
引导式书籍推荐API - 集成身份验证和大语言模型
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import json
from datetime import datetime
import asyncio

# 导入认证相关模块
from auth_middleware import get_current_user, get_current_user_optional, AuthContext, create_auth_context
from models import User

# 临时使用简化版本的推荐逻辑
router = APIRouter(prefix="/api/recommendation", tags=["recommendation"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class ReadingHistoryRequest(BaseModel):
    book_title: str
    author: str
    completion_date: str
    rating: Optional[int] = None
    notes: Optional[str] = None

MOCK_USER_ID = 1

# 模拟推荐数据
MOCK_BOOKS = [
    {
        "title": "乌合之众",
        "author": "古斯塔夫·勒庞",
        "category": "心理学",
        "description": "群体心理学的经典之作",
        "difficulty": "入门",
        "emotional_tone": "思考",
        "reading_time": "中篇",
        "reason": "基于你的职场阅读背景，这本书能让你在紧张的学习中找到平衡，同时加深对人性的理解"
    },
    {
        "title": "被讨厌的勇气",
        "author": "岸见一郎",
        "category": "心理学",
        "description": "阿德勒心理学入门",
        "difficulty": "入门",
        "emotional_tone": "治愈",
        "reading_time": "中篇",
        "reason": "适合你当前的阅读节奏，能帮助建立健康的自我认知"
    },
    {
        "title": "小王子",
        "author": "安托万·德·圣埃克苏佩里",
        "category": "文学",
        "description": "童心未泯的哲学寓言",
        "difficulty": "入门",
        "emotional_tone": "治愈",
        "reading_time": "短篇",
        "reason": "简短但深刻的阅读体验，适合作为放松阅读"
    }
]

# 模拟对话模板
DIALOGUE_TEMPLATES = {
    "start": "你好！我是你的私人阅读顾问。我注意到你最近读了很多职场技能类的书，是刚开始工作吗？",
    "follow_up": "我理解这种焦虑。不过我注意到你读的这些书都很'硬核'，全是方法论。你有多久没读过让自己放松的书了？",
    "recommendation": "基于我们的对话，我特别推荐《{book}》。这本书{reason}"
}

@router.post("/start")
async def start_recommendation_session(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """开始引导推荐会话（需要认证）"""
    try:
        setup_database()
        
        # 分析用户阅读历史
        user_profile = analyze_user_reading_patterns(current_user.id)
        
        # 生成个性化开场白
        greeting_message = generate_personalized_greeting(user_profile)
        
        return {
            "message": greeting_message,
            "user_profile": user_profile,
            "session_id": f"session_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_info": {
                "id": current_user.id,
                "username": current_user.username
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_agent(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """与推荐智能体对话（需要认证）"""
    try:
        # 获取用户画像
        user_profile = analyze_user_reading_patterns(current_user.id)
        
        # 构建对话上下文
        conversation_context = {
            "user_id": current_user.id,
            "user_profile": user_profile,
            "message": chat_request.message,
            "timestamp": datetime.now().isoformat()
        }
        
        # 调用AI生成回复
        response_data = await generate_ai_response(conversation_context)
        
        # 保存对话记录
        save_conversation_message(current_user.id, "user", chat_request.message)
        save_conversation_message(current_user.id, "agent", response_data.get("message", ""))
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_with_agent_stream(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """与推荐智能体对话（流式响应）"""
    from fastapi.responses import StreamingResponse
    from ai_conversation_engine import ai_engine
    
    async def generate_stream():
        try:
            # 获取用户画像
            user_profile = analyze_user_reading_patterns(current_user.id)
            
            # 发送开始事件
            yield f"data: {json.dumps({'event': 'start', 'data': {}})}\n\n"
            
            # 生成AI回复
            full_response = ""
            async for chunk in ai_engine.generate_response(chat_request.message, current_user.id, user_profile):
                full_response += chunk
                yield f"data: {json.dumps({'event': 'message_chunk', 'data': {'content': chunk, 'is_complete': False}})}\n\n"
            
            # 提取推荐书籍
            recommendations = ai_engine.extract_book_recommendations(full_response)
            if not recommendations and any(word in full_response.lower() for word in ["推荐", "建议", "《"]):
                recommendations = generate_personalized_recommendations(user_profile)
            
            # 发送推荐事件
            if recommendations:
                yield f"data: {json.dumps({'event': 'recommendations', 'data': {'books': recommendations}})}\n\n"
            
            # 发送完成事件
            yield f"data: {json.dumps({'event': 'complete', 'data': {'message_complete': True}})}\n\n"
            
        except Exception as e:
            print(f"流式对话失败: {e}")
            yield f"data: {json.dumps({'event': 'error', 'data': {'message': '抱歉，对话出现问题，请稍后重试。'}})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/recommendations")
async def get_recommendations():
    """获取个性化推荐"""
    setup_database()
    return {
        "recommendations": MOCK_BOOKS,
        "user_profile": {
            "reading_frequency": "高频",
            "preferred_categories": ["职场技能"],
            "current_life_stage": "职场新人",
            "emotional_needs": ["成长指导"]
        }
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": str(datetime.now())}

@router.get("/auth/status")
async def check_auth_status(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """检查用户认证状态"""
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            }
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }

def setup_database():
    """设置数据库"""
    try:
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 创建阅读历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reading_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_title TEXT,
                author TEXT,
                completion_date TEXT,
                rating INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建对话会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # 创建对话消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"数据库设置失败: {e}")

def analyze_user_reading_patterns(user_id: int) -> Dict[str, Any]:
    """分析用户阅读模式"""
    try:
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 检查ppts表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ppts'")
        if not cursor.fetchone():
            # 如果表不存在，使用默认数据
            print("警告: ppts表不存在，使用默认推荐数据")
            conn.close()
            return get_default_user_profile()
        
        # 从用户的PPT记录中获取阅读历史
        cursor.execute("""
            SELECT title, author, category_name, created_at 
            FROM ppts 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 20
        """, (user_id,))
        
        books = cursor.fetchall()
        conn.close()
        
        if not books:
            return get_default_user_profile()
        
        # 分析类别偏好
        categories = {}
        recent_books = []
        
        for book in books:
            title, author, category, created_at = book
            recent_books.append(f"《{title}》")
            
            if category:
                categories[category] = categories.get(category, 0) + 1
        
        # 排序类别
        preferred_categories = sorted(categories.keys(), key=lambda x: categories[x], reverse=True)[:3]
        
        # 推断阅读频率
        total_books = len(books)
        if total_books >= 10:
            reading_frequency = "高频"
        elif total_books >= 5:
            reading_frequency = "中频"
        else:
            reading_frequency = "低频"
        
        # 推断生活阶段（基于类别）
        life_stage = "多元探索者"
        if "职场技能" in preferred_categories or "商业管理" in preferred_categories:
            life_stage = "职场新人"
        elif "文学" in preferred_categories and "历史" in preferred_categories:
            life_stage = "文化学者"
        elif "心理学" in preferred_categories or "自我成长" in preferred_categories:
            life_stage = "自我提升者"
        
        # 推断情感需求
        emotional_needs = ["知识拓展"]
        if "心理学" in preferred_categories:
            emotional_needs.append("心理治愈")
        if "职场技能" in preferred_categories:
            emotional_needs.append("成长指导")
        if "文学" in preferred_categories:
            emotional_needs.append("情感共鸣")
        
        return {
            "reading_frequency": reading_frequency,
            "preferred_categories": preferred_categories,
            "current_life_stage": life_stage,
            "emotional_needs": emotional_needs,
            "recent_books": recent_books[:5],
            "total_books": total_books
        }
        
    except Exception as e:
        print(f"分析用户阅读模式失败: {e}")
        return get_default_user_profile()

def get_default_user_profile() -> Dict[str, Any]:
    """获取默认用户画像"""
    return {
        "reading_frequency": "新用户",
        "preferred_categories": ["文学", "心理学", "历史"],
        "current_life_stage": "探索阶段",
        "emotional_needs": ["兴趣发现", "知识拓展"],
        "recent_books": ["《活着》", "《解忧杂货店》", "《人类简史》"],
        "total_books": 3
    }

def generate_personalized_greeting(user_profile: Dict[str, Any]) -> str:
    """生成个性化开场白"""
    recent_books = user_profile.get("recent_books", [])
    life_stage = user_profile.get("current_life_stage", "探索阶段")
    preferred_categories = user_profile.get("preferred_categories", [])
    
    if not recent_books:
        return "你好！我是你的私人阅读顾问。我注意到你刚开始使用我们的系统，让我们聊聊你的阅读兴趣吧！你平时喜欢读什么类型的书？"
    
    books_text = "、".join(recent_books[:3])
    categories_text = "、".join(preferred_categories[:2]) if preferred_categories else "多种类型"
    
    greetings = {
        "职场新人": f"你好！我是你的私人阅读顾问。我看到你最近读了{books_text}等书，都是很实用的{categories_text}书籍。是刚开始工作，想快速提升自己吗？",
        "文化学者": f"你好！我是你的私人阅读顾问。从你的阅读记录看，你对{categories_text}很有研究，最近读了{books_text}。你是在做学术研究，还是纯粹出于兴趣？",
        "自我提升者": f"你好！我是你的私人阅读顾问。我注意到你很关注{categories_text}，最近读了{books_text}。看得出你很注重内在成长，最近有什么特别想改善的方面吗？",
        "多元探索者": f"你好！我是你的私人阅读顾问。你的阅读兴趣很广泛，从{books_text}可以看出你对{categories_text}都有涉猎。这种多元化的阅读很棒！最近有什么特别想深入了解的领域吗？"
    }
    
    return greetings.get(life_stage, f"你好！我是你的私人阅读顾问。我看到你最近读了{books_text}，让我们聊聊你的阅读需求吧！")

async def generate_ai_response(conversation_context: Dict[str, Any]) -> Dict[str, Any]:
    """使用AI引擎生成回复"""
    from ai_conversation_engine import ai_engine
    
    user_id = conversation_context["user_id"]
    message = conversation_context["message"]
    user_profile = conversation_context["user_profile"]
    
    try:
        # 生成AI回复
        response_text = ""
        async for chunk in ai_engine.generate_response(message, user_id, user_profile):
            response_text += chunk
        
        # 提取推荐书籍
        recommendations = ai_engine.extract_book_recommendations(response_text)
        
        # 如果没有从AI回复中提取到推荐，但回复中提到了推荐，使用备用推荐
        if not recommendations and any(word in response_text.lower() for word in ["推荐", "建议", "《"]):
            recommendations = generate_personalized_recommendations(user_profile)
        
        return {
            "message": response_text,
            "recommendations": recommendations,
            "turn": len(ai_engine.get_conversation_history(user_id)),
            "should_recommend": len(recommendations) > 0
        }
        
    except Exception as e:
        print(f"AI回复生成失败: {e}")
        # 降级到规则引擎
        return await generate_fallback_response(message, user_profile)

async def generate_fallback_response(message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """降级回复生成"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["你好", "hi", "hello", "开始"]):
        response = "很高兴和你聊天！基于你的阅读历史，我能看出你是一个很有追求的读者。让我们深入聊聊，你现在最想通过阅读解决什么问题，或者达到什么目标？"
        return {
            "message": response,
            "recommendations": [],
            "turn": 1,
            "should_recommend": False
        }
    
    elif any(word in message_lower for word in ["推荐", "建议", "什么书", "书单"]):
        recommendations = generate_personalized_recommendations(user_profile)
        response = f"基于你的阅读偏好，我为你精心挑选了几本书。这些书既能满足你的成长需求，又能带来不同的阅读体验。"
        return {
            "message": response,
            "recommendations": recommendations,
            "turn": 2,
            "should_recommend": True
        }
    
    else:
        response = "我很理解你的想法。每个人的阅读需求都不同，这正是个性化推荐的价值所在。能告诉我更多关于你当前的生活状态或者遇到的挑战吗？这样我能为你推荐更合适的书籍。"
        return {
            "message": response,
            "recommendations": [],
            "turn": 1,
            "should_recommend": False
        }
    life_stage = user_profile.get("current_life_stage", "探索阶段")
    
    if any(word in message_lower for word in ["你好", "hi", "hello", "开始"]):
        if life_stage == "职场新人":
            response = "你好！我看到你最近在关注职场成长类的书籍，这很棒！作为职场新人，在快速学习的同时，也要注意保持内心的平衡。你现在工作中遇到的最大挑战是什么？"
        else:
            response = "你好！很高兴和你聊天。从你的阅读记录可以看出你是一个很有追求的读者。最近有什么特别想通过阅读解决的问题吗？"
        
        return {
            "message": response,
            "recommendations": [],
            "turn": 1,
            "should_recommend": False
        }
    
    elif any(word in message_lower for word in ["推荐", "建议", "什么书", "书单"]):
        recommendations = generate_personalized_recommendations(user_profile)
        response = "基于你的阅读偏好，我为你推荐以下几本书："
        
        return {
            "message": response,
            "recommendations": recommendations,
            "turn": 2,
            "should_recommend": True
        }
    
    else:
        response = "我理解你的想法。每个人的阅读需求都不同，这正是个性化推荐的价值所在。能告诉我更多关于你当前的状态或想法吗？"
        
        return {
            "message": response,
            "recommendations": [],
            "turn": 1,
            "should_recommend": False
        }

def get_conversation_history(user_id: int, limit: int = 10) -> List[Dict[str, str]]:
    """获取对话历史"""
    try:
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content FROM conversation_messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit * 2))  # 获取更多记录以确保有足够的对话轮次
        
        messages = cursor.fetchall()
        conn.close()
        
        # 转换为所需格式并反转顺序（最新的在后面）
        history = []
        for role, content in reversed(messages):
            history.append({"role": role, "content": content})
        
        return history
        
    except Exception as e:
        print(f"获取对话历史失败: {e}")
        return []

def save_conversation_message(user_id: int, role: str, content: str):
    """保存对话消息"""
    try:
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 确保表存在
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
            )
        ''')
        
        message_id = f"msg_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        # 确保会话存在
        cursor.execute("""
            INSERT OR IGNORE INTO conversation_sessions (id, user_id)
            VALUES (?, ?)
        """, (session_id, user_id))
        
        # 保存消息
        cursor.execute("""
            INSERT INTO conversation_messages (id, session_id, user_id, role, content)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, session_id, user_id, role, content))
        
        conn.commit()
        conn.close()
        
        print(f"成功保存对话消息: {role} - {content[:20]}...")
        
    except Exception as e:
        print(f"保存对话消息失败: {e}")

def generate_personalized_recommendations(user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """基于用户画像生成个性化推荐"""
    preferred_categories = user_profile.get("preferred_categories", [])
    life_stage = user_profile.get("current_life_stage", "多元探索者")
    emotional_needs = user_profile.get("emotional_needs", [])
    
    # 基础推荐池
    all_books = MOCK_BOOKS.copy()
    
    # 检查数据库中是否有这些书的生成内容
    conn = sqlite3.connect("fogsight.db")
    cursor = conn.cursor()
    
    for book in all_books:
        # 查找是否有对应的生成内容
        try:
            cursor.execute("""
                SELECT id FROM ppts 
                WHERE title LIKE ? OR title LIKE ?
                LIMIT 1
            """, (f"%{book['title']}%", f"%{book['title'].replace(' ', '')}%"))
            
            result = cursor.fetchone()
            if result:
                book["has_content"] = True
                book["content_id"] = result[0]
            else:
                book["has_content"] = False
                book["content_id"] = None
        except Exception as e:
            print(f"查询书籍内容失败: {e}")
            book["has_content"] = False
            book["content_id"] = None
    
    conn.close()
    
    # 根据用户画像调整推荐理由
    for book in all_books:
        if life_stage == "职场新人":
            if book["category"] == "心理学":
                book["reason"] = f"基于你的职场阅读背景，这本书能让你在紧张的学习中找到平衡，同时加深对人性的理解，对职场人际关系很有帮助。"
            elif book["category"] == "文学":
                book["reason"] = f"在职场技能学习之余，这本书能为你提供情感的滋养和思维的放松，帮你保持内心的平衡。"
        elif life_stage == "自我提升者":
            if book["category"] == "心理学":
                book["reason"] = f"这本书与你的自我成长目标高度契合，能帮你更深入地理解自己和他人的心理机制。"
        
        # 根据情感需求调整
        if "心理治愈" in emotional_needs and book["emotional_tone"] == "治愈":
            book["reason"] += " 特别适合你当前的心理调节需求。"
    
    return all_books
