#!/usr/bin/env python3
"""
测试引导式书籍推荐系统
"""

import sqlite3
import requests
import json
from datetime import datetime

def setup_test_data():
    """设置测试数据"""
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
    
    # 添加测试数据
    test_data = [
        (1, "高效能人士的七个习惯", "史蒂芬·柯维", "2024-01-15", 5, "很有启发，正在实践"),
        (1, "金字塔原理", "芭芭拉·明托", "2024-02-01", 4, "逻辑思维的利器"),
        (1, "非暴力沟通", "马歇尔·卢森堡", "2024-02-20", 5, "改变了我的沟通方式"),
        (1, "刻意练习", "安德斯·艾利克森", "2024-03-10", 4, "方法论很实用"),
        (1, "深度工作", "卡尔·纽波特", "2024-03-25", 5, "提升了工作效率")
    ]
    
    for user_id, title, author, date, rating, notes in test_data:
        cursor.execute('''
            INSERT OR IGNORE INTO reading_history (user_id, book_title, author, completion_date, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, title, author, date, rating, notes))
    
    conn.commit()
    conn.close()
    print("✅ 测试数据已设置")

def test_recommendation_api():
    """测试推荐API"""
    base_url = "http://localhost:8000/api/recommendation"
    
    try:
        # 测试健康检查
        response = requests.get(f"{base_url}/health")
        print(f"健康检查: {response.status_code}")
        
        # 测试获取推荐
        response = requests.get(f"{base_url}/recommendations")
        print(f"获取推荐: {response.status_code}")
        if response.status_code == 200:
            print("推荐数据:", response.json())
        
        # 测试开始会话
        response = requests.post(f"{base_url}/start", json={"user_id": 1})
        print(f"开始会话: {response.status_code}")
        if response.status_code == 200:
            print("会话开始:", response.json())
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def test_direct_import():
    """直接测试模块导入"""
    try:
        from guided_recommendation_agent import GuidedRecommendationAgent
        agent = GuidedRecommendationAgent()
        print("✅ 智能体模块导入成功")
        
        # 测试分析功能
        profile = agent.analyzer.analyze_reading_patterns(1)
        print("✅ 阅读分析成功")
        print("用户档案:", profile)
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")

if __name__ == "__main__":
    print("=== 引导推荐系统测试 ===")
    setup_test_data()
    test_direct_import()
    print("\n请确保服务器已运行: python app.py")
    print("然后运行: python test_recommendation.py")