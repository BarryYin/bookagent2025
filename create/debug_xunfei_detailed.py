#!/usr/bin/env python3
"""
详细调试讯飞语音合成API
"""

import sys
import os
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ppt_voice_generator import XunfeiTTS

def debug_xunfei_api():
    """详细调试讯飞API"""
    print("🔍 详细调试讯飞语音合成API")
    print("=" * 50)
    
    # 显示配置信息
    tts = XunfeiTTS()
    print(f"🔧 配置信息:")
    print(f"  Host: {tts.host}")
    print(f"  App ID: {tts.app_id}")
    print(f"  API Key: {tts.api_key[:8]}***" if tts.api_key else "  API Key: None")
    print(f"  API Secret: {tts.api_secret[:8]}***" if tts.api_secret else "  API Secret: None")
    
    # 测试文本
    test_text = "这是测试"
    print(f"\n📝 测试文本: {test_text}")
    
    # 创建任务
    print("\n🚀 创建语音合成任务...")
    try:
        result = tts.create_task(test_text)
        if result:
            print(f"📋 创建任务响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 检查错误码
            header = result.get('header', {})
            code = header.get('code')
            message = header.get('message', '')
            
            if code == 0:
                print("✅ 任务创建成功")
                task_id = header.get('task_id')
                if task_id:
                    print(f"🆔 任务ID: {task_id}")
                    
                    # 查询任务状态
                    print("\n🔍 查询任务状态...")
                    query_result = tts.query_task(task_id)
                    if query_result:
                        print(f"📋 查询任务响应:")
                        print(json.dumps(query_result, ensure_ascii=False, indent=2))
                else:
                    print("❌ 未获取到任务ID")
            else:
                print(f"❌ 任务创建失败")
                print(f"   错误码: {code}")
                print(f"   错误信息: {message}")
                
                # 解析常见错误码
                error_codes = {
                    10013: "应用的总调用次数超限",
                    10014: "应用的QPS超限",
                    10019: "转写结果查询错误",
                    11200: "授权错误：该appid没有相关功能的授权 或者 业务配额不足",
                    11201: "日调用量超限：超过日调用量限制",
                    11202: "授权错误：ip白名单校验不通过",
                    11203: "授权错误：无效的apikey",
                }
                
                if code in error_codes:
                    print(f"   错误说明: {error_codes[code]}")
        else:
            print("❌ 创建任务返回空结果")
            
    except Exception as e:
        print(f"❌ 创建任务异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_xunfei_api()
