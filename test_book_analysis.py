#!/usr/bin/env python3
import asyncio
import json
from openai import AsyncOpenAI

# 使用百度ERNIE模型的配置
BAIDU_API_KEY = "bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9"
BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2"
BAIDU_MODEL = "ernie-4.5-turbo-32k"

async def test_book_analysis():
    """测试《小狗钱钱》的书籍分析功能"""

    topic = "小狗钱钱"

    # 模拟书中的系统提示
    system_prompt = f"""你是一位专业的图书分析师。请对《{topic}》这本书进行基本数据提取和分析。

请提取以下信息：
1. 书名和作者
2. 主要内容概述（3-5句话）
3. 核心观点或理论（3-5个要点）
4. 目标读者群体
5. 书籍的价值和意义
6. 适合制作PPT的关键章节或主题（5-8个）

请以JSON格式返回结果，确保分析内容具体、准确。"""

    try:
        # 初始化百度ERNIE客户端
        client = AsyncOpenAI(api_key=BAIDU_API_KEY, base_url=BAIDU_BASE_URL)

        print(f"正在分析《{topic}》...")
        print(f"使用的模型：{BAIDU_MODEL}")

        # 调用ERNIE模型
        response = await client.chat.completions.create(
            model=BAIDU_MODEL,
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )

        result = response.choices[0].message.content
        print(f"\nAPI响应内容：\n{result}\n")

        # 尝试解析JSON
        try:
            book_data = json.loads(result)
            print("成功解析JSON数据：")
            print(f"书名：{book_data.get('book_title', '未提及')}")
            print(f"作者：{book_data.get('author', '未提及')}")
            print(f"总结：{book_data.get('summary', [])}")
            print(f"核心观点：{book_data.get('core_ideas', [])}")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print("将结果作为原始内容处理")

    except Exception as e:
        print(f"调用失败:")
        print(f"错误类型：{type(e).__name__}")
        print(f"错误信息：{str(e)}")

if __name__ == "__main__":
    asyncio.run(test_book_analysis())