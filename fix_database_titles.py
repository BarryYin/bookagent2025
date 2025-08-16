#!/usr/bin/env python3
"""
修复数据库中的书名问题
将长文本的title字段提取出正确的书名
"""

import sqlite3
import re
import json
import os

def extract_book_title_from_text(text):
    """从长文本中提取书名"""
    # 尝试匹配《书名》格式
    title_match = re.search(r'《([^》]+)》', text)
    if title_match:
        return title_match.group(1)
    
    # 尝试匹配"书名："格式
    title_match = re.search(r'书名[：:]\s*([^\n\-]+)', text)
    if title_match:
        title = title_match.group(1).strip()
        # 移除常见的后缀
        title = re.sub(r'\s*-\s*作者.*$', '', title)
        title = re.sub(r'\s*-\s*分类.*$', '', title)
        return title.strip()
    
    return None

def fix_database_titles():
    """修复数据库中的书名问题"""
    DATABASE_PATH = "users.db"
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 查找所有可能有问题的记录（title长度超过100字符的）
    cursor.execute("SELECT id, session_id, title, author FROM ppts WHERE length(title) > 100")
    problem_records = cursor.fetchall()
    
    print(f"发现 {len(problem_records)} 条可能有问题的记录")
    
    fixed_count = 0
    for record_id, session_id, long_title, author in problem_records:
        print(f"\n处理记录 {session_id}")
        print(f"原标题: {long_title[:100]}...")
        
        # 尝试从长文本中提取书名
        extracted_title = extract_book_title_from_text(long_title)
        
        if extracted_title:
            print(f"提取的书名: {extracted_title}")
            
            # 尝试从对应的data.json文件中获取更多信息
            data_file = f"outputs/{session_id}/data.json"
            if os.path.exists(data_file):
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    book_data = data.get('book_data', {})
                    
                    # 检查是否有更好的标题
                    if 'title' in book_data:
                        extracted_title = book_data['title']
                        print(f"从data.json获取的书名: {extracted_title}")
                    elif 'book_title' in book_data:
                        extracted_title = book_data['book_title']
                        print(f"从data.json获取的书名: {extracted_title}")
                    
                    # 也更新作者信息
                    if author == "未知作者" and 'author' in book_data:
                        new_author = book_data['author']
                        print(f"更新作者: {new_author}")
                        cursor.execute("UPDATE ppts SET title = ?, author = ? WHERE id = ?", 
                                     (extracted_title, new_author, record_id))
                    else:
                        cursor.execute("UPDATE ppts SET title = ? WHERE id = ?", 
                                     (extracted_title, record_id))
                        
                except Exception as e:
                    print(f"读取data.json失败: {e}")
                    # 只更新标题
                    cursor.execute("UPDATE ppts SET title = ? WHERE id = ?", 
                                 (extracted_title, record_id))
            else:
                # 只更新标题
                cursor.execute("UPDATE ppts SET title = ? WHERE id = ?", 
                             (extracted_title, record_id))
            
            fixed_count += 1
            print(f"✅ 已修复")
        else:
            print(f"❌ 无法提取书名")
    
    conn.commit()
    conn.close()
    
    print(f"\n修复完成！共修复了 {fixed_count} 条记录")

if __name__ == "__main__":
    fix_database_titles()
