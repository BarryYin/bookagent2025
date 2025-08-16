import asyncio
import json
from appbook import generate_reliable_ppt_html_internal, get_default_book_cover

# 测试数据
test_slides = [
    {
        "title": "测试书籍",
        "subtitle": "一本测试用的书籍",
        "content": "这是测试书籍的内容介绍。"
    },
    {
        "title": "第二页",
        "subtitle": "更多内容",
        "content": "这是第二页的内容。"
    }
]

test_narrations = [
    "这是第一页的解说词内容，用于测试默认封面的显示效果。",
    "这是第二页的解说词内容。"
]

test_book_data = {
    "title": "测试书籍",
    "author": "测试作者",
    "cover_url": ""  # 空的封面URL，会触发默认封面
}

async def test_default_cover():
    """测试默认封面生成"""
    print("生成测试PPT...")
    
    # 生成HTML
    html_content = await generate_reliable_ppt_html_internal(
        test_slides, 
        test_narrations, 
        test_book_data
    )
    
    # 保存到文件
    with open("test_default_cover.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("测试PPT已生成: test_default_cover.html")
    
    # 测试默认封面生成函数
    default_cover = get_default_book_cover("测试书籍")
    print(f"默认封面CSS: {default_cover}")

if __name__ == "__main__":
    asyncio.run(test_default_cover())