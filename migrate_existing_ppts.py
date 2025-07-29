#!/usr/bin/env python3
"""
迁移现有PPT数据到用户数据库
"""
import os
import json
import sqlite3
import re
from pathlib import Path

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 创建sessions表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 创建PPT表，关联用户
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ppts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            cover_url TEXT,
            category_id TEXT,
            category_name TEXT,
            category_color TEXT,
            category_icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_default_user():
    """创建默认用户"""
    import hashlib
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # 检查是否已存在默认用户
    cursor.execute('SELECT id FROM users WHERE username = ?', ('default_user',))
    user = cursor.fetchone()
    
    if user:
        print(f"默认用户已存在，ID: {user[0]}")
        conn.close()
        return user[0]
    
    # 创建默认用户
    password_hash = hashlib.sha256("default123".encode()).hexdigest()
    cursor.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    ''', ('default_user', 'default@example.com', password_hash))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"创建默认用户成功，ID: {user_id}")
    return user_id

def extract_author_from_book_data(book_data):
    """从book_data中提取作者信息"""
    author = "未知作者"
    
    if isinstance(book_data, dict):
        if 'author' in book_data:
            author = book_data['author']
        elif 'raw_content' in book_data:
            content_str = str(book_data['raw_content'])
            author_match = re.search(r'"author":\s*"([^"]+)"', content_str)
            if author_match:
                author = author_match.group(1)
    
    return author

def migrate_existing_ppts(user_id):
    """迁移现有的PPT数据"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("outputs目录不存在")
        return
    
    migrated_count = 0
    
    for session_dir in outputs_dir.iterdir():
        if not session_dir.is_dir():
            continue
        
        session_id = session_dir.name
        data_file = session_dir / "data.json"
        
        if not data_file.exists():
            print(f"跳过 {session_id}: 没有data.json文件")
            continue
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            topic = data.get('topic', session_id)
            book_data = data.get('book_data', {})
            
            # 提取作者信息
            author = extract_author_from_book_data(book_data)
            
            # 提取分类信息
            category_id = book_data.get('category_id', 'literature')
            category_name = book_data.get('category_name', '文学类')
            category_color = book_data.get('category_color', '#E74C3C')
            category_icon = book_data.get('category_icon', '📖')
            
            # 获取封面URL
            cover_url = None
            if 'cover_url' in book_data:
                cover_url = book_data['cover_url']
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM ppts WHERE session_id = ?', (session_id,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"跳过 {session_id}: 已存在")
                continue
            
            # 插入PPT数据
            cursor.execute('''
                INSERT INTO ppts 
                (session_id, user_id, title, author, cover_url, category_id, category_name, category_color, category_icon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, topic, author, cover_url, category_id, category_name, category_color, category_icon))
            
            migrated_count += 1
            print(f"迁移 {session_id}: {topic} - {author}")
            
        except Exception as e:
            print(f"迁移 {session_id} 失败: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n迁移完成！共迁移 {migrated_count} 个PPT")

def main():
    """主函数"""
    print("开始迁移现有PPT数据...")
    
    # 初始化数据库
    init_database()
    print("数据库初始化完成")
    
    # 创建默认用户
    user_id = create_default_user()
    
    # 迁移PPT数据
    migrate_existing_ppts(user_id)
    
    print("\n迁移脚本执行完成！")
    print("默认用户信息:")
    print("用户名: default_user")
    print("密码: default123")
    print("邮箱: default@example.com")

if __name__ == "__main__":
    main() 