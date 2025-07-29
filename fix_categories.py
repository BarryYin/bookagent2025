"""
手动修复一些书籍的分类
"""
import json
import os
from pathlib import Path

# 手动分类映射
manual_categories = {
    "小王子": {"id": "fiction", "name": "虚构类", "color": "#9B59B6", "icon": "🔮"},
    "解忧杂货店": {"id": "fiction", "name": "虚构类", "color": "#9B59B6", "icon": "🔮"},
    "白夜行": {"id": "fiction", "name": "虚构类", "color": "#9B59B6", "icon": "🔮"},
    "追风筝的人": {"id": "fiction", "name": "虚构类", "color": "#9B59B6", "icon": "🔮"},
    "月亮与六便士": {"id": "fiction", "name": "虚构类", "color": "#9B59B6", "icon": "🔮"},
    "乔布斯传": {"id": "biography", "name": "自传类", "color": "#F39C12", "icon": "👤"},
    "时间管理": {"id": "efficiency", "name": "效率提升类", "color": "#27AE60", "icon": "⚡"},
    "时间管理大师": {"id": "efficiency", "name": "效率提升类", "color": "#27AE60", "icon": "⚡"},
    "高等数学": {"id": "textbook", "name": "教材类", "color": "#34495E", "icon": "📚"},
    "人间词话": {"id": "literature", "name": "文学类", "color": "#E74C3C", "icon": "📖"},
    "沉默的大多数": {"id": "literature", "name": "文学类", "color": "#E74C3C", "icon": "📖"},
    "我与地坛": {"id": "literature", "name": "文学类", "color": "#E74C3C", "icon": "📖"},
    "人间值得": {"id": "literature", "name": "文学类", "color": "#E74C3C", "icon": "📖"}
}

def fix_categories():
    """修复分类"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ outputs目录不存在")
        return
    
    print("🔧 开始手动修复分类")
    print("=" * 40)
    
    count = 0
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            data_file = session_dir / "data.json"
            if data_file.exists():
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    book_title = data.get("topic", "未知主题")
                    book_data = data.get("book_data", {})
                    
                    # 检查是否需要修复
                    if book_title in manual_categories:
                        category_info = manual_categories[book_title]
                        
                        # 更新book_data
                        book_data['category_id'] = category_info['id']
                        book_data['category_name'] = category_info['name']
                        book_data['category_color'] = category_info['color']
                        book_data['category_icon'] = category_info['icon']
                        
                        # 保存更新后的数据
                        data['book_data'] = book_data
                        with open(data_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        print(f"✅ 《{book_title}》修复为: {category_info['name']}")
                        count += 1
                    
                except Exception as e:
                    print(f"❌ 处理《{book_title}》失败: {e}")
    
    print(f"\n🎉 分类修复完成！共修复了 {count} 个PPT")

if __name__ == "__main__":
    fix_categories() 