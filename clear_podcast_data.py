#!/usr/bin/env python3
"""
清理播客数据库中的假数据
"""
import sqlite3
import os

def clear_podcast_data():
    """清理播客数据库中的所有数据"""
    try:
        # 连接数据库
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        # 删除所有播客记录
        cursor.execute("DELETE FROM podcasts")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='podcasts'")
        
        conn.commit()
        
        # 检查删除结果
        cursor.execute("SELECT COUNT(*) FROM podcasts")
        count = cursor.fetchone()[0]
        
        print(f"✅ 播客数据清理完成，剩余记录数: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 清理播客数据失败: {e}")

if __name__ == "__main__":
    clear_podcast_data()