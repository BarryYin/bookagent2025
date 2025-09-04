#!/usr/bin/env python3
"""
可靠的语音生成器 - 专为 appbook.py 设计
集成WebSocket讯飞TTS + Fish Audio + 系统语音的完整解决方案
具有快速回退机制，确保始终能生成语音
"""

import os
import sys
import json
import time
import threading
import ssl
import subprocess
import base64
import hashlib
import hmac
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode
import importlib
import requests

# WebSocket支持
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("⚠️ websocket-client未安装，讯飞TTS将不可用")

# BeautifulSoup支持
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️ beautifulsoup4未安装，将使用正则表达式解析HTML")

# Fish Audio支持检查
def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False

FISH_AUDIO_AVAILABLE = _module_available('fish_audio_sdk')


class WebSocketXunfeiTTS:
    """WebSocket方式的讯飞语音合成"""
    
    def __init__(self, app_id=None, api_secret=None, api_key=None):
        self.app_id = app_id or "e6950ae6"
        self.api_secret = api_secret or "NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh"
        self.api_key = api_key or "f2d4b9650c13355fc8286ac3fc34bf6e"
        self.audio_data = []
        self.synthesis_complete = False
        self.synthesis_success = False
        self.error_message = None

    def create_url(self):
        """创建WebSocket连接URL"""
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接字符串
        signature_origin = "host: ws-api.xfyun.cn\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET /v2/tts HTTP/1.1"
        
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'), 
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        return url

    def on_message(self, ws, message):
        """接收消息回调"""
        try:
            message = json.loads(message)
            code = message["code"]
            audio = message.get("data", {}).get("audio", "")
            status = message["data"]["status"]
            
            if code != 0:
                self.error_message = message.get("message", f"错误码: {code}")
                self.synthesis_success = False
                self.synthesis_complete = True
                ws.close()
                return
                
            if audio:
                audio_data = base64.b64decode(audio)
                self.audio_data.append(audio_data)
                
            if status == 2:  # 合成完成
                self.synthesis_success = True
                self.synthesis_complete = True
                ws.close()
                
        except Exception as e:
            self.error_message = f"处理消息失败: {e}"
            self.synthesis_success = False
            self.synthesis_complete = True

    def on_error(self, ws, error):
        """错误回调"""
        self.error_message = f"WebSocket错误: {error}"
        self.synthesis_success = False
        self.synthesis_complete = True

    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        if not self.synthesis_complete:
            self.synthesis_complete = True

    def on_open(self, ws):
        """连接打开回调"""
        def run():
            try:
                data = {
                    "common": {
                        "app_id": self.app_id,
                    },
                    "business": {
                        "aue": "lame",
                        "auf": "audio/L16;rate=16000",
                        "vcn": "xiaoyan",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "bgs": 0,
                    },
                    "data": {
                        "status": 2,
                        "text": base64.b64encode(self.text.encode('utf-8')).decode('utf-8'),
                    }
                }
                ws.send(json.dumps(data))
            except Exception as e:
                self.error_message = f"发送数据失败: {e}"
                self.synthesis_success = False
                self.synthesis_complete = True
        
        thread = threading.Thread(target=run)
        thread.start()

    def synthesize_to_file(self, text, output_file, timeout=10):
        """合成语音到文件"""
        if not WEBSOCKET_AVAILABLE:
            return False
            
        self.text = text
        self.audio_data = []
        self.synthesis_complete = False
        self.synthesis_success = False
        self.error_message = None
        
        try:
            url = self.create_url()
            ws = websocket.WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # 启动WebSocket连接（在新线程中）
            def run_ws():
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            ws_thread = threading.Thread(target=run_ws)
            ws_thread.daemon = True
            ws_thread.start()
            
            # 等待完成或超时
            start_time = time.time()
            while not self.synthesis_complete and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            # 如果超时，关闭连接
            if not self.synthesis_complete:
                ws.close()
                return False
            
            # 检查是否成功
            if self.synthesis_success and self.audio_data:
                # 保存音频文件
                with open(output_file, "wb") as f:
                    for chunk in self.audio_data:
                        f.write(chunk)
                return True
            else:
                if self.error_message:
                    print(f"讯飞TTS失败: {self.error_message}")
                return False
                
        except Exception as e:
            print(f"讯飞TTS异常: {e}")
            return False


