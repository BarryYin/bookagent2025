#!/usr/bin/env python3
"""
讯飞语音合成音频处理工具
解决讯飞API返回的URL不是直接音频文件的问题
"""
import requests
import re
import base64
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json

class XunfeiAudioHandler:
    """讯飞音频处理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def is_xunfei_url(self, url):
        """检查是否是讯飞的下载URL"""
        return 'xf-yun.com' in url or 'sgw-dx' in url
    
    def download_audio_from_url(self, url, output_path=None):
        """
        从讯飞URL下载音频文件
        
        Args:
            url: 讯飞返回的下载链接
            output_path: 输出文件路径，如果为None则自动生成
            
        Returns:
            str: 成功时返回文件路径，失败时返回None
        """
        try:
            print(f"🔗 处理讯飞音频URL: {url[:100]}...")
            
            # 如果没有指定输出路径，自动生成
            if not output_path:
                # 从URL中提取任务ID作为文件名
                parsed = urlparse(url)
                path_parts = parsed.path.split('/')
                task_id = path_parts[-1] if path_parts else 'audio'
                output_path = f"xunfei_{task_id}.mp3"
            
            # 发送GET请求下载
            print("📥 正在下载音频...")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                # 检查内容类型
                content_type = response.headers.get('content-type', '')
                print(f"📋 内容类型: {content_type}")
                
                # 检查是否是JSON响应（可能包含错误信息）
                if 'application/json' in content_type:
                    try:
                        error_data = response.json()
                        print(f"❌ API返回错误: {error_data}")
                        return None
                    except:
                        pass
                
                # 保存音频文件
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # 验证文件
                file_size = Path(output_path).stat().st_size
                print(f"📊 文件大小: {file_size} 字节")
                
                if file_size > 100:  # 至少100字节才算有效音频
                    print(f"✅ 音频下载成功: {output_path}")
                    return output_path
                else:
                    print("❌ 下载的文件太小，可能不是有效音频")
                    Path(output_path).unlink(missing_ok=True)
                    return None
            
            elif response.status_code == 401:
                print("❌ 授权失败，可能是token过期")
                return None
            elif response.status_code == 404:
                print("❌ 文件不存在，可能是URL过期")
                return None
            else:
                print(f"❌ 下载失败，状态码: {response.status_code}")
                print(f"📄 响应内容: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ 下载过程中出错: {e}")
            return None
    
    def extract_download_url_from_response(self, api_response):
        """
        从讯飞API响应中提取下载URL
        
        Args:
            api_response: 讯飞查询任务API的响应
            
        Returns:
            str: 下载URL，如果提取失败返回None
        """
        try:
            if isinstance(api_response, str):
                api_response = json.loads(api_response)
            
            # 从payload.audio.audio字段提取base64编码的URL
            audio_b64 = api_response.get('payload', {}).get('audio', {}).get('audio')
            
            if audio_b64:
                # base64解码获取下载URL
                download_url = base64.b64decode(audio_b64).decode('utf-8')
                print(f"🔗 提取到下载URL: {download_url}")
                return download_url
            else:
                print("❌ 无法从API响应中提取下载URL")
                return None
                
        except Exception as e:
            print(f"❌ 提取下载URL时出错: {e}")
            return None
    
    def process_xunfei_audio(self, url_or_response, output_path=None):
        """
        处理讯飞音频（支持直接URL或API响应）
        
        Args:
            url_or_response: 讯飞下载URL或API响应JSON
            output_path: 输出文件路径
            
        Returns:
            str: 成功时返回文件路径，失败时返回None
        """
        # 如果是API响应，先提取URL
        if isinstance(url_or_response, (dict, str)) and not url_or_response.startswith('http'):
            url = self.extract_download_url_from_response(url_or_response)
            if not url:
                return None
        else:
            url = url_or_response
        
        # 下载音频文件
        return self.download_audio_from_url(url, output_path)

def main():
    """测试函数"""
    handler = XunfeiAudioHandler()
    
    # 测试URL
    test_url = "http://sgw-dx.xf-yun.com/api/v1/dts0/qnykm51uz534fix3movgl6d4jz?authorization=c2ltcGxlLWp3dCBhaz1kdHMwMDAwMDAwMDtleHA9MTc1Nzc2MTE2ODthbGdvPWhtYWMtc2hhMjU2O3NpZz12cVVvbUczS2JxNm4zQ0hzZ2FxT1l4N09jWnA1T2FMcysvQ0pPQm5BR0lrPQ==&x_location=y2UXxTNYeSUBdo=="
    
    print("🎵 讯飞音频处理工具测试")
    print("=" * 50)
    
    result = handler.process_xunfei_audio(test_url, "test_handler_audio.mp3")
    
    if result:
        print(f"\n🎉 处理成功！音频文件: {result}")
    else:
        print("\n💥 处理失败！")

if __name__ == "__main__":
    main()