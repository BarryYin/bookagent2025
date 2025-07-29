"""
测试简化的LLM分类
"""
import asyncio
import json
from openai import AsyncOpenAI

# 配置Qwen模型
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

async def test_simple_category():
    """测试简化的LLM分类"""
    print("🧠 测试简化的LLM分类")
    print("=" * 50)
    
    test_books = ["活着", "时间管理大师", "三体", "乔布斯传", "高等数学"]
    
    for book_title in test_books:
        print(f"\n📖 测试书籍: 《{book_title}》")
        print("-" * 30)
        
        try:
            # 简单的分类prompt
            category_prompt = f"""请将《{book_title}》这本书分类到以下5个分类之一，只输出分类名称：

文学类、效率提升类、虚构类、自传类、教材类

只输出分类名称，不要其他内容。"""
            
            response = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": category_prompt}],
                temperature=0.3
            )
            
            category = response.choices[0].message.content.strip()
            print(f"🏷️ 分类结果: {category}")
            
        except Exception as e:
            print(f"❌ 分类失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_category()) 