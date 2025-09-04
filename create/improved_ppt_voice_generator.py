#!/usr/bin/env python3
"""
改进的PPT语音生成器 - 使用WebSocket讯飞TTS
"""

import os
import sys
import re
import json
import time
import subprocess
import threading
import ssl
from pathlib import Path
import importlib
import base64
import hashlib
import hmac
from datetime import datetime
from urllib.parse import urlencode


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


BS4_AVAILABLE = _module_available('bs4')
FISH_AUDIO_AVAILABLE = _module_available('fish_audio_sdk')
WEBSOCKET_AVAILABLE = _module_available('websocket')

# 动态导入
if BS4_AVAILABLE:
    from bs4 import BeautifulSoup
if FISH_AUDIO_AVAILABLE:
    from fish_audio_sdk import Session, TTSRequest
if WEBSOCKET_AVAILABLE:
    import websocket


class XunfeiWebSocketTTS:
    """讯飞语音合成类 - 使用WebSocket API"""
    def __init__(self, app_id=None, api_secret=None, api_key=None):
        self.app_id = app_id or os.getenv("XUNFEI_APP_ID", "e6950ae6")
        self.api_key = api_key or os.getenv("XUNFEI_API_KEY", "f2d4b9650c13355fc8286ac3fc34bf6e")
        self.api_secret = api_secret or os.getenv("XUNFEI_API_SECRET", "NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh")
        self.audio_data = []
        self.status = ""
        self.error_msg = ""
        
    def create_url(self):
        """创建WebSocket连接URL"""
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        signature_origin = "host: ws-api.xfyun.cn\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET /v2/tts HTTP/1.1"
        
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), 
                               signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = "api_key=\"" + self.api_key + "\", " + \
                              "algorithm=\"hmac-sha256\", " + \
                              "headers=\"host date request-line\", " + \
                              "signature=\"" + signature_sha + "\""
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        
        url = url + '?' + urlencode(v)
        return url
    
    def on_message(self, ws, message):
        """接收消息回调"""
        try:
            message = json.loads(message)
            code = message["code"]
            audio = message.get("data", {}).get("audio", "")
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            
            if code != 0:
                errMsg = message["message"]
                self.error_msg = f"语音合成失败: {code} - {errMsg}"
                self.status = "error"
                ws.close()
                return
                
            if audio:
                self.audio_data.append(audio)
                
            if status == 2:
                self.status = "completed"
                ws.close()
                
        except Exception as e:
            self.error_msg = f"处理消息时出错: {e}"
            self.status = "error"
    
    def on_error(self, ws, error):
        """错误回调"""
        self.error_msg = f"WebSocket错误: {error}"
        self.status = "error"
    
    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        if self.status == "":
            self.status = "closed"
    
    def on_open(self, ws):
        """连接打开回调"""
        def run():
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
            
        thread = threading.Thread(target=run)
        thread.start()

    def synthesize_to_file(self, text, output_file, voice="xiaoyan", max_wait=30):
        """合成语音并保存到文件"""
        if not WEBSOCKET_AVAILABLE:
            print("⚠️ websocket-client未安装，跳过讯飞语音合成")
            return False
            
        self.text = text
        self.audio_data = []
        self.status = ""
        self.error_msg = ""
        
        try:
            url = self.create_url()
            
            ws = websocket.WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            wst = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
            wst.daemon = True
            wst.start()
            
            start_time = time.time()
            while self.status == "" and time.time() - start_time < max_wait:
                time.sleep(0.1)
            
            if self.status == "completed" and self.audio_data:
                with open(output_file, "wb") as f:
                    for chunk in self.audio_data:
                        f.write(chunk)
                return True
            elif self.status == "error":
                print(f"讯飞语音合成错误: {self.error_msg}")
                return False
            else:
                print("讯飞语音合成超时")
                return False
                
        except Exception as e:
            print(f"讯飞语音合成异常: {e}")
            return False


