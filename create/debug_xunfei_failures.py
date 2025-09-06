#!/usr/bin/env python3
"""
调试讯飞TTS失败的具体原因
"""

import sys
import time
sys.path.append('/Users/mac/Documents/GitHub/bookagent/create')

from reliable_voice_generator import WebSocketXunfeiTTS

def debug_xunfei_failures():
    print("=== 调试讯飞TTS失败原因 ===")
    
    # 测试不同长度的文本
    test_texts = [
        "短文本测试",
        "《未来之地》这本书指出，决定一个人未来高度的，不是信息多少，而是认知升级的速度。",
        "认知升级不能停留在理论，必须转化为行动。这里有三个你现在就能开始的实用方法：第一，建立知识管理系统；第二，培养系统性思维习惯；第三，定期进行认知反思。",
        "《未来之地》告诉我们，真正的未来不是等来的，而是构建出来的。当你开始运用这些思维模型，你会发现自己不再被信息洪流裹挟，而是成为信息的主人，认知的领航者。"
    ]
    
    xunfei = WebSocketXunfeiTTS()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i} (长度: {len(text)}字符):")
        print(f"内容: {text[:50]}...")
        
        # 测试多次
        success_count = 0
        for attempt in range(3):
            try:
                output_file = f"/tmp/debug_test_{i}_{attempt}.mp3"
                success = xunfei.synthesize_to_file(text, output_file, timeout=15)
                if success:
                    success_count += 1
                    print(f"  尝试 {attempt+1}: ✅ 成功")
                else:
                    print(f"  尝试 {attempt+1}: ❌ 失败 - {xunfei.error_message}")
                time.sleep(1)  # 避免频率限制
            except Exception as e:
                print(f"  尝试 {attempt+1}: ❌ 异常 - {e}")
        
        print(f"成功率: {success_count}/3 ({success_count/3*100:.0f}%)")

if __name__ == "__main__":
    debug_xunfei_failures()
