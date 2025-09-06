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
import requests  # HTTP API需要

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
    """HTTP方式的讯飞语音合成（参考demo实现）"""
    
    def __init__(self, app_id=None, api_secret=None, api_key=None):
        # 尝试从配置文件读取API密钥
        config = self._load_config()
        
        self.app_id = app_id or config.get('app_id') or "e6950ae6"
        self.api_secret = api_secret or config.get('api_secret') or "NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh"
        self.api_key = api_key or config.get('api_key') or "f2d4b9650c13355fc8286ac3fc34bf6e"
        self.host = "api-dx.xf-yun.com"
        
        # 检查是否使用默认密钥
        if self.app_id == "e6950ae6":
            print("⚠️ [警告] 使用默认API密钥，可能导致音频内容错误！")
            print("请在 xunfei_config.json 中配置正确的讯飞API密钥")
    
    def _load_config(self):
        """加载讯飞配置"""
        try:
            import json
            config_path = Path(__file__).parent.parent / "xunfei_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    xunfei_config = data.get('xunfei', {})
                    
                    # 检查配置是否为占位符
                    if (xunfei_config.get('app_id') == "你的APP_ID" or 
                        xunfei_config.get('api_key') == "你的API_KEY"):
                        print("⚠️ [警告] xunfei_config.json 中的API密钥未配置")
                        return {}
                    
                    return xunfei_config
            return {}
        except Exception as e:
            print(f"⚠️ [警告] 读取配置文件失败: {e}")
            return {}

    def assemble_auth_url(self, path):
        """生成鉴权的url（参考demo实现）"""
        params = self.assemble_auth_params(path)
        # 请求地址
        request_url = "http://" + self.host + path
        # 拼接请求地址和鉴权参数，生成带鉴权参数的url
        auth_url = request_url + "?" + urlencode(params)
        return auth_url
    
    def assemble_auth_params(self, path):
        """生成鉴权的参数（参考demo实现）"""
        from wsgiref.handlers import format_date_time
        from time import mktime
        
        # 生成RFC1123格式的时间戳
        format_date = format_date_time(mktime(datetime.now().timetuple()))
        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + format_date + "\n"
        signature_origin += "POST " + path + " HTTP/1.1"
        # 进行hmac-sha256加密
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        # 构建请求参数
        authorization_origin = 'api_key="%s", algorithm="%s", headers="%s", signature="%s"' % (
            self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        # 将请求参数使用base64编码
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        params = {
            "host": self.host,
            "date": format_date,
            "authorization": authorization
        }
        return params

    def create_task(self, text):
        """创建任务（参考demo实现）"""
        # 创建任务的路由
        create_path = "/v1/private/dts_create"
        # 拼接鉴权参数后生成的url
        auth_url = self.assemble_auth_url(create_path)
        # 合成文本
        encode_str = base64.encodebytes(text.encode("UTF8"))
        txt = encode_str.decode()
        # 请求头
        headers = {'Content-Type': 'application/json'}
        # 请求参数
        data = {
            "header": {
                "app_id": self.app_id,
            },
            "parameter": {
                "dts": {
                    "vcn": "x4_mingge",  # 使用明哥发音人（与demo一致）
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
                        "encoding": "lame",  # MP3格式
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
            import requests
            res = requests.post(url=auth_url, headers=headers, data=json.dumps(data), timeout=10)
            res = json.loads(res.text)
            return res
        except Exception as e:
            print(f"创建任务接口调用异常，错误详情:{e}")
            return None
    
    def query_task(self, task_id):
        """查询任务（参考demo实现）"""
        # 查询任务的路由
        query_path = "/v1/private/dts_query"
        # 拼接鉴权参数后生成的url
        auth_url = self.assemble_auth_url(query_path)
        # 请求头
        headers = {'Content-Type': 'application/json'}
        # 请求参数
        data = {
            "header": {
                "app_id": self.app_id,
                "task_id": task_id
            }
        }
        try:
            import requests
            res = requests.post(url=auth_url, headers=headers, data=json.dumps(data), timeout=10)
            res = json.loads(res.text)
            return res
        except Exception as e:
            print(f"查询任务接口调用异常，错误详情:{e}")
            return None

    def synthesize_to_file(self, text, output_file, timeout=30):
        """合成语音到文件 - 使用HTTP API（参考demo实现）"""
        # 详细调试信息
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"    🔍 [DEBUG {timestamp}] 讯飞TTS开始合成")
        print(f"    📝 [DEBUG] 输入文本: {repr(text[:50])}...")
        print(f"    📏 [DEBUG] 文本长度: {len(text)} 字符")
        print(f"    📁 [DEBUG] 输出文件: {output_file}")
        
        try:
            # 1. 创建任务
            print(f"    🚀 [DEBUG] 创建讯飞TTS任务...")
            create_result = self.create_task(text)
            
            if not create_result:
                print(f"    ❌ [DEBUG] 创建任务失败")
                return False
            
            code = create_result.get('header', {}).get('code')
            if code != 0:
                message = create_result.get('header', {}).get('message', f"错误码: {code}")
                print(f"    ❌ [DEBUG] 创建任务失败: {message}")
                return False
            
            task_id = create_result.get('header', {}).get('task_id')
            print(f"    ✅ [DEBUG] 任务创建成功，task_id: {task_id}")
            
            # 2. 查询任务状态
            print(f"    🔍 [DEBUG] 查询任务状态...")
            for i in range(15):  # 最多查询15次
                time.sleep(1)  # 等待1秒
                
                query_result = self.query_task(task_id)
                if not query_result:
                    print(f"    ❌ [DEBUG] 查询任务失败")
                    return False
                
                code = query_result.get('header', {}).get('code')
                if code != 0:
                    message = query_result.get('header', {}).get('message', f"错误码: {code}")
                    print(f"    ❌ [DEBUG] 查询任务失败: {message}")
                    return False
                
                task_status = query_result.get('header', {}).get('task_status')
                print(f"    📊 [DEBUG] 第{i+1}次查询，任务状态: {task_status}")
                
                if task_status == '5':  # 任务完成
                    audio_b64 = query_result.get('payload', {}).get('audio', {}).get('audio')
                    if audio_b64:
                        # 解码获取下载链接
                        download_url = base64.b64decode(audio_b64).decode()
                        print(f"    🔗 [DEBUG] 获取下载链接: {download_url[:100]}...")
                        
                        # 3. 下载音频文件
                        if self._download_audio(download_url, output_file):
                            print(f"    ✅ [DEBUG] 讯飞TTS合成成功")
                            print(f"    🎵 [DEBUG] 使用引擎: 讯飞TTS (HTTP API)")
                            return True
                        else:
                            print(f"    ❌ [DEBUG] 音频下载失败")
                            return False
                    else:
                        print(f"    ❌ [DEBUG] 响应中没有音频数据")
                        return False
                elif task_status in ['2']:  # 任务失败
                    print(f"    ❌ [DEBUG] 任务处理失败")
                    return False
                # 其他状态继续等待
            
            print(f"    ⏰ [DEBUG] 任务查询超时")
            return False
            
        except Exception as e:
            print(f"    ❌ [DEBUG] 讯飞TTS异常: {e}")
            return False
    
    def _download_audio(self, url, output_file):
        """下载音频文件"""
        try:
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            print(f"    📥 [DEBUG] 正在下载音频...")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # 确保输出目录存在
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 保存文件
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                # 检查文件大小
                file_size = os.path.getsize(output_file)
                print(f"    📊 [DEBUG] 音频文件大小: {file_size} 字节")
                
                if file_size > 1000:  # 至少1KB
                    return True
                else:
                    print(f"    ⚠️ [DEBUG] 下载的文件太小")
                    return False
            else:
                print(f"    ❌ [DEBUG] 下载失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    ❌ [DEBUG] 下载音频时出错: {e}")
            return False

    def _save_pcm_as_wav(self, pcm_data, output_file):
        """将PCM数据保存为WAV文件，如果目标是mp3则尝试转换"""
        try:
            import wave
            import struct
            
            # WAV文件参数
            channels = 1      # 单声道
            sample_width = 2  # 16位 = 2字节
            framerate = 16000 # 16kHz采样率
            
            # 确保输出目录存在
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果目标文件是mp3，先保存为临时wav文件
            if str(output_file).endswith('.mp3'):
                temp_wav = str(output_file).replace('.mp3', '_temp.wav')
                
                # 创建临时WAV文件
                with wave.open(temp_wav, 'wb') as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(sample_width)
                    wav_file.setframerate(framerate)
                    wav_file.writeframes(pcm_data)
                
                # 尝试转换为MP3
                if self._convert_wav_to_mp3(temp_wav, str(output_file)):
                    # 删除临时WAV文件
                    try:
                        os.remove(temp_wav)
                    except:
                        pass
                    return True
                else:
                    # 转换失败，重命名WAV文件为mp3（保持兼容性）
                    print(f"    ⚠️ [DEBUG] MP3转换失败，保存为WAV格式但保持.mp3扩展名")
                    try:
                        os.rename(temp_wav, str(output_file))
                        return True
                    except:
                        # 如果重命名失败，直接保存为wav格式
                        with wave.open(str(output_path), 'wb') as wav_file:
                            wav_file.setnchannels(channels)
                            wav_file.setsampwidth(sample_width)
                            wav_file.setframerate(framerate)
                            wav_file.writeframes(pcm_data)
                        return True
            else:
                # 直接保存为WAV文件
                with wave.open(str(output_path), 'wb') as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(sample_width)
                    wav_file.setframerate(framerate)
                    wav_file.writeframes(pcm_data)
                return True
            
        except Exception as e:
            print(f"    ❌ [DEBUG] PCM转WAV失败: {e}")
            # 降级保存原始PCM数据
            try:
                with open(output_file, 'wb') as f:
                    f.write(pcm_data)
                print(f"    📁 [DEBUG] 保存为原始PCM数据: {output_file}")
                return True
            except Exception as e2:
                print(f"    ❌ [DEBUG] 保存PCM数据也失败: {e2}")
                return False

    def _convert_wav_to_mp3(self, wav_file, mp3_file):
        """将WAV文件转换为MP3格式"""
        try:
            # 尝试使用ffmpeg转换
            cmd = [
                "ffmpeg", 
                "-i", wav_file,
                "-acodec", "libmp3lame",
                "-ab", "128k",
                "-ar", "16000",  # 保持采样率
                "-ac", "1",      # 单声道
                "-y",            # 覆盖输出文件
                mp3_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(mp3_file):
                print(f"    ✅ [DEBUG] 成功转换为MP3格式")
                return True
            else:
                print(f"    ❌ [DEBUG] ffmpeg转换失败: {result.stderr.decode() if result.stderr else 'Unknown error'}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"    ⏰ [DEBUG] ffmpeg转换超时")
            return False
        except FileNotFoundError:
            print(f"    ❌ [DEBUG] ffmpeg未安装或不可用")
            return False
        except Exception as e:
            print(f"    ❌ [DEBUG] 音频转换异常: {e}")
            return False


class FishAudioTTS:
    """Fish Audio语音合成"""
    
    def __init__(self):
        self.available = FISH_AUDIO_AVAILABLE
        if self.available:
            try:
                from fish_audio_sdk import Session, TTSRequest
                self.Session = Session
                self.TTSRequest = TTSRequest
                # 检查是否有API key配置
                self.api_key = os.getenv("FISH_AUDIO_API_KEY")
                if not self.api_key:
                    print("⚠️ Fish Audio API key未配置，将跳过Fish Audio")
                    self.available = False
            except ImportError:
                self.available = False

    def synthesize_to_file(self, text, output_file, timeout=15):
        """使用Fish Audio合成语音"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"    🔍 [DEBUG {timestamp}] Fish Audio TTS开始合成")
        print(f"    📝 [DEBUG] 输入文本: {repr(text[:50])}...")
        print(f"    📁 [DEBUG] 输出文件: {output_file}")
        
        if not self.available:
            print(f"    ❌ [DEBUG] Fish Audio不可用，跳过")
            return False
            
        try:
            if self.api_key:
                print(f"    🔑 [DEBUG] 使用配置的API Key")
                session = self.Session(api_key=self.api_key)
            else:
                print(f"    🔑 [DEBUG] 使用默认配置")
                session = self.Session()  # 尝试使用默认配置
            
            request = self.TTSRequest(text=text)
            print(f"    🚀 [DEBUG] 发送Fish Audio请求...")
            audio_data = session.tts(request)
            
            if audio_data:
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                file_size = os.path.getsize(output_file)
                print(f"    ✅ [DEBUG] Fish Audio合成成功: {file_size} 字节")
                print(f"    🎵 [DEBUG] 使用引擎: Fish Audio")
                return True
            else:
                print(f"    ❌ [DEBUG] Fish Audio返回空数据")
                return False
            
        except Exception as e:
            print(f"    ❌ [DEBUG] Fish Audio TTS失败: {e}")
            return False


class SystemTTS:
    """系统语音合成（macOS say命令）"""
    
    def synthesize_to_file(self, text, output_file, timeout=20):
        """使用系统语音合成"""
        try:
            # 确保输出目录存在
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成临时文件
            temp_file = str(output_path).replace('.mp3', '_temp.aiff')
            
            # 使用macOS的say命令
            cmd = [
                "say", 
                "-v", "Tingting",  # 中文语音
                "-r", "200",       # 语速
                "-o", temp_file,   # 输出文件
                text
            ]
            
            print(f"    ├─ 系统语音命令: {' '.join(cmd[:4])}...")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0 and os.path.exists(temp_file):
                # 检查文件大小
                file_size = os.path.getsize(temp_file)
                if file_size > 1000:  # 至少1KB
                    # 尝试转换为mp3格式
                    if self._convert_to_mp3(temp_file, str(output_path)):
                        return True
                    else:
                        # 如果转换失败，重命名为aiff格式保留
                        aiff_output = str(output_path).replace('.mp3', '.aiff')
                        os.rename(temp_file, aiff_output)
                        print(f"    ├─ 保存为AIFF格式: {aiff_output}")
                        return True
                else:
                    print(f"    ├─ 生成的文件太小: {file_size} bytes")
            else:
                print(f"    ├─ say命令失败: {result.stderr}")
            
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return False
            
        except Exception as e:
            print(f"    ├─ 系统语音合成失败: {e}")
            return False
    
    def _convert_to_mp3(self, input_file, output_file):
        """转换音频格式为MP3"""
        try:
            # 尝试使用ffmpeg转换
            cmd = [
                "ffmpeg", 
                "-i", input_file,
                "-acodec", "libmp3lame",
                "-ab", "128k",
                "-y",  # 覆盖输出文件
                output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                # 删除临时文件
                os.remove(input_file)
                return True
            else:
                print(f"    ├─ ffmpeg转换失败，保留原格式")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"    ├─ ffmpeg不可用，保留AIFF格式")
            return False
        except Exception as e:
            print(f"    ├─ 音频转换异常: {e}")
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
            ("讯飞TTS", self.xunfei_tts, 30),     # 30秒超时（HTTP API需要更长时间）
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
        
        for i, slide in enumerate(slides):
            # 添加延迟，避免API调用过于频繁
            if i > 0:
                time.sleep(0.5)
                
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


def test_xunfei_tts():
    """测试讯飞TTS功能"""
    print("🧪 测试讯飞TTS功能...")
    
    # 创建测试实例
    tts = WebSocketXunfeiTTS()
    
    # 测试文本
    test_text = "这是一个测试文本，用来验证讯飞语音合成是否正常工作。"
    output_file = "test_xunfei.wav"
    
    print(f"📝 测试文本: {test_text}")
    print(f"📁 输出文件: {output_file}")
    
    # 执行合成
    success = tts.synthesize_to_file(test_text, output_file, timeout=15)
    
    if success and os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ 讯飞TTS测试成功！文件大小: {file_size} 字节")
        return True
    else:
        print(f"❌ 讯飞TTS测试失败")
        return False


def main():
    """测试函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python reliable_voice_generator.py <html_file> [audio_prefix]  # 处理HTML文件")
        print("  python reliable_voice_generator.py --test                       # 测试讯飞TTS")
        return
    
    if sys.argv[1] == "--test":
        test_xunfei_tts()
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
