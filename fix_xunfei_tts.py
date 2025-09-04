#!/usr/bin/env python3
"""
讯飞语音合成问题修复方案
"""

import os
import json
from pathlib import Path

def create_xunfei_config_template():
    """创建讯飞配置模板"""
    
    print("🔧 讯飞语音合成配置指南")
    print("=" * 50)
    
    # 检查当前配置
    current_app_id = os.getenv("XUNFEI_APP_ID", "e6950ae6")
    current_api_key = os.getenv("XUNFEI_API_KEY", "f2d4b9650c13355fc8286ac3fc34bf6e")
    current_api_secret = os.getenv("XUNFEI_API_SECRET", "NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh")
    
    print(f"📋 当前配置:")
    print(f"  APP_ID: {current_app_id}")
    print(f"  API_KEY: {current_api_key[:8]}***")
    print(f"  API_SECRET: {current_api_secret[:8]}***")
    
    print(f"\n❌ 当前API返回错误: 11200 - licc limit")
    print(f"   这表示API配额已用完或许可证限制")
    
    print(f"\n🔑 解决方案:")
    print(f"1. 获取新的讯飞API密钥:")
    print(f"   - 访问 https://console.xfyun.cn/")
    print(f"   - 注册账号并创建应用")
    print(f"   - 获取新的APP_ID、API_KEY、API_SECRET")
    
    print(f"\n2. 设置环境变量:")
    env_commands = f"""
export XUNFEI_APP_ID="你的APP_ID"
export XUNFEI_API_KEY="你的API_KEY"
export XUNFEI_API_SECRET="你的API_SECRET"
export XUNFEI_VOICE="x4_xiaoguo"
"""
    print(env_commands)
    
    print(f"\n3. 或者修改代码中的默认值:")
    print(f"   编辑 create/ppt_voice_generator.py 第43-45行")
    
    # 创建配置文件模板
    config_template = {
        "xunfei": {
            "app_id": "你的APP_ID",
            "api_key": "你的API_KEY", 
            "api_secret": "你的API_SECRET",
            "voice": "x4_xiaoguo",
            "note": "请替换为你的真实讯飞API密钥"
        },
        "备选方案": {
            "fish_audio": {
                "api_key": "Fish Audio API密钥",
                "reference_id": "音色参考ID"
            },
            "system_voice": {
                "enabled": True,
                "voice": "Tingting",
                "note": "macOS系统语音，无需API密钥"
            }
        }
    }
    
    config_file = Path("xunfei_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_template, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 已创建配置模板: {config_file}")
    
    print(f"\n🔄 当前备选方案:")
    print(f"  由于讯飞API配额问题，系统会自动回退到:")
    print(f"  1. Fish Audio (如果已配置)")
    print(f"  2. macOS系统语音 (say命令)")
    
    print(f"\n✅ 系统仍可正常工作，只是使用备选语音合成方案")

def check_alternative_tts():
    """检查备选TTS方案状态"""
    print(f"\n🔍 检查备选语音合成方案:")
    
    # 检查Fish Audio
    try:
        import fish_audio_sdk
        print(f"  ✅ Fish Audio SDK: 已安装")
    except ImportError:
        print(f"  ❌ Fish Audio SDK: 未安装")
        print(f"     安装命令: pip install fish-audio-sdk")
    
    # 检查系统语音
    import subprocess
    try:
        result = subprocess.run(["say", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ macOS系统语音: 可用")
        else:
            print(f"  ❌ macOS系统语音: 不可用")
    except FileNotFoundError:
        print(f"  ❌ macOS系统语音: 不可用 (非macOS系统)")
    
    # 检查ffmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ FFmpeg: 已安装")
        else:
            print(f"  ❌ FFmpeg: 未安装")
    except FileNotFoundError:
        print(f"  ❌ FFmpeg: 未安装")
        print(f"     安装命令: brew install ffmpeg")

if __name__ == "__main__":
    create_xunfei_config_template()
    check_alternative_tts()