class ImprovedPPTVoiceGenerator:
    """改进的PPT语音生成器"""
    
    def __init__(self, html_file: str = "高效人士的7个习惯PPT演示.html", audio_prefix: str = "habit_slide"):
        self.html_file = html_file
        self.audio_prefix = audio_prefix
        self.output_dir = Path("ppt_audio")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化语音引擎
        self.xunfei_tts = XunfeiWebSocketTTS()

    def extract_slides(self) -> list[dict]:
        """从HTML中提取幻灯片内容"""
        slides = []
        
        if not BS4_AVAILABLE:
            print("⚠️ BeautifulSoup4未安装，使用简单解析")
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单正则提取
            pattern = r'data-speech=["\'](.*?)["\']'
            matches = re.findall(pattern, content)
            
            for i, text in enumerate(matches):
                slides.append({
                    'slide_number': i + 1,
                    'text': text.strip(),
                    'audio_file': f"{self.audio_prefix}_{i+1:02d}.mp3"
                })
        else:
            # 使用BeautifulSoup解析
            with open(self.html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            elements = soup.find_all(attrs={"data-speech": True})
            
            for i, element in enumerate(elements):
                text = element.get('data-speech', '').strip()
                if text:
                    slides.append({
                        'slide_number': i + 1,
                        'text': text,
                        'audio_file': f"{self.audio_prefix}_{i+1:02d}.mp3"
                    })
        
        return slides

    def _generate_system_audio(self, text: str, output_file: Path) -> str | None:
        """使用系统语音生成"""
        try:
            # macOS say命令
            cmd = ['say', '-o', str(output_file), text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and output_file.exists():
                return str(output_file)
            else:
                print(f"系统语音生成失败: {result.stderr}")
                return None
        except Exception as e:
            print(f"系统语音生成异常: {e}")
            return None

    def _generate_fish_audio(self, text: str, output_file: Path) -> str | None:
        """使用Fish Audio生成"""
        if not FISH_AUDIO_AVAILABLE:
            return None
            
        try:
            session = Session()
            result = session.tts(TTSRequest(text=text))
            
            with open(output_file, 'wb') as f:
                f.write(result)
            
            return str(output_file)
        except Exception as e:
            print(f"Fish Audio生成失败: {e}")
            return None

    def generate_audio_for_slide(self, slide: dict) -> str | None:
        """为单个幻灯片生成音频"""
        text = slide['text']
        output_file = self.output_dir / slide['audio_file']
        
        if not text.strip():
            print(f"跳过空文本: slide {slide['slide_number']}")
            return None
        
        print(f"🎵 生成音频 [{slide['slide_number']}]: {text[:50]}...")
        
        # 1. 优先尝试讯飞TTS (WebSocket)
        if self.xunfei_tts.synthesize_to_file(text, str(output_file)):
            print(f"✅ 讯飞TTS生成成功: {output_file}")
            return str(output_file)
        
        # 2. 尝试Fish Audio
        result = self._generate_fish_audio(text, output_file)
        if result:
            print(f"✅ Fish Audio生成成功: {output_file}")
            return result
        
        # 3. 回退到系统语音
        result = self._generate_system_audio(text, output_file)
        if result:
            print(f"✅ 系统语音生成成功: {output_file}")
            return result
        
        print(f"❌ 所有语音引擎都失败了: slide {slide['slide_number']}")
        return None

    def generate_all_audio(self) -> list[dict]:
        """生成所有音频"""
        slides = self.extract_slides()
        
        if not slides:
            print("❌ 没有找到任何幻灯片内容")
            return []
        
        print(f"📄 找到 {len(slides)} 张幻灯片")
        
        generated = []
        for slide in slides:
            audio_file = self.generate_audio_for_slide(slide)
            if audio_file:
                slide['audio_file'] = audio_file
                generated.append(slide)
        
        return generated

    def create_playlist(self, generated: list[dict]) -> str:
        """创建M3U播放列表"""
        m3u = self.output_dir / f"{Path(self.html_file).stem}配音列表.m3u"
        
        with open(m3u, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for item in generated:
                title = f"幻灯片{item['slide_number']}: {item['text'][:30]}"
                dur = 5  # 估算时长
                name = Path(item['audio_file']).name
                f.write(f"#EXTINF:{dur},{title}\n{name}\n")
                
        print(f"📝 播放列表: {m3u}")
        return str(m3u)


def main():
    html_file = sys.argv[1] if len(sys.argv) > 1 else "高效人士的7个习惯PPT演示.html"
    audio_prefix = sys.argv[2] if len(sys.argv) > 2 else "habit_slide"
    
    generator = ImprovedPPTVoiceGenerator(html_file, audio_prefix)

    if not Path(generator.html_file).exists():
        print(f"❌ 找不到 HTML 文件: {generator.html_file}")
        sys.exit(1)

    generated = generator.generate_all_audio()
    if generated:
        generator.create_playlist(generated)
        print("\n🎉 完成！可在 ppt_audio 目录查看")
        print(f"📱 可用播放列表: {Path(generator.html_file).stem}配音列表.m3u")
        sys.exit(0)
    else:
        print("❌ 未生成任何音频")
        sys.exit(2)


if __name__ == "__main__":
    main()
