#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的讯飞API凭证是否可以正常生成语音
"""

import hashlib
import hmac
import base64
import urllib.parse
import time
import json
import websocket
import threading
import ssl
from datetime import datetime
from urllib.parse import urlencode

class XunfeiTTSTest:
    def __init__(self, app_id, api_secret, api_key):
        self.app_id = app_id
        self.api_secret = api_secret
        self.api_key = api_key
        self.audio_data = []
        self.status = ""
        
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
            sid = message["sid"]
            audio = message.get("data", {}).get("audio", "")
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            
            print(f"收到消息: code={code}, sid={sid}, status={status}, audio_len={len(audio)}")
            
            if code != 0:
                errMsg = message["message"]
                print(f"❌ 语音合成失败: {code} - {errMsg}")
                ws.close()
                return
                
            if audio:
                self.audio_data.append(audio)
                
            if status == 2:
                print("✅ 语音合成完成")
                ws.close()
                
        except Exception as e:
            print(f"处理消息时出错: {e}")
    
    def on_error(self, ws, error):
        """错误回调"""
        print(f"❌ WebSocket错误: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        print("WebSocket连接已关闭")
    
    def on_open(self, ws):
        """连接打开回调"""
        def run():
            # 发送数据
            data = {
                "common": {
                    "app_id": self.app_id,
                },
                "business": {
                    "aue": "lame",  # 音频编码，可选值：raw（生成 pcm 格式）、lame（生成 mp3 格式）
                    "auf": "audio/L16;rate=16000",  # 音频采样率
                    "vcn": "xiaoyan",  # 发音人，可选值：见控制台-我的应用-语音合成-添加试用或购买发音人
                    "speed": 50,  # 语速，可选值：[0-100]，默认为50
                    "volume": 50,  # 音量，可选值：[0-100]，默认为50
                    "pitch": 50,  # 音调，可选值：[0-100]，默认为50
                    "bgs": 0,  # 背景音乐，可选值：[0-2]，默认为0
                },
                "data": {
                    "status": 2,  # 数据状态，固定值2
                    "text": base64.b64encode("这是一个讯飞语音合成测试，使用新的API凭证。".encode('utf-8')).decode('utf-8'),
                }
            }
            
            ws.send(json.dumps(data))
            print("✅ 发送数据成功")
            
        thread = threading.Thread(target=run)
        thread.start()
    
    def test_synthesis(self):
        """测试语音合成"""
        print("=== 讯飞语音合成测试 ===")
        print(f"App ID: {self.app_id}")
        print(f"API Key: {self.api_key[:10]}...")
        print(f"API Secret: {self.api_secret[:10]}...")
        
        try:
            # 创建WebSocket连接
            url = self.create_url()
            print(f"连接URL: {url[:100]}...")
            
            ws = websocket.WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # 开始连接
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 检查结果
            if self.audio_data:
                # 保存音频文件
                output_file = "/Users/mac/Documents/GitHub/bookagent/create/test_xunfei_output.mp3"
                with open(output_file, "wb") as f:
                    for chunk in self.audio_data:
                        f.write(chunk)
                print(f"✅ 音频文件已保存: {output_file}")
                print(f"音频数据大小: {sum(len(chunk) for chunk in self.audio_data)} bytes")
                return True
            else:
                print("❌ 没有接收到音频数据")
                return False
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False

def main():
    # 使用新的API凭证
    app_id = "e6950ae6"
    api_secret = "NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh"
    api_key = "f2d4b9650c13355fc8286ac3fc34bf6e"
    
    tester = XunfeiTTSTest(app_id, api_secret, api_key)
    success = tester.test_synthesis()
    
    if success:
        print("🎉 讯飞语音合成测试成功！")
    else:
        print("❌ 讯飞语音合成测试失败！")

if __name__ == "__main__":
    main()
