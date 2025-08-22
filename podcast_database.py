import sqlite3
import os
from datetime import datetime

def init_podcast_database():
    """初始化播客数据库"""
    conn = sqlite3.connect('podcasts.db')
    cursor = conn.cursor()
    
    # 创建播客表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            book_title TEXT NOT NULL,
            book_author TEXT,
            description TEXT,
            script_content TEXT,
            audio_url TEXT,
            audio_file_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            user_id TEXT,
            tags TEXT,
            duration INTEGER,
            file_size INTEGER,
            play_count INTEGER DEFAULT 0
        )
    ''')
    
    # 添加play_count列（如果不存在）
    try:
        cursor.execute('ALTER TABLE podcasts ADD COLUMN play_count INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # 列已存在，忽略错误
        pass
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcasts_created_at ON podcasts(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcasts_book_title ON podcasts(book_title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcasts_status ON podcasts(status)')
    
    conn.commit()
    conn.close()
    print("✅ 播客数据库初始化完成")

def save_podcast_to_database(session_id, book_title, book_author, description, script_content, audio_url=None, audio_file_path=None, user_id=None):
    """保存播客到数据库"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        # 获取音频文件信息
        duration = None
        file_size = None
        if audio_file_path and os.path.exists(audio_file_path):
            file_size = os.path.getsize(audio_file_path)
            # 这里可以添加获取音频时长的逻辑
        
        # 插入或更新播客记录
        cursor.execute('''
            INSERT OR REPLACE INTO podcasts 
            (session_id, book_title, book_author, description, script_content, 
             audio_url, audio_file_path, user_id, duration, file_size, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, book_title, book_author, description, script_content,
              audio_url, audio_file_path, user_id, duration, file_size, datetime.now()))
        
        conn.commit()
        podcast_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ 播客已保存到数据库: {book_title} (ID: {podcast_id})")
        return podcast_id
        
    except Exception as e:
        print(f"❌ 保存播客到数据库失败: {e}")
        return None

def get_all_podcasts(limit=50, offset=0):
    """获取所有播客"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, book_title, book_author, description, 
                   audio_url, audio_file_path, created_at, duration, file_size, play_count
            FROM podcasts 
            WHERE status = 'active'
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        podcasts = []
        for row in rows:
            podcast = {
                'id': row[0],
                'session_id': row[1],
                'book_title': row[2],
                'book_author': row[3] or '用户',
                'description': row[4] or '这是一个精彩的读后感播客',
                'audio_url': row[5],
                'audio_file_path': row[6],
                'created_at': row[7],
                'duration': row[8],
                'file_size': row[9],
                'play_count': row[10] or 0
            }
            podcasts.append(podcast)
        
        return podcasts
        
    except Exception as e:
        print(f"❌ 获取播客列表失败: {e}")
        return []

def get_podcast_by_session_id(session_id):
    """根据会话ID获取播客"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, book_title, book_author, description, 
                   script_content, audio_url, audio_file_path, created_at
            FROM podcasts 
            WHERE session_id = ? AND status = 'active'
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'session_id': row[1],
                'book_title': row[2],
                'book_author': row[3],
                'description': row[4],
                'script_content': row[5],
                'audio_url': row[6],
                'audio_file_path': row[7],
                'created_at': row[8]
            }
        return None
        
    except Exception as e:
        print(f"❌ 获取播客失败: {e}")
        return None

def delete_podcast(podcast_id):
    """删除播客（软删除）"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE podcasts 
            SET status = 'deleted', updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), podcast_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 播客已删除: ID {podcast_id}")
        return True
        
    except Exception as e:
        print(f"❌ 删除播客失败: {e}")
        return False

def increment_play_count(session_id):
    """增加播客播放次数"""
    try:
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE podcasts 
            SET play_count = COALESCE(play_count, 0) + 1, updated_at = ?
            WHERE session_id = ? AND status = 'active'
        ''', (datetime.now(), session_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 播客播放次数已增加: {session_id}")
        return True
        
    except Exception as e:
        print(f"❌ 增加播放次数失败: {e}")
        return False

if __name__ == "__main__":
    # 初始化数据库
    init_podcast_database()