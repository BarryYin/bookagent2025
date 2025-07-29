"""
测试分类功能
"""
import asyncio
import json
from openai import AsyncOpenAI

# 配置
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
client = AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-1234567890abcdef"
)

async def test_category():
    """测试分类功能"""
    test_books = [
        "小王子",
        "解忧杂货店", 
        "时间管理",
        "乔布斯传",
        "高等数学"
    ]
    
    for book in test_books:
        print(f"\n📖 测试书籍: 《{book}》")
        
        category_prompt = f"""请将《{book}》这本书分类到以下5个分类之一，只输出分类名称：

文学类、效率提升类、虚构类、自传类、教材类

只输出分类名称，不要其他内容。"""
        
        try:
            response = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": category_prompt}],
                temperature=0.3
            )
            category = response.choices[0].message.content.strip()
            print(f"✅ 分类结果: {category}")
        except Exception as e:
            print(f"❌ 分类失败: {e}")

if __name__ == "__main__":
    print("🧪 测试分类功能")
    print("=" * 40)
    asyncio.run(test_category()) 