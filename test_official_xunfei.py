#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于官方文档的讯飞TTS测试
"""

import requests
import json
import base64
import hashlib
import time
from urllib.parse import urlencode
import hmac
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import sys
import os

class OfficialXunfeiTTS:
    def __init__(self, host="api-dx.xf-yun.com", app_id=None, api_key=None, api_secret=None):
        self.host = host
        self.app_id = app_id or "e6950ae6"
        self.api_key = api_key or "f2d4b9650c13355fc8286ac3fc34bf6e"
        self.api_secret = api_secret or "NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh"

    def assemble_auth_url(self, path):
        """生成鉴权的url"""
        params = self.assemble_auth_params(path)
        request_url = "http://" + self.host + path
        auth_url = request_url + "?" + urlencode(params)
        return auth_url

    def assemble_auth_params(self, path):
        """生成鉴权的参数"""
        format_date = format_date_time(mktime(datetime.now().timetuple()))
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + format_date + "\n"
        signature_origin += "POST " + path + " HTTP/1.1"
        
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = 'api_key="%s", algorithm="%s", headers="%s", signature="%s"' % (
            self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        params = {
            "host": self.host,
            "date": format_date,
            "authorization": authorization
        }
        return params

    def create_task(self, text):
        """创建任务"""
        create_path = "/v1/private/dts_create"
        auth_url = self.assemble_auth_url(create_path)
        
        encode_str = base64.encodebytes(text.encode("UTF8"))
        txt = encode_str.decode()
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "header": {
                "app_id": self.app_id,
            },
            "parameter": {
                "dts": {
                    "vcn": "x4_xiaoguo",
                    "language": "zh",
                    "speed": 50,
                    "volume": 50,
                    "pitch": 50,
                    "rhy": 1,
                    "bgs": 0,
                    "reg": 0,
                    "rdn": 0,
                    "scn": 0,
                    "audio": {
                        "encoding": "lame",
                        "sample_rate": 16000,
                        "channels": 1,
                        "bit_depth": 16,
                        "frame_size": 0
                    },
                    "pybuf": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "plain"
                    }
                }
            },
            "payload": {
                "text": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "text": txt
                }
            },
        }
        
        try:
            print("📝 创建TTS任务...")
            print(f"📋 请求文本: {text}")
            res = requests.post(url=auth_url, headers=headers, data=json.dumps(data))
            res = json.loads(res.text)
            print(f"📄 创建响应: {json.dumps(res, ensure_ascii=False)}")
            return res
        except Exception as e:
            print(f"❌ 创建任务异常: {e}")
            return None

    def query_task(self, task_id, max_retries=10):
        """查询任务"""
        query_path = "/v1/private/dts_query"
        auth_url = self.assemble_auth_url(query_path)
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "header": {
                "app_id": self.app_id,
                "task_id": task_id
            }
        }
        
        for i in range(max_retries):
            try:
                print(f"🔍 第{i+1}次查询任务状态...")
                time.sleep(1)
                
                res = requests.post(url=auth_url, headers=headers, data=json.dumps(data))
                res = json.loads(res.text)
                print(f"📄 查询响应: {json.dumps(res, ensure_ascii=False)}")
                
                code = res.get('header', {}).get('code')
                if code == 0:
                    task_status = res.get('header', {}).get('task_status')
                    print(f"📊 任务状态: {task_status}")
                    
                    if task_status == '5':  # 任务完成
                        audio_info = res.get('payload', {}).get('audio', {})
                        if audio_info:
                            audio = audio_info.get('audio')
                            if audio:
                                decode_audio = base64.b64decode(audio)
                                download_url = decode_audio.decode()
                                print(f"✅ 任务完成! 下载链接: {download_url}")
                                return download_url
                        print("❌ 未找到音频数据")
                        return None
                    else:
                        print(f"⏳ 任务处理中，状态码: {task_status}")
                else:
                    print(f"❌ 查询失败，错误码: {code}")
                    return None
                    
            except Exception as e:
                print(f"❌ 查询任务异常: {e}")
                
        print("❌ 查询超时")
        return None

    def synthesize_to_file(self, text, output_file):
        """合成语音到文件"""
        print(f"🎵 开始官方讯飞TTS合成...")
        print(f"📝 输入文本: {text}")
        print(f"📁 输出文件: {output_file}")
        
        # 创建任务
        create_result = self.create_task(text)
        if not create_result:
            return False
            
        code = create_result.get('header', {}).get('code')
        if code != 0:
            print(f"❌ 创建任务失败，错误码: {code}")
            message = create_result.get('header', {}).get('message', '')
            print(f"❌ 错误信息: {message}")
            return False
            
        task_id = create_result.get('header', {}).get('task_id')
        if not task_id:
            print("❌ 未获取到task_id")
            return False
            
        print(f"✅ 任务创建成功，task_id: {task_id}")
        
        # 查询任务结果
        download_url = self.query_task(task_id)
        if not download_url:
            return False
            
        # 下载音频文件
        try:
            print(f"📥 正在下载音频文件...")
            response = requests.get(download_url)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, "wb") as f:
                f.write(response.content)
                
            file_size = os.path.getsize(output_file)
            print(f"✅ 音频下载成功! 文件大小: {file_size} 字节")
            return True
            
        except Exception as e:
            print(f"❌ 下载音频失败: {e}")
            return False

def test_official_tts():
    """测试官方TTS实现"""
    print("=== 官方讯飞TTS测试 ===\n")
    
    tts = OfficialXunfeiTTS()
    
    # 测试用例
    test_cases = [
        "官方测试12345",
        "你好世界",
        "这是正确的讯飞语音合成测试"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🧪 测试案例 {i}: {text}")
        output_file = f"ppt_audio/official_test_{i}.mp3"
        
        success = tts.synthesize_to_file(text, output_file)
        
        if success:
            print(f"✅ 测试 {i} 成功!")
            
            # 播放音频验证
            try:
                import subprocess
                print(f"🔊 播放音频验证内容...")
                subprocess.run(["afplay", output_file], timeout=10)
                print(f"🎵 播放完成")
            except Exception as e:
                print(f"⚠️ 播放失败: {e}")
        else:
            print(f"❌ 测试 {i} 失败!")
            
        print("-" * 50)

if __name__ == "__main__":
    test_official_tts()


