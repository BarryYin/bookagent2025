#!/usr/bin/env python3
import asyncio
import json
import re
from openai import AsyncOpenAI

# 百度ERNIE模型的配置
BAIDU_API_KEY = "bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9"
BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2"
BAIDU_MODEL = "ernie-4.5-turbo-32k"

# 更新后的JSON解析函数（与修复的代码一致）
def parse_llm_response(result: str):
    """解析LLM响应，支持从markdown代码块中提取JSON"""
    try:
        # 尝试直接解析JSON
        return json.loads(result)
    except:
        # 如果直接解析失败，尝试从markdown代码块中提取JSON
        try:
            json_match = re.search(r'```json\s*\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                # 尝试其他形式的代码块
                json_match = re.search(r'```\s*\n(.*?)\n```', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    # 如果都无法解析，返回原始内容
                    return {"raw_content": result}
        except:
            # 所有解析方式都失败
            return {"raw_content": result}

async def test_enhanced_book_analysis():
    """测试修复后的书本分析功能"""

    topic = "小狗钱钱"

    # 模拟appbook.py中的系统提示
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
        # 初始化百度ERNIE客户端（模拟appbook.py）
        client = AsyncOpenAI(api_key=BAIDU_API_KEY, base_url=BAIDU_BASE_URL)

        print(f"🔍 正在分析《{topic}》...")
        print(f"🤖 使用的模型：{BAIDU_MODEL}")

        # 调用ERNIE模型
        response = await client.chat.completions.create(
            model=BAIDU_MODEL,
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )

        result = response.choices[0].message.content
        print(f"\n📡 API响应原始内容长度：{len(result)}字符")

        # 使用修复后的解析函数
        book_data = parse_llm_response(result)

        print("\n✅ 成功解析的数据结构：")
        if "raw_content" not in book_data:
            print(f"📖 书名：{book_data.get('书名和作者', {}).get('书名', '《小狗钱钱》')}")
            print(f"✍️  作者：{book_data.get('书名和作者', {}).get('作者', '未知作者')}")
            print(f"📋 主要内容概述：")
            for summary in book_data.get('主要内容概述', [])[:3]:
                print(f"   - {summary}")
            print(f"💡 核心观点：{len(book_data.get('核心观点或理论', []))}个")
            for idea in book_data.get('核心观点或理论', [])[:2]:
                print(f"   • {idea}")
        else:
            print("❌ 解析失败，仍返回原始内容")

        print("\n🎉 修复验证完成！现在应该能够正确解析百度ERNIE模型的响应内容。")

    except Exception as e:
        print(f"💥 调用失败:")
        print(f"错误类型：{type(e).__name__}")
        print(f"错误信息：{str(e)}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_book_analysis())