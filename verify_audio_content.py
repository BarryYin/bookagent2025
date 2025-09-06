#!/usr/bin/env python3
"""
验证音频内容是否匹配预期文本
"""

import os
import subprocess
import time

def play_audio_with_description(file_path, expected_text, slide_num):
    """播放音频并显示预期内容"""
    if not os.path.exists(file_path):
        print(f"❌ [{slide_num}] 文件不存在: {file_path}")
        return
    
    print(f"\n🎵 播放幻灯片 [{slide_num}]:")
    print(f"📄 预期内容: {expected_text[:50]}...")
    print(f"🔊 正在播放: {os.path.basename(file_path)}")
    print("=" * 60)
    
    # 使用 afplay 播放音频
    try:
        process = subprocess.Popen(['afplay', file_path], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        
        # 等待几秒让用户听到内容
        time.sleep(6)
        
        # 停止播放
        process.terminate()
        process.wait()
        
        # 询问用户验证
        user_input = input("✅ 音频内容是否与预期一致？(y/n/s=跳过): ").strip().lower()
        if user_input == 'y':
            print("✅ 验证通过")
            return True
        elif user_input == 's':
            print("⏭️ 跳过验证")
            return None
        else:
            print("❌ 内容不匹配")
            return False
            
    except Exception as e:
        print(f"❌ 播放失败: {e}")
        return False

def main():
    print("🔍 验证《倾听的艺术》音频内容")
    print("请仔细听取每个音频，确认内容是否正确")
    print()
    
    # 音频文件和预期内容
    test_cases = [
        ("ppt_audio/a00f042c-f472-4844-ad59-fda9b39970fc_slide_01.mp3", 
         "有一个残酷的事实：90%的人际问题，都源于不会听。你有没有这样的经历：说了却没人理解？听了却没听懂？"),
        
        ("ppt_audio/a00f042c-f472-4844-ad59-fda9b39970fc_slide_02.mp3",
         "传统观念认为，沟通的重点是说。但认知升级的关键在于明白：听见不等于理解，理解不等于共鸣"),
        
        ("ppt_audio/a00f042c-f472-4844-ad59-fda9b39970fc_slide_03.mp3",
         "倾听的艺术这本书告诉我们，高效倾听由三个层次构成：第一层，听见信息"),
        
        ("ppt_audio/a00f042c-f472-4844-ad59-fda9b39970fc_slide_04.mp3",
         "心理学和管理学的研究告诉我们：在团队中，高效倾听者的信任度提升82%"),
        
        ("ppt_audio/a00f042c-f472-4844-ad59-fda9b39970fc_slide_05.mp3",
         "从被动听到到主动倾听，你可以通过三步跃迁来完成：第一步，信息层训练"),
        
        ("ppt_audio/a00f042c-f472-4844-ad59-fda9b39970fc_slide_06.mp3",
         "你会发现，你能赢得他人真正的信任，你能快速洞察问题的本质")
    ]
    
    results = []
    for i, (file_path, expected_text) in enumerate(test_cases, 1):
        result = play_audio_with_description(file_path, expected_text, i)
        results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 验证结果总结:")
    
    correct_count = sum(1 for r in results if r is True)
    incorrect_count = sum(1 for r in results if r is False)
    skipped_count = sum(1 for r in results if r is None)
    
    print(f"✅ 正确: {correct_count}")
    print(f"❌ 错误: {incorrect_count}")
    print(f"⏭️ 跳过: {skipped_count}")
    
    if incorrect_count > 0:
        print("\n⚠️ 发现内容不匹配的音频文件，需要重新生成")
    elif correct_count == len(test_cases):
        print("\n🎉 所有音频内容验证通过！")

if __name__ == "__main__":
    main()
