#!/usr/bin/env python3
"""测试完整的书籍分析、PPT生成和旁白生成的流程"""

import asyncio
import json
import re
from openai import AsyncOpenAI

# 配置
BAIDU_API_KEY = "bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9"
BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2"
BAIDU_MODEL = "ernie-4.5-turbo-32k"

# 模拟状态
USE_BAIDU = True
USE_QWEN = False

async def test_step_creation():
    """测试Step1到Step3的完整流程"""

    topic = "小狗钱钱"
    book_data = None
    slides = None
    narrations = None

    print(f"🚀 开始测试《{topic}》的完整生成流程...\n")

    # Step 1: 书籍分析
    print("📚 Step1: 书籍分析...")
    try:
        client = AsyncOpenAI(api_key=BAIDU_API_KEY, base_url=BAIDU_BASE_URL)

        # Step1系统提示
        system_prompt_1 = f"""你是一位专业的图书分析师。请对《{topic}》这本书进行基本数据提取和分析。

请提取以下信息：
1. 书名和作者
2. 主要内容概述（3-5句话）
3. 核心观点或理论（3-5个要点）
4. 目标读者群体
5. 书籍的价值和意义
6. 适合制作PPT的关键章节或主题（5-8个）

请以JSON格式返回结果，确保分析角度符合上述方法论要求。"""

        response_1 = await client.chat.completions.create(
            model=BAIDU_MODEL,
            messages=[{"role": "user", "content": system_prompt_1}],
            temperature=0.7
        )

        result_1 = response_1.choices[0].message.content
        print(f"Step1响应长度: {len(result_1)}字符")

        # 解析JSON（使用修复后的逻辑）
        try:
            import re
            # 尝试从代码块提取
            json_match = re.search(r'```json\s*\n(.*?)\n```', result_1, re.DOTALL)
            if json_match:
                book_data = json.loads(json_match.group(1))
            else:
                # 直接解析
                book_data = json.loads(result_1)
            print("✅ Step1完成 - 成功获取书籍数据")
            print(f"   书名: {book_data.get('书名和作者', {}).get('书名', 'N/A')}")
            print(f"   作者: {book_data.get('书名和作者', {}).get('作者', 'N/A')}")
        except Exception as e:
            print(f"❌ Step1 JSON解析失败: {e}")
            return

    except Exception as e:
        print(f"❌ Step1 失败: {type(e).__name__} - {str(e)}")
        return

    # Step 2: PPT结构生成
    print("\n🎨 Step2: PPT画面结构生成...")
    try:
        # 模拟PPT结构生成提示（简化版）
        system_prompt_2 = f"""基于书籍数据创建PPT结构：《{topic}》

书籍数据：
{json.dumps(book_data, ensure_ascii=False)[:500]}

请生成JSON格式的PPT结构，包含5-6页内容。"""

        response_2 = await client.chat.completions.create(
            model=BAIDU_MODEL,
            messages=[{"role": "user", "content": system_prompt_2}],
            temperature=0.8
        )

        result_2 = response_2.choices[0].message.content
        print(f"Step2响应长度: {len(result_2)}字符")

        # 解析PPT数据
        try:
            json_match = re.search(r'\[([\s\S]*?)\]', result_2)  # 简化匹配
            if json_match:
                slides_text = '[' + json_match.group(1) + ']'
                slides = json.loads(slides_text)
            print(f"✅ Step2完成 - 成功生成 {len(slides)} 个幻灯片结构")
        except Exception as e:
            print(f"⚠️  Step2 JSON解析失败: {e}")
            slides = [{"raw_content": result_2}]

    except Exception as e:
        print(f"❌ Step2 失败: {type(e).__name__} - {str(e)}")
        return

    # Step 3: 旁白生成
    print("\n🎤 Step3: 旁白词生成...")
    try:
        # Step3系统提示
        system_prompt_3 = f"""为《{topic}》的PPT生成旁白，每页1段解说词

PPT结构：
{json.dumps(slides[:2], ensure_ascii=False)}  # 只使用前2页简化测试

请以JSON数组返回，每页包含：
- slide_number: 页码
- opening: 开场白
- main_narration: 主要内容（100-200字）
- transition: 过渡语"""

        print(f"📡 正在调用 {BAIDU_MODEL} 模型...")
        response_3 = await client.chat.completions.create(
            model=BAIDU_MODEL,
            messages=[{"role": "user", "content": system_prompt_3}],
            temperature=0.8
        )

        result_3 = response_3.choices[0].message.content
        print(f"Step3响应长度: {len(result_3)}字符")
        print(f"响应预览: {result_3[:200]}...")

        # 解析旁白数据
        try:
            json_match = re.search(r'```json\s*\n(.*?)\n```', result_3, re.DOTALL)
            if json_match:
                narrations = json.loads(json_match.group(1))
            else:
                # 尝试直接解析
                narrations = json.loads(result_3)
            print(f"✅ Step3完成 - 成功生成 {len(narrations)} 段旁白词")
        except Exception as e:
            print(f"⚠️  Step3 JSON解析失败: {e}")
            narrations = [{"raw_content": result_3}]

    except Exception as e:
        print(f"❌ Step3 失败: {type(e).__name__} - {str(e)}")
        print(f"错误详情: {str(e)}")
        return

    # 结果总结
    print("\n🎉 测试完成!")
    print(f"✅ 成功生成 《{topic}」 的完整内容")
    book_data_ok = "✅" if book_data and 'raw_content' not in book_data else "❌"
    slides_ok = "✅" if slides and 'raw_content' not in slides[0] else "❌"
    print(f"   书籍数据: {book_data_ok}")
    print(f"   PPT结构: {slides_ok}")
    print(f"   旁白词数: {len(narrations)} 段")

if __name__ == "__main__":
    asyncio.run(test_step_creation())