#!/usr/bin/env python3
"""
更新播客数据库脚本
添加play_count字段并初始化现有数据
"""

import sqlite3
import os

def update_podcast_database():
    """更新播客数据库结构"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        # 检查play_count列是否存在
        cursor.execute("PRAGMA table_info(podcasts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'play_count' not in columns:
            print("添加play_count列...")
            cursor.execute('ALTER TABLE podcasts ADD COLUMN play_count INTEGER DEFAULT 0')
            print("✅ play_count列添加成功")
        else:
            print("✅ play_count列已存在")
        
        # 更新现有记录的play_count为0（如果为NULL）
        cursor.execute('UPDATE podcasts SET play_count = 0 WHERE play_count IS NULL')
        
        conn.commit()
        conn.close()
        
        print("✅ 播客数据库更新完成")
        
    except Exception as e:
        print(f"❌ 更新播客数据库失败: {e}")

if __name__ == "__main__":
    update_podcast_database()