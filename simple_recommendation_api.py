"""
简化的引导推荐API
兼容现有FastAPI应用
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import json
from datetime import datetime

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
async def start_recommendation_session():
    """开始引导推荐会话"""
    try:
        setup_database()
        
        return {
            "message": DIALOGUE_TEMPLATES["start"],
            "user_profile": {
                "reading_frequency": "高频",
                "preferred_categories": ["职场技能"],
                "current_life_stage": "职场新人",
                "emotional_needs": ["成长指导"],
                "recent_books": ["高效能人士的七个习惯", "金字塔原理", "非暴力沟通"]
            },
            "session_id": f"session_{MOCK_USER_ID}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_agent(chat_request: ChatRequest):
    """与推荐智能体对话"""
    try:
        message = chat_request.message.lower()
        
        if "是的" in message or "开始" in message or "工作" in message:
            response = DIALOGUE_TEMPLATES["follow_up"]
        elif "推荐" in message or "书" in message:
            book = MOCK_BOOKS[0]
            response = DIALOGUE_TEMPLATES["recommendation"].format(
                book=book["title"],
                reason=book["reason"]
            )
        else:
            response = "很理解你的情况。让我为你推荐几本适合的书吧！"
            
        return {
            "message": response,
            "recommendations": MOCK_BOOKS,
            "turn": 1,
            "should_recommend": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

def setup_database():
    """设置数据库"""
    try:
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
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
        
        # 添加测试数据
        test_data = [
            (1, "高效能人士的七个习惯", "史蒂芬·柯维", "2024-01-15", 5, "很有启发"),
            (1, "金字塔原理", "芭芭拉·明托", "2024-02-01", 4, "逻辑思维"),
            (1, "非暴力沟通", "马歇尔·卢森堡", "2024-02-20", 5, "改变沟通方式")
        ]
        
        for user_id, title, author, date, rating, notes in test_data:
            cursor.execute('''
                INSERT OR IGNORE INTO reading_history (user_id, book_title, author, completion_date, rating, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, author, date, rating, notes))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"数据库设置失败: {e}")