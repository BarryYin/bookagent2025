#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re
from datetime import datetime

def auto_sync_book_to_stats(session_id: str, book_data: dict):
    """自动同步新生成的书籍到统计系统"""
    import time
    
    # 重试机制
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        conn = None
        try:
            # 提取书籍信息
            title = "未知书籍"
            author = "未知作者"
            
            # 方法1：直接从book_data获取
            if 'title' in book_data and book_data['title']:
                title = book_data['title']
            if 'author' in book_data and book_data['author']:
                author = book_data['author']
            
            # 方法2：从topic字段获取
            if title == "未知书籍" and 'topic' in book_data:
                title = book_data['topic']
            
            # 方法3：从raw_content中提取
            if 'raw_content' in book_data:
                raw_content = str(book_data['raw_content'])
                
                # 提取更准确的信息
                title_match = re.search(r'"book_title":\s*"([^"]+)"', raw_content)
                if title_match and title == "未知书籍":
                    title = title_match.group(1)
                
                author_match = re.search(r'"author":\s*"([^"]+)"', raw_content)
                if author_match and author == "未知作者":
                    author = author_match.group(1)
            
            # 清理标题和作者
            title = re.sub(r'\s*-\s*(PPT演示|Bookagent\s*智能演示|FogSight\s*AI\s*智能演示).*$', '', title)
            title = re.sub(r'\s*\(.*?\)\s*', '', title).strip()
            author = re.sub(r'\s*\(.*?\)\s*', '', author).strip()
            
            # 获取分类信息
            category_info = {
                'category_id': book_data.get('category_id', 'literature'),
                'category_name': book_data.get('category_name', '文学类'),
                'category_color': book_data.get('category_color', '#E74C3C'),
                'category_icon': book_data.get('category_icon', '📖')
            }
            
            # 连接数据库，设置超时
            conn = sqlite3.connect('fogsight.db', timeout=10.0)
            cursor = conn.cursor()
            
            # 检查ppts表是否已存在
            cursor.execute('SELECT id FROM ppts WHERE session_id = ?', (session_id,))
            if cursor.fetchone():
                # 已存在，更新信息
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
                print(f"🔄 更新PPT记录: 《{title}》 - {author}")
            else:
                # 添加到ppts表
                cursor.execute('''
                    INSERT INTO ppts (
                        session_id, user_id, title, author, 
                        category_id, category_name, category_color, category_icon,
                        view_count, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (session_id, 1, title, author,
                      category_info['category_id'], category_info['category_name'],
                      category_info['category_color'], category_info['category_icon'], 0))
                print(f"➕ 新增PPT记录: 《{title}》 - {author}")
            
            # 检查book_statistics表
            cursor.execute('SELECT id FROM book_statistics WHERE book_title = ? AND author = ?', (title, author))
            existing_stat = cursor.fetchone()
            
            if not existing_stat:
                # 添加到统计表
                try:
                    cursor.execute('''
                        INSERT INTO book_statistics (
                            book_title, author, total_views, ppt_count, 
                            created_at, category_name
                        ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                    ''', (title, author, 0, 1, category_info['category_name']))
                    print(f"📊 新增统计记录: 《{title}》 - {author}")
                except sqlite3.IntegrityError:
                    # 如果违反唯一约束，更新现有记录
                    cursor.execute('''
                        UPDATE book_statistics 
                        SET ppt_count = (
                            SELECT COUNT(*) FROM ppts 
                            WHERE title = ? AND author = ?
                        )
                        WHERE book_title = ? AND author = ?
                    ''', (title, author, title, author))
                    print(f"📊 更新统计记录（约束冲突）: 《{title}》 - {author}")
            else:
                # 更新PPT数量
                cursor.execute('''
                    UPDATE book_statistics 
                    SET ppt_count = (
                        SELECT COUNT(*) FROM ppts 
                        WHERE title = ? AND author = ?
                    )
                    WHERE book_title = ? AND author = ?
                ''', (title, author, title, author))
                print(f"📊 更新统计记录: 《{title}》 - {author}")
            
            conn.commit()
            conn.close()
            
            print(f"🎯 自动同步完成: 《{title}》 - {author}")
            return True
            
        except sqlite3.OperationalError as e:
            if conn:
                conn.close()
            if "database is locked" in str(e):
                print(f"⚠️ 数据库锁定，第 {attempt + 1} 次重试...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            print(f"❌ 数据库操作失败: {e}")
            return False
        except Exception as e:
            if conn:
                conn.close()
            print(f"❌ 自动同步失败 (尝试 {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return False
    
    print(f"❌ 自动同步最终失败，已重试 {max_retries} 次")
    return False

def record_book_view_enhanced(session_id: str):
    """增强版访问量记录"""
    import time
    
    # 重试机制
    max_retries = 3
    retry_delay = 0.2
    
    for attempt in range(max_retries):
        conn = None
        try:
            conn = sqlite3.connect('fogsight.db', timeout=5.0)
            cursor = conn.cursor()
            
            # 更新ppts表
            cursor.execute('UPDATE ppts SET view_count = view_count + 1 WHERE session_id = ?', (session_id,))
            
            # 获取书籍信息
            cursor.execute('SELECT title, author FROM ppts WHERE session_id = ?', (session_id,))
            result = cursor.fetchone()
            
            if result:
                title, author = result
                
                # 更新book_statistics表
                cursor.execute('''
                    UPDATE book_statistics 
                    SET total_views = total_views + 1,
                        last_viewed = CURRENT_TIMESTAMP
                    WHERE book_title = ? AND author = ?
                ''', (title, author))
                
                # 如果book_statistics中不存在该书，创建记录
                if cursor.rowcount == 0:
                    try:
                        cursor.execute('''
                            INSERT INTO book_statistics (
                                book_title, author, total_views, ppt_count, 
                                last_viewed, created_at, category_name
                            ) VALUES (?, ?, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '文学类')
                        ''', (title, author))
                    except sqlite3.IntegrityError:
                        # 如果有唯一约束冲突，再次尝试更新
                        cursor.execute('''
                            UPDATE book_statistics 
                            SET total_views = total_views + 1,
                                last_viewed = CURRENT_TIMESTAMP
                            WHERE book_title = ? AND author = ?
                        ''', (title, author))
                
                print(f"📈 访问量+1: 《{title}》 - {author}")
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.OperationalError as e:
            if conn:
                conn.close()
            if "database is locked" in str(e):
                print(f"⚠️ 访问量记录：数据库锁定，第 {attempt + 1} 次重试...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            print(f"❌ 访问量记录：数据库操作失败: {e}")
            return False
        except Exception as e:
            if conn:
                conn.close()
            print(f"❌ 记录访问量失败 (尝试 {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return False
    
    print(f"❌ 访问量记录最终失败，已重试 {max_retries} 次")
    return False

def sync_all_outputs_to_stats():
    """一键同步所有outputs目录中的书籍到统计系统"""
    import os
    import json
    
    try:
        outputs_dir = 'outputs'
        if not os.path.exists(outputs_dir):
            print("❌ outputs目录不存在")
            return False
        
        session_dirs = [d for d in os.listdir(outputs_dir) if os.path.isdir(os.path.join(outputs_dir, d))]
        synced_count = 0
        
        for session_id in session_dirs:
            data_path = os.path.join(outputs_dir, session_id, 'data.json')
            
            if os.path.exists(data_path):
                try:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 提取book_data
                    book_data = data.get('book_data', {})
                    if 'topic' in data:
                        book_data['topic'] = data['topic']
                    
                    # 同步到统计系统
                    if auto_sync_book_to_stats(session_id, book_data):
                        synced_count += 1
                        
                except Exception as e:
                    print(f"⚠️ 处理 {session_id} 失败: {e}")
                    continue
        
        print(f"\n✅ 批量同步完成，成功处理 {synced_count} 本书籍")
        return True
        
    except Exception as e:
        print(f"❌ 批量同步失败: {e}")
        return False

if __name__ == "__main__":
    # 测试功能
    print("🧪 测试自动同步钩子...")
    
    # 示例数据
    test_book_data = {
        'topic': '测试书籍',
        'author': '测试作者',
        'category_id': 'literature',
        'category_name': '文学类',
        'category_color': '#E74C3C',
        'category_icon': '📖'
    }
    
    test_session_id = 'test-session-12345'
    
    # 测试同步
    success = auto_sync_book_to_stats(test_session_id, test_book_data)
    if success:
        print("✅ 自动同步测试成功")
        
        # 测试访问量记录
        success2 = record_book_view_enhanced(test_session_id)
        if success2:
            print("✅ 访问量记录测试成功")
    
    print("\n🔄 执行批量同步...")
    sync_all_outputs_to_stats()
