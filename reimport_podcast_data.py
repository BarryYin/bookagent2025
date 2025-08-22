#!/usr/bin/env python3
"""
重新导入播客数据脚本
清除现有数据库数据并重新导入 podcast_audio 文件夹中的音频文件
"""

import sqlite3
import os
import re
from datetime import datetime
from podcast_database import init_podcast_database, save_podcast_to_database

def clear_podcast_database():
    """清除播客数据库中的所有数据"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        # 删除所有播客记录
        cursor.execute("DELETE FROM podcasts")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='podcasts'")
        
        conn.commit()
        conn.close()
        
        print("✅ 播客数据库已清空")
        
    except Exception as e:
        print(f"❌ 清空播客数据库失败: {e}")

def extract_info_from_filename(filename):
    """从文件名提取信息"""
    # 移除扩展名
    name = os.path.splitext(filename)[0]
    
    # 提取时间戳
    timestamp_match = re.search(r'(\d{8}_\d{6})$', name)
    timestamp = timestamp_match.group(1) if timestamp_match else None
    
    # 提取会话ID（如果存在）
    session_id_match = re.search(r'([a-f0-9]{30,})', name)
    session_id = session_id_match.group(1) if session_id_match else None
    
    # 根据文件名模式确定书名
    if name.startswith('reading_podcast_ai_'):
        book_title = "AI读后感播客"
        if session_id:
            book_title += f" ({session_id[:8]})"
    elif name.startswith('podcast_'):
        book_title = "播客节目"
        if timestamp:
            book_title += f" ({timestamp})"
    else:
        book_title = name
    
    return {
        'session_id': session_id or name,
        'book_title': book_title,
        'timestamp': timestamp
    }

def import_audio_files():
    """导入音频文件到数据库"""
    audio_dir = '/Users/mac/Documents/GitHub/fogsight/podcast_audio'
    
    if not os.path.exists(audio_dir):
        print(f"❌ 音频文件夹不存在: {audio_dir}")
        return
    
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    
    if not audio_files:
        print("❌ 未找到音频文件")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件")
    
    for filename in audio_files:
        file_path = os.path.join(audio_dir, filename)
        
        # 提取文件信息
        info = extract_info_from_filename(filename)
        
        # 生成描述
        description = f"这是一个精彩的读后感播客，基于 {info['book_title']} 生成"
        
        # 生成脚本内容
        script_content = f"播客内容：{info['book_title']}\n文件：{filename}\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 保存到数据库
        podcast_id = save_podcast_to_database(
            session_id=info['session_id'],
            book_title=info['book_title'],
            book_author="AI助手",
            description=description,
            script_content=script_content,
            audio_file_path=file_path,
            user_id="system"
        )
        
        if podcast_id:
            print(f"✅ 导入成功: {filename} -> ID: {podcast_id}")
        else:
            print(f"❌ 导入失败: {filename}")

def main():
    """主函数"""
    print("🚀 开始重新导入播客数据...")
    
    # 1. 初始化数据库
    print("\n1. 初始化数据库...")
    init_podcast_database()
    
    # 2. 清空现有数据
    print("\n2. 清空现有数据...")
    clear_podcast_database()
    
    # 3. 导入音频文件
    print("\n3. 导入音频文件...")
    import_audio_files()
    
    # 4. 验证导入结果
    print("\n4. 验证导入结果...")
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM podcasts WHERE status = 'active'")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ 导入完成，共有 {count} 个播客记录")
    except Exception as e:
        print(f"❌ 验证失败: {e}")

if __name__ == "__main__":
    main()