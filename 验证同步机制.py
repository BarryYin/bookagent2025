#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def verify_sync_status():
    """验证同步机制状态"""
    
    print("🔍 验证书籍统计同步机制状态")
    print("=" * 50)
    
    conn = sqlite3.connect('fogsight.db')
    cursor = conn.cursor()
    
    # 1. 检查总体统计
    cursor.execute('SELECT COUNT(*) FROM ppts')
    ppt_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM (SELECT DISTINCT title, author FROM ppts WHERE title != "未知书籍")')
    unique_books = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM book_statistics')
    stats_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(view_count) FROM ppts')
    total_views = cursor.fetchone()[0] or 0
    
    print(f"📊 整体统计:")
    print(f"   PPT记录总数: {ppt_count}")
    print(f"   独立书籍数: {unique_books}")
    print(f"   统计表记录: {stats_count}")
    print(f"   总访问量: {total_views}")
    
    # 2. 检查数据一致性
    print(f"\n🔄 数据一致性检查:")
    
    # 检查ppts表中有记录但book_statistics表中没有的书籍
    cursor.execute('''
        SELECT DISTINCT p.title, p.author 
        FROM ppts p 
        LEFT JOIN book_statistics bs ON p.title = bs.book_title AND p.author = bs.author 
        WHERE bs.book_title IS NULL AND p.title != "未知书籍"
        LIMIT 5
    ''')
    missing_stats = cursor.fetchall()
    
    if missing_stats:
        print(f"   ⚠️ 发现 {len(missing_stats)} 本书在统计表中缺失:")
        for title, author in missing_stats:
            print(f"      - 《{title}》 - {author}")
    else:
        print(f"   ✅ 所有书籍都已同步到统计表")
    
    # 3. 检查最近生成的书籍
    print(f"\n📚 最近生成的书籍 (前10本):")
    cursor.execute('''
        SELECT title, author, view_count, created_at 
        FROM ppts 
        WHERE title != "未知书籍"
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    
    recent_books = cursor.fetchall()
    for i, (title, author, views, created) in enumerate(recent_books, 1):
        created_date = created[:10] if created else "Unknown"
        print(f"   {i:2d}. 《{title}》 - {author or 'Unknown'} (访问{views}次, {created_date})")
    
    # 4. 检查访问量最高的书籍
    print(f"\n🏆 访问量最高的书籍 (前5本):")
    cursor.execute('''
        SELECT title, author, SUM(view_count) as total_views
        FROM ppts 
        WHERE title != "未知书籍"
        GROUP BY title, author
        ORDER BY total_views DESC 
        LIMIT 5
    ''')
    
    top_books = cursor.fetchall()
    for i, (title, author, total_views) in enumerate(top_books, 1):
        print(f"   {i}. 《{title}》 - {author or 'Unknown'} ({total_views}次)")
    
    # 5. 检查首页提到的书籍
    print(f"\n🎯 检查首页重点书籍:")
    target_books = ['社会动物', '朱元璋传', '明朝那些事儿']
    
    for book_title in target_books:
        cursor.execute('''
            SELECT COUNT(*), SUM(view_count) 
            FROM ppts 
            WHERE title LIKE ?
        ''', (f'%{book_title}%',))
        
        result = cursor.fetchone()
        ppt_count = result[0] if result else 0
        views = result[1] if result and result[1] else 0
        
        cursor.execute('''
            SELECT total_views, ppt_count 
            FROM book_statistics 
            WHERE book_title LIKE ?
            LIMIT 1
        ''', (f'%{book_title}%',))
        
        stats_result = cursor.fetchone()
        
        if ppt_count > 0:
            print(f"   ✅ 《{book_title}》: {ppt_count}个PPT, {views}次访问", end="")
            if stats_result:
                print(f", 统计表记录: {stats_result[1]}个PPT, {stats_result[0]}次访问")
            else:
                print(f", ⚠️ 统计表中缺失")
        else:
            print(f"   ❌ 《{book_title}》: 未找到相关记录")
    
    conn.close()
    
    print(f"\n" + "=" * 50)
    print(f"✅ 同步机制验证完成")
    
    # 6. 状态总结
    sync_rate = (stats_count / unique_books * 100) if unique_books > 0 else 0
    print(f"\n📈 同步状态总结:")
    print(f"   同步率: {sync_rate:.1f}% ({stats_count}/{unique_books})")
    
    if sync_rate >= 95:
        print(f"   🎉 同步状态: 优秀")
    elif sync_rate >= 80:
        print(f"   👍 同步状态: 良好")
    else:
        print(f"   ⚠️ 同步状态: 需要改进")

if __name__ == "__main__":
    verify_sync_status()
