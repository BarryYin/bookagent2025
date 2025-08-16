"""
引导式书籍推荐API
提供与引导推荐智能体交互的REST API端点
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import json
from datetime import datetime

from guided_recommendation_agent import GuidedRecommendationAgent

router = APIRouter(prefix="/api/recommendation", tags=["recommendation"])

# 初始化智能体
recommendation_agent = GuidedRecommendationAgent()

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class ReadingHistoryRequest(BaseModel):
    book_title: str
    author: str
    completion_date: str
    rating: Optional[int] = None
    notes: Optional[str] = None

class UserProfileRequest(BaseModel):
    username: str
    email: str

# 模拟用户数据（实际应用中应该从认证系统获取）
MOCK_USER_ID = 1

def get_user_id_from_request(request: Request) -> int:
    """从请求中获取用户ID（简化版）"""
    # 实际应用中应该从session或token中获取
    return MOCK_USER_ID

@router.post("/start")
async def start_recommendation_session(request: Request):
    """开始引导推荐会话"""
    try:
        user_id = get_user_id_from_request(request)
        result = await recommendation_agent.start_recommendation_session(user_id)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_agent(chat_request: ChatRequest, request: Request):
    """与推荐智能体对话"""
    try:
        user_id = get_user_id_from_request(request)
        result = await recommendation_agent.continue_conversation(
            user_id, 
            chat_request.message
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def get_user_reading_profile(request: Request):
    """获取用户阅读档案"""
    try:
        user_id = get_user_id_from_request(request)
        profile = recommendation_agent.analyzer.analyze_reading_patterns(user_id)
        return JSONResponse(content=profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reading-history")
async def add_reading_history(history_request: ReadingHistoryRequest, request: Request):
    """添加阅读历史"""
    try:
        user_id = get_user_id_from_request(request)
        
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
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
        
        cursor.execute('''
            INSERT INTO reading_history (user_id, book_title, author, completion_date, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            history_request.book_title,
            history_request.author,
            history_request.completion_date,
            history_request.rating,
            history_request.notes
        ))
        
        conn.commit()
        conn.close()
        
        return JSONResponse(content={"message": "阅读历史添加成功"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(request: Request):
    """获取个性化推荐"""
    try:
        user_id = get_user_id_from_request(request)
        
        # 获取用户画像
        profile = recommendation_agent.analyzer.analyze_reading_patterns(user_id)
        
        # 生成推荐
        recommendations = recommendation_agent.recommendation_engine.recommend_books(
            profile, {}
        )
        
        # 格式化推荐结果
        formatted_recommendations = [
            {
                "title": book.title,
                "author": book.author,
                "category": book.category,
                "description": book.description,
                "difficulty": book.difficulty_level,
                "emotional_tone": book.emotional_tone,
                "reading_time": book.reading_time,
                "tags": book.tags
            }
            for book in recommendations
        ]
        
        return JSONResponse(content={
            "recommendations": formatted_recommendations,
            "user_profile": profile
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_book_categories():
    """获取书籍分类信息"""
    try:
        categories = [
            "职场技能", "心理学", "文学", "历史", "哲学", 
            "科普", "女性议题", "人生思考", "自我成长"
        ]
        
        return JSONResponse(content={"categories": categories})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mock-data")
async def add_mock_data(request: Request):
    """添加模拟数据用于测试"""
    try:
        user_id = get_user_id_from_request(request)
        
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 创建表
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
        
        # 添加模拟数据
        mock_data = [
            ("高效能人士的七个习惯", "史蒂芬·柯维", "2024-01-15", 5, "很有启发，正在实践"),
            ("金字塔原理", "芭芭拉·明托", "2024-02-01", 4, "逻辑思维的利器"),
            ("非暴力沟通", "马歇尔·卢森堡", "2024-02-20", 5, "改变了我的沟通方式"),
            ("刻意练习", "安德斯·艾利克森", "2024-03-10", 4, "方法论很实用"),
            ("深度工作", "卡尔·纽波特", "2024-03-25", 5, "提升了工作效率")
        ]
        
        for title, author, date, rating, notes in mock_data:
            cursor.execute('''
                INSERT INTO reading_history (user_id, book_title, author, completion_date, rating, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, author, date, rating, notes))
        
        conn.commit()
        conn.close()
        
        return JSONResponse(content={"message": "模拟数据添加成功"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点
@router.get("/health")
async def health_check():
    """健康检查"""
    return JSONResponse(content={"status": "healthy", "timestamp": str(datetime.now())})