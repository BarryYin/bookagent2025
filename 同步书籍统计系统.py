#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def extract_book_info_from_data(data: dict) -> Tuple[str, str, dict]:
    """从data.json中提取书籍信息"""
    
    title = "未知书籍"
    author = "未知作者"
    category_info = {
        'category_id': 'literature',
        'category_name': '文学类',
        'category_color': '#E74C3C',
        'category_icon': '📖'
    }
    
    # 方法1：直接从data中获取
    if 'title' in data and data['title'] and data['title'] != 'Unknown':
        title = data['title']
    
    if 'author' in data and data['author'] and data['author'] != 'Unknown':
        author = data['author']
    
    # 方法2：从topic字段获取
    if title == "未知书籍" and 'topic' in data and data['topic']:
        title = data['topic']
    
    # 方法3：从book_data中提取
    if 'book_data' in data:
        book_data = data['book_data']
        
        # 从分类信息中获取
        if isinstance(book_data, dict):
            if 'category_id' in book_data:
                category_info['category_id'] = book_data['category_id']
            if 'category_name' in book_data:
                category_info['category_name'] = book_data['category_name']
            if 'category_color' in book_data:
                category_info['category_color'] = book_data['category_color']
            if 'category_icon' in book_data:
                category_info['category_icon'] = book_data['category_icon']
        
        # 从raw_content中解析
        if 'raw_content' in book_data:
            raw_content = str(book_data['raw_content'])
            
            # 提取书名
            title_patterns = [
                r'"book_title":\s*"([^"]+)"',
                r'"title":\s*"([^"]+)"',
                r'书名[：:]\s*《?([^》\n]+)》?',
                r'《([^》]+)》'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, raw_content)
                if match and title == "未知书籍":
                    extracted_title = match.group(1).strip()
                    if extracted_title and extracted_title != "Unknown":
                        title = extracted_title
                        break
            
            # 提取作者
            author_patterns = [
                r'"author":\s*"([^"]+)"',
                r'作者[：:]\s*([^\n\r，,]+)',
                r'by\s+([^\n\r，,]+)',
                r'著[：:]?\s*([^\n\r，,]+)'
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, raw_content)
                if match and author == "未知作者":
                    extracted_author = match.group(1).strip()
                    if extracted_author and extracted_author != "Unknown":
                        author = extracted_author
                        break
    
    # 清理标题
    title = re.sub(r'\s*-\s*(PPT演示|Bookagent\s*智能演示|FogSight\s*AI\s*智能演示).*$', '', title)
    title = re.sub(r'\s*\(.*?\)\s*', '', title)  # 移除括号内容
    title = title.strip()
    
    # 清理作者
    author = re.sub(r'\s*\(.*?\)\s*', '', author)  # 移除括号内容
    author = author.strip()
    
    return title, author, category_info

