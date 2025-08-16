#!/usr/bin/env python3
"""
引导推荐智能体演示脚本
直接体验核心功能
"""

import asyncio
from guided_recommendation_agent import GuidedRecommendationAgent
import sqlite3
from datetime import datetime

def setup_demo_data():
    """设置演示数据"""
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
    
    # 清除旧数据
    cursor.execute("DELETE FROM reading_history WHERE user_id = 1")
    
    # 添加演示数据 - 职场新人小张的阅读记录
    demo_books = [
        ("高效能人士的七个习惯", "史蒂芬·柯维", "2024-01-15", 5, "很有启发"),
        ("金字塔原理", "芭芭拉·明托", "2024-02-01", 4, "逻辑思维提升"),
        ("非暴力沟通", "马歇尔·卢森堡", "2024-02-20", 5, "改变沟通方式"),
        ("刻意练习", "安德斯·艾利克森", "2024-03-05", 4, "技能提升方法"),
        ("深度工作", "卡尔·纽波特", "2024-03-20", 5, "专注力训练")
    ]
    
    for title, author, date, rating, notes in demo_books:
        cursor.execute('''
            INSERT INTO reading_history (user_id, book_title, author, completion_date, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (1, title, author, date, rating, notes))
    
    conn.commit()
    conn.close()
    print("✅ 演示数据已设置（模拟职场新人小张的阅读记录）")

async def demo_conversation():
    """演示完整的推荐对话流程"""
    print("\n" + "="*50)
    print("🤖 引导推荐智能体演示")
    print("="*50)
    
    # 初始化智能体
    agent = GuidedRecommendationAgent()
    
    # 开始推荐会话
    print("\n📊 正在分析用户阅读数据...")
    session_data = await agent.start_recommendation_session(user_id=1)
    
    print(f"\n🎯 用户画像分析结果：")
    profile = session_data['user_profile']
    print(f"   阅读频率：{profile.get('reading_frequency', '未知')}")
    print(f"   偏好类别：{', '.join(profile.get('preferred_categories', []))}")
    print(f"   生活阶段：{profile.get('current_life_stage', '未知')}")
    print(f"   情感需求：{', '.join(profile.get('emotional_needs', []))}")
    print(f"   最近阅读：{', '.join(profile.get('recent_books', [])[:3])}")
    
    print(f"\n💬 智能体开场：")
    print(f"   {session_data['message']}")
    
    # 模拟用户回复和对话流程
    conversations = [
        ("是的，刚毕业半年，感觉要学的太多了。", "确认职场新人身份"),
        ("确实...感觉没时间读闲书。", "承认缺乏放松阅读"),
        ("好的，我想试试看。", "接受推荐建议")
    ]
    
    for user_msg, description in conversations:
        print(f"\n👤 用户回复：{user_msg}")
        print(f"   ({description})")
        
        response = await agent.continue_conversation(user_id=1, user_response=user_msg)
        
        print(f"\n🤖 智能体回复：")
        print(f"   {response['message']}")
        
        if response.get('recommendations'):
            print(f"\n📚 个性化推荐：")
            for i, book in enumerate(response['recommendations'], 1):
                print(f"   {i}. 《{book['title']}》- {book['author']}")
                print(f"      类别：{book['category']}")
                print(f"      推荐理由：{book['reason']}")
                print()

def demo_api_endpoints():
    """演示API端点"""
    print("\n" + "="*50)
    print("🔌 API端点演示")
    print("="*50)
    
    endpoints = [
        ("POST /api/recommendation/start", "开始推荐会话"),
        ("POST /api/recommendation/chat", "与智能体对话"),
        ("GET /api/recommendation/recommendations", "获取推荐列表"),
        ("GET /recommendation-agent", "访问推荐界面")
    ]
    
    print("\n可用的API端点：")
    for endpoint, description in endpoints:
        print(f"   {endpoint} - {description}")
    
    print(f"\n🌐 Web界面访问：")
    print(f"   启动应用：conda activate xunfei && python app.py")
    print(f"   访问地址：http://localhost:8000/recommendation-agent")

def demo_features():
    """演示核心特性"""
    print("\n" + "="*50)
    print("✨ 核心特性展示")
    print("="*50)
    
    features = [
        ("📊 智能数据分析", "自动分析用户阅读历史，构建个人画像"),
        ("💬 引导式对话", "通过自然对话挖掘用户真实需求"),
        ("🎯 精准推荐", "基于用户状态和需求提供个性化推荐"),
        ("🔄 持续学习", "根据用户反馈不断优化推荐策略"),
        ("🎨 美观界面", "现代化的聊天界面，支持实时对话"),
        ("📱 响应式设计", "支持桌面和移动设备访问")
    ]
    
    for feature, description in features:
        print(f"   {feature} {description}")

async def main():
    """主演示函数"""
    print("🚀 引导式书籍推荐智能体 - 功能演示")
    
    # 设置演示数据
    setup_demo_data()
    
    # 演示核心特性
    demo_features()
    
    # 演示完整对话流程
    await demo_conversation()
    
    # 演示API端点
    demo_api_endpoints()
    
    print(f"\n" + "="*50)
    print("🎉 演示完成！")
    print("="*50)
    print("\n💡 体验建议：")
    print("   1. 运行 'python app.py' 启动完整应用")
    print("   2. 访问 http://localhost:8000/recommendation-agent")
    print("   3. 与智能体对话，体验个性化推荐")
    print("   4. 尝试不同的回复，看推荐如何变化")

if __name__ == "__main__":
    asyncio.run(main())