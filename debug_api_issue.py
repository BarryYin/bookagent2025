"""
调试API问题，找出哪些PPT被跳过了
"""
import json
import os
from pathlib import Path
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone('Asia/Shanghai')

def debug_api_issue():
    """调试API问题"""
    outputs_dir = Path("outputs")
    
    print("🔍 调试API问题")
    print("=" * 50)
    
    # 1. 获取所有PPT目录
    all_sessions = []
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            all_sessions.append(session_dir.name)
    
    print(f"📁 总共有 {len(all_sessions)} 个PPT目录")
    
    # 2. 检查每个PPT是否被API正确处理
    api_processed = []
    api_skipped = []
    
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            data_file = session_dir / "data.json"
            html_file = session_dir / "presentation.html"
            
            if data_file.exists() and html_file.exists():
                try:
                    # 读取数据文件获取PPT信息
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 获取文件创建时间
                    created_time = datetime.fromtimestamp(
                        data_file.stat().st_ctime, 
                        tz=shanghai_tz
                    ).strftime("%Y-%m-%d %H:%M")
                    
                    # 获取封面信息
                    book_data = data.get("book_data", {})
                    cover_url = book_data.get("cover_url", "default_cover")
                    
                    # 获取分类信息
                    category_id = book_data.get("category_id", "literature")
                    category_name = book_data.get("category_name", "文学类")
                    category_color = book_data.get("category_color", "#E74C3C")
                    category_icon = book_data.get("category_icon", "📖")
                    
                    ppt_info = {
                        "session_id": session_dir.name,
                        "title": data.get("topic", "未知主题"),
                        "created_time": created_time,
                        "html_url": f"/outputs/{session_dir.name}/presentation.html",
                        "preview_url": f"/ppt-preview/{session_dir.name}",
                        "cover_url": cover_url,
                        "category_id": category_id,
                        "category_name": category_name,
                        "category_color": category_color,
                        "category_icon": category_icon
                    }
                    
                    api_processed.append(ppt_info)
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ 读取PPT数据失败: {session_dir.name}, 错误: {e}")
                    api_skipped.append(session_dir.name)
                    continue
            else:
                print(f"❌ 文件缺失: {session_dir.name}")
                api_skipped.append(session_dir.name)
    
    # 3. 按创建时间排序
    api_processed.sort(key=lambda x: x["created_time"], reverse=True)
    
    print(f"\n📊 统计结果:")
    print(f"  API处理的PPT数量: {len(api_processed)}")
    print(f"  API跳过的PPT数量: {len(api_skipped)}")
    
    if api_skipped:
        print(f"\n❌ 被跳过的PPT:")
        for session_id in api_skipped:
            print(f"  - {session_id}")
    
    # 4. 检查分类分布
    categories = {}
    for ppt in api_processed:
        category = ppt.get('category_name', '未知')
        if category not in categories:
            categories[category] = []
        categories[category].append(ppt['title'])
    
    print(f"\n📚 分类分布:")
    for category, titles in categories.items():
        print(f"  {category}: {len(titles)} 个")
        for title in titles[:3]:  # 显示前3个
            print(f"    - {title}")
    
    # 5. 检查是否有其他分类
    other_categories = [cat for cat in categories.keys() if cat != '文学类']
    if other_categories:
        print(f"\n✅ 发现其他分类: {', '.join(other_categories)}")
        
        # 显示其他分类的PPT
        for category in other_categories:
            print(f"\n📖 {category} PPT:")
            for ppt in api_processed:
                if ppt['category_name'] == category:
                    print(f"  - 《{ppt['title']}》 ({ppt['created_time']})")
    else:
        print(f"\n⚠️ 只有文学类，需要更多样化的内容")

if __name__ == "__main__":
    debug_api_issue() 