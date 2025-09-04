#!/usr/bin/env python3
"""
使用WebSocket方式的讯飞语音合成（经过验证可以工作）
"""

import hashlib
import hmac
import base64
import time
import json
import websocket
import threading
import ssl
from datetime import datetime
from urllib.parse import urlencode
import os
from pathlib import Path

class XunfeiWebSocketTTS:
    """基于WebSocket的讯飞语音合成类"""
    
    def __init__(self, app_id, api_secret, api_key):
        self.app_id = app_id
        self.api_secret = api_secret
        self.api_key = api_key
        self.audio_data = []
        self.completed = False
        self.error = None
        
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
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), 
                               signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = "api_key=\"" + self.api_key + "\", " + \
                              "algorithm=\"hmac-sha256\", " + \
                              "headers=\"host date request-line\", " + \
                              "signature=\"" + signature_sha + "\""
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
                self.error = f"API错误: {code} - {message.get('message', '未知错误')}"
                ws.close()
                return
                
            if audio:
                audio_bytes = base64.b64decode(audio)
                self.audio_data.append(audio_bytes)
                
            if status == 2:
                self.completed = True
                ws.close()
                
        except Exception as e:
            self.error = f"处理消息时出错: {e}"
    
    def on_error(self, ws, error):
        """错误回调"""
        self.error = f"WebSocket错误: {error}"
    
    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        pass
    
    def on_open(self, ws):
        """连接打开回调"""
        def run():
            # 发送数据
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
    
    def synthesize_to_file(self, text, output_file, timeout=30):
        """合成语音并保存到文件"""
        self.text = text
        self.audio_data = []
        self.completed = False
        self.error = None
        
        try:
            # 创建WebSocket连接
            url = self.create_url()
            
            ws = websocket.WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # 开始连接（设置超时）
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 等待完成或超时
            start_time = time.time()
            while not self.completed and not self.error and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if self.error:
                print(f"❌ {self.error}")
                return False
                
            if not self.completed:
                print("❌ 操作超时")
                return False
            
            # 保存音频文件
            if self.audio_data:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    for chunk in self.audio_data:
                        f.write(chunk)
                return True
            else:
                print("❌ 没有接收到音频数据")
                return False
                
        except Exception as e:
            print(f"❌ 合成失败: {e}")
            return False

# 更新PPTVoiceGenerator以使用WebSocket版本
def patch_ppt_voice_generator():
    """修补PPTVoiceGenerator以使用WebSocket TTS"""
    import sys
    sys.path.append('/Users/mac/Documents/GitHub/bookagent/create')
    
    try:
        from ppt_voice_generator import PPTVoiceGenerator
        
        # 创建新的生成音频方法
        def generate_audio_for_slide_websocket(self, slide: dict) -> str | None:
            """使用WebSocket TTS生成幻灯片音频"""
            text = slide['text']
            audio_file = Path(self.audio_dir) / f"{self.audio_prefix}_{slide['index']:02d}.mp3"
            
            print(f"🎙️ 正在为第{slide['index']}张幻灯片生成语音: {text[:30]}...")
            
            # 使用WebSocket TTS
            tts = XunfeiWebSocketTTS(
                app_id="e6950ae6",
                api_secret="NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
                api_key="f2d4b9650c13355fc8286ac3fc34bf6e"
            )
            
            success = tts.synthesize_to_file(text, str(audio_file))
            
            if success and audio_file.exists():
                print(f"✅ 讯飞语音生成成功: {audio_file.name}")
                return str(audio_file)
            else:
                print(f"❌ 讯飞语音生成失败，尝试系统语音...")
                # 回退到系统语音
                return self._generate_system_audio(text, audio_file)
        
        # 替换方法
        PPTVoiceGenerator.generate_audio_for_slide = generate_audio_for_slide_websocket
        
        return PPTVoiceGenerator
        
    except ImportError as e:
        print(f"导入PPTVoiceGenerator失败: {e}")
        return None

def test_websocket_tts():
    """测试WebSocket TTS"""
    print("=== 测试WebSocket方式的讯飞TTS ===")
    
    tts = XunfeiWebSocketTTS(
        app_id="e6950ae6",
        api_secret="NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
        api_key="f2d4b9650c13355fc8286ac3fc34bf6e"
    )
    
    test_text = "这是使用WebSocket方式的讯飞语音合成测试。"
    output_file = "/Users/mac/Documents/GitHub/bookagent/create/test_websocket_xunfei.mp3"
    
    print(f"测试文本: {test_text}")
    print(f"输出文件: {output_file}")
    
    success = tts.synthesize_to_file(test_text, output_file)
    
    if success and os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ WebSocket TTS成功！文件大小: {file_size} bytes")
        return True
    else:
        print("❌ WebSocket TTS失败")
        return False

if __name__ == "__main__":
    success = test_websocket_tts()
    
    if success:
        print("\n🎉 WebSocket方式的讯飞TTS可以正常工作！")
        print("现在可以用这个方式替代原来的HTTP API。")
    else:
        print("\n❌ WebSocket方式也无法工作。")
