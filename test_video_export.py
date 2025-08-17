#!/usr/bin/env python3
"""
测试视频导出API
"""
import requests
import json

def test_video_export():
    """测试视频导出功能"""
    
    url = "http://0.0.0.0:8001/api/export-video"
    
    # 请求数据
    data = {
        "session_id": "a850a995-88ec-4362-b475-a3c839bcb8b1",
        "html_file": "presentation.html", 
        "audio_prefix": "a850a995-88ec-4362-b475-a3c839bcb8b1_slide"
    }
    
    print("🚀 正在测试视频导出API...")
    print(f"📡 URL: {url}")
    print(f"📦 数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data, timeout=300)  # 5分钟超时
        
        print(f"📊 状态码: {response.status_code}")
        print(f"📄 响应内容:")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                print(f"✅ 视频导出成功!")
                print(f"🎬 视频文件: {result.get('filename')}")
                print(f"📁 文件大小: {result.get('file_size')}")
                print(f"⏱️ 视频时长: {result.get('duration')}秒")
                print(f"🔗 下载地址: http://0.0.0.0:8001{result.get('video_url')}")
            else:
                print(f"❌ 视频导出失败: {result.get('error')}")
        else:
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏱️ 请求超时 - 视频生成可能需要更长时间")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_video_export()
