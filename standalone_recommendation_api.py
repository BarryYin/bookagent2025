"""
引导式书籍推荐API - 独立版本（无需认证）
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import sqlite3
from datetime import datetime
import os

# 创建路由
router = APIRouter(prefix="/api/standalone-recommendation", tags=["standalone-recommendation"])

class ChatRequest(BaseModel):
    message: str

# 扩展模拟推荐数据
MOCK_BOOKS = [
    {
        "title": "乌合之众",
        "author": "古斯塔夫·勒庞",
        "category": "心理学",
        "description": "群体心理学的经典之作",
        "difficulty": "入门",
        "emotional_tone": "思考",
        "reading_time": "中篇",
        "reason": "这本书能让你深入理解群体心理，对人性有更深刻的认识",
        "has_content": True,
        "content_id": "c2a25ac7-ff4d-4952-a43c-135cd9482a10"
    },
    {
        "title": "被讨厌的勇气",
        "author": "岸见一郎",
        "category": "心理学",
        "description": "阿德勒心理学入门",
        "difficulty": "入门",
        "emotional_tone": "治愈",
        "reading_time": "中篇",
        "reason": "适合你当前的阅读节奏，能帮助建立健康的自我认知",
        "has_content": False,
        "content_id": None
    },
    {
        "title": "小王子",
        "author": "安托万·德·圣埃克苏佩里",
        "category": "文学",
        "description": "童心未泯的哲学寓言",
        "difficulty": "入门",
        "emotional_tone": "治愈",
        "reading_time": "短篇",
        "reason": "简短但深刻的阅读体验，适合作为放松阅读",
        "has_content": True,
        "content_id": "9b70435a-c7b8-47c7-9ecf-084eaf6daf00"
    },
    {
        "title": "活着",
        "author": "余华",
        "category": "文学",
        "description": "中国当代文学经典",
        "difficulty": "中等",
        "emotional_tone": "沉思",
        "reading_time": "中篇",
        "reason": "这本书通过平凡人物的一生，展现了生命的韧性和人性的复杂",
        "has_content": True,
        "content_id": "c2a7f4ac-bda9-4a3d-8b18-90cbac0952b9"
    },
    {
        "title": "思考，快与慢",
        "author": "丹尼尔·卡尼曼",
        "category": "心理学",
        "description": "行为经济学和认知心理学的经典著作",
        "difficulty": "中等",
        "emotional_tone": "思考",
        "reading_time": "长篇",
        "reason": "这本书揭示了人类思维的两种模式，帮助你理解自己的决策过程",
        "has_content": False,
        "content_id": None
    },
    {
        "title": "三体",
        "author": "刘慈欣",
        "category": "科幻",
        "description": "中国科幻文学的里程碑",
        "difficulty": "中等",
        "emotional_tone": "震撼",
        "reading_time": "长篇",
        "reason": "这部作品展现了宏大的宇宙想象和深刻的哲学思考",
        "has_content": True,
        "content_id": "5fb16de9-35c1-42f9-ac37-c5e2c263f499"
    }
]

# 模拟对话模板
DIALOGUE_TEMPLATES = {
    "start": "你好！我是你的私人阅读顾问。我可以根据你的阅读偏好和需求推荐适合的书籍。你最近在读什么类型的书？",
    "follow_up": "我理解这种阅读需求。你平时更喜欢什么类型的书？小说、非虚构、心理学还是其他？",
    "recommendation": "基于我们的对话，我特别推荐《{book}》。这本书{reason}"
}

# 聊天历史记录
chat_history = {}

@router.post("/start")
async def start_recommendation_session():
    """开始引导推荐会话（无需认证）"""
    try:
        greeting_message = DIALOGUE_TEMPLATES["start"]
        session_id = f"standalone_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 初始化聊天历史
        chat_history[session_id] = []
        
        # 尝试从数据库获取一些真实的书籍数据
        real_books = get_real_books_from_database()
        
        return {
            "message": greeting_message,
            "user_profile": {
                "reading_frequency": "新用户",
                "preferred_categories": ["文学", "心理学", "科幻"],
                "current_life_stage": "探索阶段",
                "emotional_needs": ["兴趣发现", "知识拓展"],
                "recent_books": []
            },
            "session_id": session_id,
            "user_info": {
                "id": 0,
                "username": "访客用户"
            }
        }
    except Exception as e:
        print(f"启动会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_agent(chat_request: ChatRequest):
    """与推荐智能体对话（无需认证）"""
    try:
        message = chat_request.message.lower()
        
        # 简单的规则引擎
        if any(word in message for word in ["你好", "hi", "hello", "开始"]):
            response = "很高兴和你聊天！我是你的阅读顾问。你平时喜欢读什么类型的书？或者你现在有什么阅读需求？"
            return {
                "message": response,
                "recommendations": []
            }
        
        elif any(word in message for word in ["推荐", "建议", "什么书", "书单"]):
            response = "根据你的需求，我为你精心挑选了几本书。这些书既能满足你的阅读需求，又能带来不同的阅读体验。"
            
            # 尝试从数据库获取一些真实的书籍数据
            real_books = get_real_books_from_database()
            if real_books:
                # 如果成功获取到真实数据，使用真实数据
                return {
                    "message": response,
                    "recommendations": real_books
                }
            else:
                # 否则使用模拟数据
                return {
                    "message": response,
                    "recommendations": MOCK_BOOKS
                }
        
        elif any(word in message for word in ["心理", "成长", "自我"]):
            response = "心理学和自我成长类的书籍确实能帮助我们更好地认识自己。我为你推荐了几本这方面的经典著作。"
            filtered_books = [book for book in MOCK_BOOKS if book["category"] == "心理学"]
            return {
                "message": response,
                "recommendations": filtered_books
            }
        
        elif any(word in message for word in ["文学", "小说", "故事"]):
            response = "文学作品能带给我们不同的情感体验和思考。这里有一些我认为值得一读的文学作品。"
            filtered_books = [book for book in MOCK_BOOKS if book["category"] == "文学"]
            return {
                "message": response,
                "recommendations": filtered_books
            }
            
        elif any(word in message for word in ["科幻", "科学", "未来"]):
            response = "科幻作品能带我们探索未知的可能性，思考科技与人性的关系。这里有一些优秀的科幻作品推荐。"
            filtered_books = [book for book in MOCK_BOOKS if book["category"] == "科幻"]
            return {
                "message": response,
                "recommendations": filtered_books
            }
        
        else:
            response = "我理解你的想法。每个人的阅读需求都不同，这正是个性化推荐的价值所在。我为你推荐了几本可能符合你兴趣的书籍，希望能对你有所帮助。"
            return {
                "message": response,
                "recommendations": MOCK_BOOKS[:3]  # 只返回前三本，避免信息过载
            }
            
    except Exception as e:
        print(f"聊天处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_real_books_from_database():
    """尝试从数据库获取真实的书籍数据"""
    try:
        if not os.path.exists("fogsight.db"):
            print("数据库文件不存在，使用模拟数据")
            return None
            
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 检查ppts表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ppts'")
        if not cursor.fetchone():
            print("ppts表不存在，使用模拟数据")
            conn.close()
            return None
        
        # 获取一些真实的书籍数据
        cursor.execute("""
            SELECT id, title, author, category_name, description, created_at 
            FROM ppts 
            ORDER BY created_at DESC 
            LIMIT 6
        """)
        
        books = cursor.fetchall()
        conn.close()
        
        if not books:
            print("没有找到书籍数据，使用模拟数据")
            return None
        
        # 转换为推荐格式
        real_books = []
        for book in books:
            book_id, title, author, category, description, created_at = book
            
            # 确保数据完整性
            if not title or not author:
                continue
                
            real_books.append({
                "title": title,
                "author": author or "未知作者",
                "category": category or "未分类",
                "description": description or f"{title}的精彩介绍",
                "difficulty": "中等",
                "emotional_tone": "思考",
                "reading_time": "中篇",
                "reason": f"这本书在我们的图书馆中很受欢迎，已经有完整的内容生成",
                "has_content": True,
                "content_id": book_id
            })
        
        return real_books if real_books else None
        
    except Exception as e:
        print(f"获取真实书籍数据失败: {e}")
        return None
