"""
完整模拟API逻辑，找出问题所在
"""
import json
import os
from pathlib import Path
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone('Asia/Shanghai')

def get_default_book_cover(book_title: str) -> str:
    """生成默认书籍封面"""
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "linear-gradient(135deg, #ff8a80 0%, #ea4c89 100%)",
        "linear-gradient(135deg, #8fd3f4 0%, #84fab0 100%)"
    ]
    gradient_index = hash(book_title) % len(gradients)
    gradient = gradients[gradient_index]
    return f"gradient:{gradient}"

def debug_api_complete():
    """完整模拟API逻辑"""
    outputs_dir = Path("outputs")
    
    print("🔍 完整模拟API逻辑")
    print("=" * 50)
    
    ppt_list = []
    skipped_sessions = []
    
    # 遍历outputs目录下的所有子目录
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            data_file = session_dir / "data.json"
            html_file = session_dir / "presentation.html"
            
            print(f"\n📁 处理: {session_dir.name}")
            print(f"  data.json存在: {data_file.exists()}")
            print(f"  presentation.html存在: {html_file.exists()}")
            
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
                    cover_url = book_data.get("cover_url", get_default_book_cover(data.get("topic", "未知主题")))
                    
                    # 转换本地封面路径为URL
                    if cover_url.startswith('covers/'):
                        cover_url = f"/covers/{cover_url.replace('covers/', '')}"
                    
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
                    
                    ppt_list.append(ppt_info)
                    print(f"  ✅ 成功处理: {ppt_info['title']} ({category_name})")
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"  ❌ 读取PPT数据失败: {session_dir.name}, 错误: {e}")
                    skipped_sessions.append(session_dir.name)
                    continue
                except Exception as e:
                    print(f"  ❌ 其他错误: {session_dir.name}, 错误: {e}")
                    skipped_sessions.append(session_dir.name)
                    continue
            else:
                print(f"  ❌ 文件缺失")
                skipped_sessions.append(session_dir.name)
    
    # 按创建时间排序，最新的在前
    ppt_list.sort(key=lambda x: x["created_time"], reverse=True)
    
    print(f"\n📊 最终统计:")
    print(f"  成功处理的PPT: {len(ppt_list)}")
    print(f"  跳过的PPT: {len(skipped_sessions)}")
    
    if skipped_sessions:
        print(f"\n❌ 被跳过的PPT:")
        for session_id in skipped_sessions:
            print(f"  - {session_id}")
    
    # 检查分类分布
    categories = {}
    for ppt in ppt_list:
        category = ppt.get('category_name', '未知')
        if category not in categories:
            categories[category] = []
        categories[category].append(ppt['title'])
    
    print(f"\n📚 分类分布:")
    for category, titles in categories.items():
        print(f"  {category}: {len(titles)} 个")
        for title in titles[:3]:  # 显示前3个
            print(f"    - {title}")
    
    # 检查是否有其他分类
    other_categories = [cat for cat in categories.keys() if cat != '文学类']
    if other_categories:
        print(f"\n✅ 发现其他分类: {', '.join(other_categories)}")
    else:
        print(f"\n⚠️ 只有文学类")
    
    return ppt_list, skipped_sessions

if __name__ == "__main__":
    debug_api_complete() 