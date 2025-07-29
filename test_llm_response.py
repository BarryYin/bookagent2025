"""
测试LLM原始响应
"""
import asyncio
import json
from openai import AsyncOpenAI

# 配置Qwen模型
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

async def test_llm_response():
    """测试LLM原始响应"""
    print("🧠 测试LLM原始响应")
    print("=" * 50)
    
    topic = "活着"
    
    system_prompt = f"""你是一位专业的图书分析师。请对《{topic}》这本书进行基本数据提取和分析。

请提取以下信息：
1. 书名和作者
2. 主要内容概述（3-5句话）
3. 核心观点或理论（3-5个要点）
4. 目标读者群体
5. 书籍的价值和意义
6. 适合制作PPT的关键章节或主题（5-8个）
7. 书籍分类：请将这本书归类到以下5个分类之一：
   - 文学类：小说、诗歌、散文等文学作品
   - 效率提升类：时间管理、学习方法、技能提升等实用书籍
   - 虚构类：科幻、奇幻、悬疑等虚构作品
   - 自传类：传记、自传、回忆录等
   - 教材类：教科书、参考书、学术著作等

请以JSON格式返回结果，包含category字段。
"""

    try:
        response = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )
        result = response.choices[0].message.content
        
        print("📝 LLM原始响应:")
        print("-" * 30)
        print(result)
        print("\n" + "="*50)
        
        # 尝试解析JSON
        try:
            book_data = json.loads(result)
            print("✅ JSON解析成功:")
            print(json.dumps(book_data, ensure_ascii=False, indent=2))
            
            # 检查分类信息
            category = book_data.get('category', '未找到')
            print(f"\n🏷️ 分类信息: {category}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print("原始响应不是有效的JSON格式")
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_response()) 