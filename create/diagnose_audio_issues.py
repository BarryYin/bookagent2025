#!/usr/bin/env python3
"""
诊断音频配对问题
"""

import os
import json
from pathlib import Path

def diagnose_audio_matching():
    print("=== 诊断音频配对问题 ===")
    
    # 检查音频目录
    audio_dir = Path("/Users/mac/Documents/GitHub/bookagent/ppt_audio")
    if not audio_dir.exists():
        print("❌ ppt_audio目录不存在")
        return
    
    print(f"📁 音频目录: {audio_dir}")
    
    # 列出所有音频文件
    audio_files = list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.aiff"))
    print(f"🎵 找到 {len(audio_files)} 个音频文件:")
    
    for audio_file in sorted(audio_files):
        size = audio_file.stat().st_size
        print(f"  📄 {audio_file.name}: {size:,} bytes")
    
    # 检查播放列表
    playlists = list(audio_dir.glob("*.m3u"))
    print(f"\n📝 找到 {len(playlists)} 个播放列表:")
    
    for playlist in playlists:
        print(f"  📄 {playlist.name}")
        try:
            with open(playlist, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                print(f"    行数: {len(lines)}")
                for line in lines[:5]:  # 显示前5行
                    print(f"    {line}")
                if len(lines) > 5:
                    print(f"    ... 还有 {len(lines)-5} 行")
        except Exception as e:
            print(f"    ❌ 读取失败: {e}")
    
    # 检查最近的HTML文件
    print(f"\n🌐 检查HTML文件中的data-speech属性:")
    html_files = list(Path("/Users/mac/Documents/GitHub/bookagent/outputs").glob("*.html"))
    
    if html_files:
        # 取最新的HTML文件
        latest_html = max(html_files, key=lambda f: f.stat().st_mtime)
        print(f"  📄 最新HTML: {latest_html.name}")
        
        try:
            with open(latest_html, 'r', encoding='utf-8') as f:
                content = f.read()
                
            import re
            speeches = re.findall(r'data-speech="([^"]*)"', content)
            print(f"  🎤 找到 {len(speeches)} 个data-speech属性:")
            
            for i, speech in enumerate(speeches, 1):
                preview = speech[:50] + "..." if len(speech) > 50 else speech
                print(f"    {i}: {preview}")
                
                # 检查对应的音频文件是否存在
                expected_audio = audio_dir / f"slide_{i:02d}.mp3"
                alt_audio = audio_dir / f"slide_{i:02d}.aiff"
                
                if expected_audio.exists():
                    size = expected_audio.stat().st_size
                    print(f"      ✅ 音频存在: {expected_audio.name} ({size:,} bytes)")
                elif alt_audio.exists():
                    size = alt_audio.stat().st_size
                    print(f"      ✅ 音频存在: {alt_audio.name} ({size:,} bytes)")
                else:
                    print(f"      ❌ 音频缺失: slide_{i:02d}.mp3")
                    
        except Exception as e:
            print(f"    ❌ 分析HTML失败: {e}")
    else:
        print("  ❌ 没有找到HTML文件")

def check_audio_playability():
    """检查音频文件是否可播放"""
    print(f"\n🔊 检查音频文件可播放性:")
    
    audio_dir = Path("/Users/mac/Documents/GitHub/bookagent/ppt_audio")
    audio_files = list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.aiff"))
    
    for audio_file in sorted(audio_files)[:3]:  # 只检查前3个
        print(f"  🎵 测试: {audio_file.name}")
        
        # 检查文件头
        try:
            with open(audio_file, 'rb') as f:
                header = f.read(16)
                
            if audio_file.suffix == '.mp3':
                # MP3文件应该以ID3标签或同步帧开始
                if header.startswith(b'ID3') or header[0:2] == b'\xff\xfb':
                    print(f"    ✅ MP3格式正确")
                else:
                    print(f"    ⚠️ MP3格式可能有问题: {header[:8].hex()}")
            elif audio_file.suffix == '.aiff':
                # AIFF文件应该以FORM开始
                if header.startswith(b'FORM'):
                    print(f"    ✅ AIFF格式正确")
                else:
                    print(f"    ⚠️ AIFF格式可能有问题: {header[:8].hex()}")
                    
        except Exception as e:
            print(f"    ❌ 读取文件头失败: {e}")

if __name__ == "__main__":
    diagnose_audio_matching()
    check_audio_playability()
