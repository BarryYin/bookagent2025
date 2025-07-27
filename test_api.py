#!/usr/bin/env python3
"""
测试API调用
"""
import asyncio
import json
from google import genai
import os

# 设置API密钥
credentials = json.load(open("credentials.json"))
API_KEY = credentials["API_KEY"]
os.environ["GEMINI_API_KEY"] = API_KEY
gemini_client = genai.Client()

async def test_gemini_api():
    """测试Gemini API调用"""
    try:
        print("开始测试Gemini API...")
        
        system_prompt = """请对《测试书籍》这本书进行基本数据提取和分析。

请提取以下信息：
1. 书名和作者
2. 主要内容概述（3-5句话）

请以JSON格式返回结果。
"""
        
        print("发送请求...")
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp", 
                contents=system_prompt
            )
        )
        
        print("收到响应:")
        print(response.text)
        
        return True
        
    except Exception as e:
        print(f"API调用失败: {e}")
        print(f"错误类型: {type(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_api())
    print(f"测试结果: {'成功' if result else '失败'}")



#     curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
#   -H 'Content-Type: application/json' \
#   -H 'X-goog-api-key: AIzaSyA3TRlJCLkFVSk7deD-7F3-q3A1tHguHm0' \
#   -X POST \
#   -d '{
#     "contents": [
#       {
#         "parts": [
#           {
#             "text": "Explain how AI works in a few words"
#           }
#         ]
#       }
#     ]
#   }'