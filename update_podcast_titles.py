#!/usr/bin/env python3
"""
更新播客标题脚本
"""

import sqlite3

def update_podcast_titles():
    """更新播客标题"""
    # 标题映射
    title_mapping = {
        '5f0fa2d5': '《朱元璋》',
        '59a11cd0': '《边城》', 
        'efd2e377': '《三体》',
        '2bd0dab9': '《百年孤独》',
        '20250817_201248': '书籍排行榜'
    }
    
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        for session_key, new_title in title_mapping.items():
            cursor.execute('''
                UPDATE podcasts 
                SET book_title = ? 
                WHERE session_id LIKE ?
            ''', (new_title, f'%{session_key}%'))
            
            print(f"✅ 更新: {session_key} -> {new_title}")
        
        conn.commit()
        conn.close()
        
        print("✅ 所有播客标题更新完成")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")

if __name__ == "__main__":
    update_podcast_titles()