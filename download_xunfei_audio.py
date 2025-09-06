#!/usr/bin/env python3
"""
下载讯飞语音合成的音频文件
"""
import requests
import sys
from pathlib import Path

def download_xunfei_audio(url, output_file="downloaded_audio.mp3"):
    """
    从讯飞API下载链接下载音频文件
    
    Args:
        url: 讯飞返回的下载链接
        output_file: 输出文件名
    """
    try:
        print(f"🔗 下载链接: {url}")
        print(f"📁 输出文件: {output_file}")
        
        # 发送GET请求下载音频
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print("📥 正在下载音频...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            print(f"📋 内容类型: {content_type}")
            
            # 保存文件
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            # 检查文件大小
            file_size = Path(output_file).stat().st_size
            print(f"📊 文件大小: {file_size} 字节")
            
            if file_size > 0:
                print(f"✅ 音频下载成功: {output_file}")
                return True
            else:
                print("❌ 下载的文件为空")
                return False
        else:
            print(f"❌ 下载失败，状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ 下载过程中出错: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python download_xunfei_audio.py <讯飞下载链接> [输出文件名]")
        print("示例: python download_xunfei_audio.py 'http://sgw-dx.xf-yun.com/api/v1/dts0/...' audio.mp3")
        return
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "xunfei_audio.mp3"
    
    print("🎵 讯飞音频下载工具")
    print("=" * 50)
    
    success = download_xunfei_audio(url, output_file)
    
    if success:
        print("\n🎉 下载完成！")
        print(f"🎵 可以播放文件: {output_file}")
    else:
        print("\n💥 下载失败！")
        print("可能的原因:")
        print("1. 链接已过期")
        print("2. 授权参数无效")
        print("3. 网络连接问题")

if __name__ == "__main__":
    main()