class FishAudioTTS:
    """Fish Audio语音合成"""
    
    def __init__(self):
        self.available = FISH_AUDIO_AVAILABLE
        if self.available:
            try:
                from fish_audio_sdk import Session
                self.Session = Session
            except ImportError:
                self.available = False

    def synthesize_to_file(self, text, output_file, timeout=15):
        """使用Fish Audio合成语音"""
        if not self.available:
            return False
            
        try:
            session = self.Session()
            audio_data = session.tts(text)
            
            if audio_data:
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                return True
            return False
            
        except Exception as e:
            print(f"Fish Audio TTS失败: {e}")
            return False


class SystemTTS:
    """系统语音合成（macOS say命令）"""
    
    def synthesize_to_file(self, text, output_file, timeout=20):
        """使用系统语音合成"""
        try:
            # 使用macOS的say命令
            cmd = [
                "say", 
                "-v", "Tingting",  # 中文语音
                "-o", str(output_file).replace('.mp3', '.aiff'),  # say输出aiff格式
                text
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                # 转换为mp3格式
                aiff_file = str(output_file).replace('.mp3', '.aiff')
                if os.path.exists(aiff_file):
                    try:
                        # 使用ffmpeg转换（如果可用）
                        convert_cmd = ["ffmpeg", "-i", aiff_file, "-y", output_file]
                        convert_result = subprocess.run(
                            convert_cmd, 
                            capture_output=True, 
                            timeout=10
                        )
                        
                        if convert_result.returncode == 0:
                            os.remove(aiff_file)  # 删除临时文件
                            return True
                        else:
                            # 如果ffmpeg失败，保留aiff文件
                            os.rename(aiff_file, output_file.replace('.mp3', '.aiff'))
                            return True
                            
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        # ffmpeg不可用，保留aiff文件
                        os.rename(aiff_file, output_file.replace('.mp3', '.aiff'))
                        return True
            
            return False
            
        except Exception as e:
            print(f"系统语音合成失败: {e}")
            return False


class ReliableVoiceGenerator:
    """可靠的语音生成器 - 多引擎回退机制"""
    
    def __init__(self, html_file, audio_prefix="slide"):
        self.html_file = Path(html_file)
        self.audio_prefix = audio_prefix
        self.audio_dir = Path("ppt_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
        # 初始化语音引擎
        self.xunfei_tts = WebSocketXunfeiTTS()
        self.fish_tts = FishAudioTTS()
        self.system_tts = SystemTTS()
        
        # 引擎优先级
        self.engines = [
            ("讯飞TTS", self.xunfei_tts, 8),      # 8秒超时
            ("Fish Audio", self.fish_tts, 15),     # 15秒超时
            ("系统语音", self.system_tts, 20)      # 20秒超时
        ]

    def extract_slides(self):
        """从HTML文件提取幻灯片文本"""
        if not self.html_file.exists():
            print(f"❌ HTML文件不存在: {self.html_file}")
            return []
        
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            slides = []
            if BS4_AVAILABLE:
                # 使用BeautifulSoup解析
                soup = BeautifulSoup(content, 'html.parser')
                elements = soup.find_all(attrs={'data-speech': True})
                
                for i, element in enumerate(elements):
                    text = element.get('data-speech', '').strip()
                    if text:
                        slides.append({
                            'index': i + 1,
                            'text': text,
                            'audio_file': self.audio_dir / f"{self.audio_prefix}_{i+1:02d}.mp3"
                        })
            else:
                # 使用正则表达式解析
                import re
                pattern = r'data-speech="([^"]*)"'
                matches = re.findall(pattern, content)
                
                for i, text in enumerate(matches):
                    if text.strip():
                        slides.append({
                            'index': i + 1,
                            'text': text.strip(),
                            'audio_file': self.audio_dir / f"{self.audio_prefix}_{i+1:02d}.mp3"
                        })
            
            print(f"📋 提取到 {len(slides)} 张幻灯片")
            return slides
            
        except Exception as e:
            print(f"❌ 提取幻灯片失败: {e}")
            return []

    def generate_audio_for_slide(self, slide):
        """为单张幻灯片生成音频"""
        text = slide['text']
        output_file = slide['audio_file']
        
        print(f"🎵 生成音频 [{slide['index']}]: {text[:30]}...")
        
        # 如果文件已存在且大小合理，跳过
        if output_file.exists() and output_file.stat().st_size > 1000:
            print(f"  └─ ✅ 音频文件已存在，跳过")
            return str(output_file)
        
        # 尝试各个引擎
        for engine_name, engine, timeout in self.engines:
            try:
                print(f"  ├─ 尝试 {engine_name}...")
                start_time = time.time()
                
                success = engine.synthesize_to_file(text, str(output_file), timeout=timeout)
                
                if success and output_file.exists() and output_file.stat().st_size > 100:
                    elapsed = time.time() - start_time
                    print(f"  └─ ✅ {engine_name} 成功 ({elapsed:.1f}s)")
                    return str(output_file)
                else:
                    print(f"  ├─ ❌ {engine_name} 失败")
                    
            except Exception as e:
                print(f"  ├─ ❌ {engine_name} 异常: {e}")
                continue
        
        print(f"  └─ ❌ 所有语音引擎都失败了")
        return None

    def generate_all_audio(self):
        """生成所有音频文件"""
        slides = self.extract_slides()
        if not slides:
            return []
        
        results = []
        print(f"\n🎤 开始生成 {len(slides)} 个音频文件...")
        
        for slide in slides:
            audio_file = self.generate_audio_for_slide(slide)
            if audio_file:
                results.append({
                    'index': slide['index'],
                    'text': slide['text'],
                    'audio_file': audio_file,
                    'title': f"幻灯片 {slide['index']}"
                })
        
        print(f"\n✅ 音频生成完成: {len(results)}/{len(slides)} 成功")
        return results

    def create_playlist(self, generated):
        """创建播放列表"""
        if not generated:
            return None
            
        m3u_file = self.audio_dir / f"{self.audio_prefix}_playlist.m3u"
        
        with open(m3u_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for item in generated:
                duration = self._get_audio_duration(item['audio_file'])
                title = item.get('title', f"幻灯片 {item['index']}")
                filename = Path(item['audio_file']).name
                f.write(f"#EXTINF:{duration},{title}\n{filename}\n")
        
        print(f"📝 播放列表: {m3u_file}")
        return str(m3u_file)

    def _get_audio_duration(self, audio_file):
        """获取音频时长（简单估算）"""
        try:
            # 简单估算：文件大小 / 每秒字节数
            file_size = Path(audio_file).stat().st_size
            # MP3大概8kbps，即1KB/s
            estimated_duration = max(1, file_size // 1024)
            return min(estimated_duration, 60)  # 最长60秒
        except:
            return 10  # 默认10秒


def main():
    """测试函数"""
    if len(sys.argv) < 2:
        print("用法: python reliable_voice_generator.py <html_file> [audio_prefix]")
        return
    
    html_file = sys.argv[1]
    audio_prefix = sys.argv[2] if len(sys.argv) > 2 else "slide"
    
    generator = ReliableVoiceGenerator(html_file, audio_prefix)
    results = generator.generate_all_audio()
    
    if results:
        generator.create_playlist(results)
        print(f"\n🎉 完成！生成了 {len(results)} 个音频文件")
    else:
        print("\n❌ 没有生成任何音频文件")


if __name__ == "__main__":
    main()
