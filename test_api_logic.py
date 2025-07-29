"""
测试API逻辑，找出为什么"时间管理"PPT没有被返回
"""
import json
import os
from pathlib import Path
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone('Asia/Shanghai')

def test_api_logic():
    """测试API逻辑"""
    outputs_dir = Path("outputs")
    target_session = "fa838c99-8ee6-4033-ab79-886ce19277d4"
    
    print(f"🔍 测试API逻辑 - 查找session: {target_session}")
    print("=" * 50)
    
    ppt_list = []
    
    # 遍历outputs目录下的所有子目录
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            data_file = session_dir / "data.json"
            html_file = session_dir / "presentation.html"
            
            print(f"\n📁 检查目录: {session_dir.name}")
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
                    
                    ppt_list.append(ppt_info)
                    
                    if session_dir.name == target_session:
                        print(f"✅ 找到目标PPT!")
                        print(f"  标题: {ppt_info['title']}")
                        print(f"  分类: {ppt_info['category_name']}")
                        print(f"  创建时间: {ppt_info['created_time']}")
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ 读取PPT数据失败: {session_dir.name}, 错误: {e}")
                    if session_dir.name == target_session:
                        print(f"❌ 目标PPT读取失败!")
                    continue
    
    # 按创建时间排序，最新的在前
    ppt_list.sort(key=lambda x: x["created_time"], reverse=True)
    
    print(f"\n📊 统计结果:")
    print(f"  总PPT数量: {len(ppt_list)}")
    
    # 查找目标PPT在排序后的位置
    target_index = None
    for i, ppt in enumerate(ppt_list):
        if ppt['session_id'] == target_session:
            target_index = i
            break
    
    if target_index is not None:
        print(f"  目标PPT在排序后的位置: {target_index + 1}")
        print(f"  目标PPT信息: {ppt_list[target_index]}")
    else:
        print(f"❌ 目标PPT没有在列表中!")
    
    # 显示前10个PPT
    print(f"\n📋 前10个PPT:")
    for i, ppt in enumerate(ppt_list[:10]):
        print(f"  {i+1}. {ppt['title']} ({ppt['category_name']}) - {ppt['created_time']}")

if __name__ == "__main__":
    test_api_logic() 