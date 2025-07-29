"""
重新分类现有的PPT
"""
import os
import json
import asyncio
from pathlib import Path
from openai import AsyncOpenAI

# 配置
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
client = AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-1234567890abcdef"
)

# 分类映射
category_mapping = {
    '文学类': {'id': 'literature', 'name': '文学类', 'color': '#E74C3C', 'icon': '📖'},
    '效率提升类': {'id': 'efficiency', 'name': '效率提升类', 'color': '#27AE60', 'icon': '⚡'},
    '虚构类': {'id': 'fiction', 'name': '虚构类', 'color': '#9B59B6', 'icon': '🔮'},
    '自传类': {'id': 'biography', 'name': '自传类', 'color': '#F39C12', 'icon': '👤'},
    '教材类': {'id': 'textbook', 'name': '教材类', 'color': '#34495E', 'icon': '📚'}
}

async def classify_book(book_title: str) -> dict:
    """分类单本书"""
    category_prompt = f"""请将《{book_title}》这本书分类到以下5个分类之一，只输出分类名称：

文学类、效率提升类、虚构类、自传类、教材类

只输出分类名称，不要其他内容。"""
    
    try:
        response = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": category_prompt}],
            temperature=0.3
        )
        category = response.choices[0].message.content.strip()
        return category_mapping.get(category, category_mapping['文学类'])
    except Exception as e:
        print(f"分类《{book_title}》失败: {e}")
        return category_mapping['文学类']

async def reclassify_existing_ppts():
    """重新分类现有的PPT"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ outputs目录不存在")
        return
    
    print("🧪 开始重新分类现有PPT")
    print("=" * 50)
    
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
                    
                    # 检查是否已经有分类信息
                    if book_data.get("category_id") and book_data.get("category_name"):
                        print(f"✅ 《{book_title}》已有分类: {book_data.get('category_name')}")
                        continue
                    
                    print(f"📖 正在分类: 《{book_title}》")
                    category_info = await classify_book(book_title)
                    
                    # 更新book_data
                    book_data['category_id'] = category_info['id']
                    book_data['category_name'] = category_info['name']
                    book_data['category_color'] = category_info['color']
                    book_data['category_icon'] = category_info['icon']
                    
                    # 保存更新后的数据
                    data['book_data'] = book_data
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ 《{book_title}》分类为: {category_info['name']}")
                    count += 1
                    
                    # 避免请求过快
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"❌ 处理《{book_title}》失败: {e}")
    
    print(f"\n🎉 重新分类完成！共处理了 {count} 个PPT")

if __name__ == "__main__":
    print("⚠️ 请确保服务器已启动 (python appbook.py)")
    print("然后运行此脚本重新分类现有PPT...")
    
    # 询问是否继续
    response = input("是否继续重新分类? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(reclassify_existing_ppts())
    else:
        print("重新分类已取消") 