def sync_books_to_database():
    """同步所有书籍到数据库统计系统"""
    
    print("🔄 开始同步书籍到统计系统...")
    
    # 连接数据库
    conn = sqlite3.connect('fogsight.db')
    cursor = conn.cursor()
    
    # 获取现有的数据库记录
    cursor.execute('SELECT session_id, title, author FROM ppts')
    existing_ppts = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    cursor.execute('SELECT book_title, author FROM book_statistics')
    existing_stats = set((row[0], row[1] or 'Unknown') for row in cursor.fetchall())
    
    # 扫描outputs目录
    outputs_dir = 'outputs'
    session_dirs = [d for d in os.listdir(outputs_dir) if os.path.isdir(os.path.join(outputs_dir, d))]
    
    print(f"📁 找到 {len(session_dirs)} 个会话目录")
    
    synced_count = 0
    updated_count = 0
    stats_added_count = 0
    
    for session_id in session_dirs:
        data_path = os.path.join(outputs_dir, session_id, 'data.json')
        
        if not os.path.exists(data_path):
            continue
            
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取书籍信息
            title, author, category_info = extract_book_info_from_data(data)
            
            # 检查是否需要更新ppts表
            if session_id in existing_ppts:
                existing_title, existing_author = existing_ppts[session_id]
                
                # 如果现有信息不完整，更新它
                if (existing_title in ['未知书籍', 'Unknown', ''] or 
                    existing_author in ['未知作者', 'Unknown', '', None]):
                    
                    cursor.execute('''
                        UPDATE ppts 
                        SET title = ?, author = ?, 
                            category_id = ?, category_name = ?, 
                            category_color = ?, category_icon = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = ?
                    ''', (title, author, 
                          category_info['category_id'], category_info['category_name'],
                          category_info['category_color'], category_info['category_icon'],
                          session_id))
                    
                    updated_count += 1
                    print(f"✏️  更新: 《{title}》 - {author} ({session_id[:8]}...)")
            else:
                # 添加新记录到ppts表
                cursor.execute('''
                    INSERT INTO ppts (
                        session_id, user_id, title, author, 
                        category_id, category_name, category_color, category_icon,
                        view_count, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (session_id, 1, title, author,  # 默认user_id为1
                      category_info['category_id'], category_info['category_name'],
                      category_info['category_color'], category_info['category_icon'], 0))
                
                synced_count += 1
                print(f"➕ 新增: 《{title}》 - {author} ({session_id[:8]}...)")
            
            # 检查book_statistics表
            book_key = (title, author)
            if book_key not in existing_stats:
                # 检查是否有访问记录
                cursor.execute('SELECT SUM(view_count) FROM ppts WHERE title = ? AND author = ?', (title, author))
                total_views = cursor.fetchone()[0] or 0
                
                cursor.execute('SELECT COUNT(*) FROM ppts WHERE title = ? AND author = ?', (title, author))
                ppt_count = cursor.fetchone()[0] or 0
                
                # 添加到book_statistics
                cursor.execute('''
                    INSERT INTO book_statistics (
                        book_title, author, total_views, ppt_count, 
                        created_at, category_name
                    ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                ''', (title, author, total_views, ppt_count, category_info['category_name']))
                
                existing_stats.add(book_key)
                stats_added_count += 1
                print(f"📊 统计表新增: 《{title}》 - {author}")
                
        except Exception as e:
            print(f"❌ 处理 {session_id} 时出错: {e}")
            continue
    
    # 更新book_statistics中的统计数据
    print("\n🔄 更新统计数据...")
    cursor.execute('''
        UPDATE book_statistics 
        SET total_views = (
            SELECT COALESCE(SUM(view_count), 0) 
            FROM ppts 
            WHERE ppts.title = book_statistics.book_title 
            AND ppts.author = book_statistics.author
        ),
        ppt_count = (
            SELECT COUNT(*) 
            FROM ppts 
            WHERE ppts.title = book_statistics.book_title 
            AND ppts.author = book_statistics.author
        ),
        last_viewed = (
            SELECT MAX(updated_at) 
            FROM ppts 
            WHERE ppts.title = book_statistics.book_title 
            AND ppts.author = book_statistics.author
            AND view_count > 0
        )
    ''')
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n✅ 同步完成!")
    print(f"   新增书籍: {synced_count} 本")
    print(f"   更新书籍: {updated_count} 本")
    print(f"   统计表新增: {stats_added_count} 本")
    
    return synced_count + updated_count > 0

def show_current_stats():
    """显示当前统计数据"""
    
    conn = sqlite3.connect('fogsight.db')
    cursor = conn.cursor()
    
    # 从ppts表统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total_books,
            COUNT(DISTINCT title) as unique_titles,
            SUM(view_count) as total_views,
            COUNT(CASE WHEN view_count > 0 THEN 1 END) as viewed_books
        FROM ppts
    ''')
    
    stats = cursor.fetchone()
    
    print(f"\n📊 当前统计数据:")
    print(f"   总PPT数: {stats[0]}")
    print(f"   独立书籍数: {stats[1]}")
    print(f"   总访问量: {stats[2]}")
    print(f"   有访问记录的PPT: {stats[3]}")
    
    # book_statistics表统计
    cursor.execute('SELECT COUNT(*) FROM book_statistics')
    stats_count = cursor.fetchone()[0]
    print(f"   统计表中的书籍: {stats_count}")
    
    # 显示最新的几本书
    cursor.execute('''
        SELECT title, author, view_count, created_at 
        FROM ppts 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    
    recent_books = cursor.fetchall()
    print(f"\n📚 最新的10本书:")
    for i, (title, author, views, created) in enumerate(recent_books, 1):
        print(f"   {i:2d}. 《{title}》 - {author or 'Unknown'} (访问{views}次)")
    
    conn.close()

if __name__ == "__main__":
    print("🔄 书籍统计系统同步工具")
    print("=" * 50)
    
    # 显示当前状态
    show_current_stats()
    
    # 执行同步
    success = sync_books_to_database()
    
    if success:
        print("\n" + "=" * 50)
        show_current_stats()
        print(f"\n💡 同步完成！现在所有生成的书籍都已加入统计系统")
    else:
        print("\n❌ 同步过程中没有发现需要处理的数据")