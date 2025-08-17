#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def query_book_access_stats():
    """查询书籍访问统计"""
    
    db_path = 'fogsight.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print('=== 从 ppts 表查询书籍访问统计 ===')
        
        # 查询书籍访问统计
        cursor.execute('''
            SELECT 
                title,
                author,
                COUNT(*) as ppt_count,
                SUM(view_count) as total_views,
                MAX(view_count) as max_views,
                AVG(view_count) as avg_views
            FROM ppts 
            GROUP BY title, author 
            ORDER BY total_views DESC
        ''')
        
        results = cursor.fetchall()
        
        if not results:
            print("没有找到任何书籍数据")
            return
        
        print(f'\n共有 {len(results)} 本书籍的PPT')
        print(f"{'书名':<30} {'作者':<20} {'PPT数量':<8} {'总访问量':<10} {'最大访问量':<10} {'平均访问量':<10}")
        print('-' * 100)
        
        total_books = len(results)
        total_ppts = 0
        total_all_views = 0
        
        for i, (title, author, ppt_count, total_views, max_views, avg_views) in enumerate(results, 1):
            title_display = title[:28] + '...' if len(title) > 30 else title
            author_display = (author or 'Unknown')[:18] + '...' if author and len(author) > 20 else (author or 'Unknown')
            
            total_views = total_views or 0
            max_views = max_views or 0
            avg_views = avg_views or 0
            
            print(f'{title_display:<30} {author_display:<20} {ppt_count:<8} {total_views:<10} {max_views:<10} {avg_views:<10.1f}')
            
            total_ppts += ppt_count
            total_all_views += total_views
        
        print('-' * 100)
        print(f'汇总统计:')
        print(f'  总书籍数: {total_books} 本')
        print(f'  总PPT数: {total_ppts} 个')
        print(f'  总访问量: {total_all_views} 次')
        print(f'  平均每本书访问量: {total_all_views/total_books:.1f} 次')
        print(f'  平均每个PPT访问量: {total_all_views/total_ppts:.1f} 次' if total_ppts > 0 else '  平均每个PPT访问量: 0 次')
        
        # 查看访问量分布
        print(f'\n=== 访问量分布 ===')
        zero_views = len([r for r in results if (r[3] or 0) == 0])
        low_views = len([r for r in results if 0 < (r[3] or 0) <= 10])
        medium_views = len([r for r in results if 10 < (r[3] or 0) <= 50])
        high_views = len([r for r in results if (r[3] or 0) > 50])
        
        print(f'  无访问 (0次): {zero_views} 本')
        print(f'  低访问 (1-10次): {low_views} 本')
        print(f'  中访问 (11-50次): {medium_views} 本')
        print(f'  高访问 (>50次): {high_views} 本')
        
        # 显示最受欢迎的前10本书
        if results:
            print(f'\n=== 最受欢迎的前10本书 ===')
            top_books = sorted(results, key=lambda x: x[3] or 0, reverse=True)[:10]
            for i, (title, author, ppt_count, total_views, max_views, avg_views) in enumerate(top_books, 1):
                print(f'{i:2d}. 《{title}》 - {author or "Unknown"} (访问 {total_views or 0} 次)')
        
        # 查看 book_statistics 表
        print(f'\n=== book_statistics 表数据 ===')
        cursor.execute('SELECT COUNT(*) FROM book_statistics')
        stats_count = cursor.fetchone()[0]
        
        if stats_count > 0:
            cursor.execute('SELECT book_title, author, total_views, ppt_count, last_viewed FROM book_statistics ORDER BY total_views DESC LIMIT 10')
            stats_results = cursor.fetchall()
            
            print(f"{'书名':<30} {'作者':<20} {'总访问量':<10} {'PPT数量':<8} {'最后访问':<20}")
            print('-' * 100)
            
            for book_title, author, total_views, ppt_count, last_viewed in stats_results:
                title_display = book_title[:28] + '...' if len(book_title) > 30 else book_title
                author_display = (author or 'Unknown')[:18] + '...' if author and len(author) > 20 else (author or 'Unknown')
                last_viewed_display = last_viewed[:19] if last_viewed else 'Never'
                print(f'{title_display:<30} {author_display:<20} {total_views:<10} {ppt_count:<8} {last_viewed_display:<20}')
        else:
            print('book_statistics 表中没有数据')
        
    except sqlite3.Error as e:
        print(f"数据库查询错误: {e}")
    except Exception as e:
        print(f"程序执行错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    query_book_access_stats()
