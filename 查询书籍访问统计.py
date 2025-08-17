#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def get_book_access_stats():
    """查询所有书籍的访问次数统计"""
    
    # 数据库文件路径
    db_path = 'fogsight.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有书籍及其访问次数，按访问次数降序排列
        query = """
        SELECT 
            id,
            title,
            author,
            view_count,
            CASE 
                WHEN view_count = 0 THEN '未访问'
                WHEN view_count <= 5 THEN '低频访问'
                WHEN view_count <= 20 THEN '中频访问'
                ELSE '高频访问'
            END as access_level
        FROM books 
        ORDER BY view_count DESC, title ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("数据库中没有找到书籍记录")
            return
        
        print(f"=== 书籍访问次数统计报告 ===")
        print(f"总计书籍数量: {len(results)} 本")
        print("-" * 80)
        
        # 统计各访问级别的书籍数量
        access_stats = {'未访问': 0, '低频访问': 0, '中频访问': 0, '高频访问': 0}
        total_views = 0
        
        print(f"{'序号':<4} {'书名':<30} {'作者':<20} {'访问次数':<8} {'访问级别':<10}")
        print("-" * 80)
        
        for i, (book_id, title, author, view_count, access_level) in enumerate(results, 1):
            # 截断过长的标题和作者名
            title_display = title[:28] + "..." if len(title) > 30 else title
            author_display = author[:18] + "..." if len(author) > 20 else author
            
            print(f"{i:<4} {title_display:<30} {author_display:<20} {view_count:<8} {access_level:<10}")
            
            access_stats[access_level] += 1
            total_views += view_count
        
        print("-" * 80)
        print(f"访问统计汇总:")
        print(f"  未访问书籍: {access_stats['未访问']} 本")
        print(f"  低频访问书籍 (1-5次): {access_stats['低频访问']} 本")
        print(f"  中频访问书籍 (6-20次): {access_stats['中频访问']} 本")
        print(f"  高频访问书籍 (>20次): {access_stats['高频访问']} 本")
        print(f"  总访问次数: {total_views} 次")
        print(f"  平均访问次数: {total_views/len(results):.2f} 次/本")
        
        # 找出访问次数最多和最少的书籍
        if results:
            most_viewed = results[0]
            least_viewed = [book for book in results if book[3] == min(result[3] for result in results)][0]
            
            print(f"\n最受欢迎书籍: 《{most_viewed[1]}》- {most_viewed[2]} (访问 {most_viewed[3]} 次)")
            print(f"最少访问书籍: 《{least_viewed[1]}》- {least_viewed[2]} (访问 {least_viewed[3]} 次)")
        
    except sqlite3.Error as e:
        print(f"数据库查询错误: {e}")
    except Exception as e:
        print(f"程序执行错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    get_book_access_stats()