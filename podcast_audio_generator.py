#!/usr/bin/env python3
"""
播客音频生成器
基于播客脚本生成音频文件
"""
import os
import sys
import re
import json
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import importlib

# 添加create目录到路径
sys.path.append(str(Path(__file__).parent / "create"))

def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False

FISH_AUDIO_AVAILABLE = _module_available('fish_audio_sdk')

class PodcastAudioGenerator:
    """播客音频生成器"""
    
    def __init__(self):
        self.audio_dir = Path("./podcast_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
        # Fish Audio 配置
        self.fish_api_key = os.getenv("FISH_API_KEY", "8a3f82b04cdc4ae6bdd799953c45813b")
        self.fish_reference_id = os.getenv("FISH_REFERENCE_ID", "c7cbda1c101c4ce8906c046f01eca1a2")
        self._fish_mod = None
        self.fish_session = None
        
        if FISH_AUDIO_AVAILABLE:
            try:
                self._fish_mod = importlib.import_module('fish_audio_sdk')
                self.fish_session = self._fish_mod.Session(self.fish_api_key)
                print("✅ Fish Audio Session 初始化成功")
            except Exception as e:
                print(f"⚠️ Fish Audio Session 初始化失败: {e}")
    
    async def generate_podcast_audio(self, podcast_script: str, session_id: str) -> Dict[str, Any]:
        """生成播客音频"""
        try:
            # 解析播客脚本
            segments = self._parse_podcast_script(podcast_script)
            
            # 为每个片段生成音频
            audio_files = []
            total_duration = 0
            
            for i, segment in enumerate(segments):
                audio_file = await self._generate_segment_audio(
                    segment["content"], 
                    session_id, 
                    i,
                    segment["type"]
                )
                
                if audio_file:
                    audio_files.append({
                        "segment_type": segment["type"],
                        "audio_file": audio_file,
                        "duration": self._estimate_audio_duration(segment["content"])
                    })
                    total_duration += self._estimate_audio_duration(segment["content"])
            
            # 生成合并后的音频文件（如果需要）
            merged_audio_file = await self._merge_audio_files(audio_files, session_id)
            
            return {
                "session_id": session_id,
                "audio_files": audio_files,
                "merged_audio": merged_audio_file,
                "total_duration": total_duration,
                "generation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"播客音频生成失败: {e}")
            return {"error": str(e)}
    
    def _parse_podcast_script(self, script: str) -> List[Dict[str, Any]]:
        """解析播客脚本"""
        segments = []
        current_segment = {"type": "intro", "content": ""}
        
        lines = script.split('\n')
        for line in lines:
            line = line.strip()
            
            # 检查是否是片段标题
            if line.startswith('### '):
                if current_segment["content"].strip():
                    segments.append(current_segment)
                
                segment_type = line.replace('### ', '').lower()
                current_segment = {
                    "type": segment_type,
                    "content": ""
                }
            elif line and not line.startswith('#') and not line.startswith('```'):
                # 添加内容
                if current_segment["content"]:
                    current_segment["content"] += " "
                current_segment["content"] += line
        
        # 添加最后一个片段
        if current_segment["content"].strip():
            segments.append(current_segment)
        
        return segments
    
    async def _generate_segment_audio(self, text: str, session_id: str, segment_index: int, segment_type: str) -> Optional[str]:
        """为单个片段生成音频"""
        try:
            # 清理文本
            clean_text = self._clean_text(text)
            if not clean_text:
                return None
            
            # 生成文件名
            timestamp = int(time.time())
            audio_filename = f"{session_id}_segment_{segment_index}_{segment_type}.mp3"
            audio_path = self.audio_dir / audio_filename
            
            # 优先使用 Fish Audio
            if FISH_AUDIO_AVAILABLE and self.fish_session:
                return await self._generate_with_fish_audio(clean_text, audio_path)
            else:
                return await self._generate_with_system_tts(clean_text, audio_path)
                
        except Exception as e:
            print(f"片段音频生成失败: {e}")
            return None
    
    async def _generate_with_fish_audio(self, text: str, audio_path: Path) -> str:
        """使用 Fish Audio 生成音频"""
        try:
            # 分段生成（Fish Audio 有长度限制）
            max_length = 500
            if len(text) > max_length:
                chunks = self._split_text(text, max_length)
                temp_files = []
                
                for i, chunk in enumerate(chunks):
                    temp_file = audio_path.parent / f"{audio_path.stem}_part_{i}.mp3"
                    await self._generate_fish_audio_chunk(chunk, temp_file)
                    temp_files.append(temp_file)
                
                # 合并音频文件
                await self._merge_audio_files_list(temp_files, audio_path)
                
                # 清理临时文件
                for temp_file in temp_files:
                    if temp_file.exists():
                        temp_file.unlink()
                
                return str(audio_path)
            else:
                await self._generate_fish_audio_chunk(text, audio_path)
                return str(audio_path)
                
        except Exception as e:
            print(f"Fish Audio 生成失败: {e}")
            # 降级到系统 TTS
            return await self._generate_with_system_tts(text, audio_path)
    
    async def _generate_fish_audio_chunk(self, text: str, audio_path: Path):
        """生成 Fish Audio 音频片段"""
        try:
            # 使用 Fish Audio 生成语音
            result = self.fish_session.tts(
                text=text,
                reference_id=self.fish_reference_id,
                format="mp3",
                sample_rate=44100
            )
            
            # 保存音频文件
            with open(audio_path, "wb") as f:
                f.write(result)
            
            print(f"✅ Fish Audio 生成成功: {audio_path}")
            
        except Exception as e:
            print(f"Fish Audio 片段生成失败: {e}")
            raise
    
    async def _generate_with_system_tts(self, text: str, audio_path: Path) -> str:
        """使用系统 TTS 生成音频"""
        try:
            # 使用 macOS say 命令
            cmd = ['say', '-v', 'Tingting', '-o', str(audio_path.with_suffix('.aiff')), text]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 转换为 MP3 格式
            if audio_path.suffix == '.mp3':
                cmd = ['ffmpeg', '-i', str(audio_path.with_suffix('.aiff')), 
                       str(audio_path), '-y']
                subprocess.run(cmd, check=True, capture_output=True)
                audio_path.with_suffix('.aiff').unlink()
            
            print(f"✅ 系统 TTS 生成成功: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            print(f"系统 TTS 生成失败: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的标点符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：""''（）【】《》、]', '', text)
        # 移除多余的空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """分割长文本"""
        sentences = re.split(r'[。！？.!?]', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _estimate_audio_duration(self, text: str) -> int:
        """估算音频时长（秒）"""
        # 中文平均语速：每分钟 200-300 字
        chars_per_second = 4
        return max(1, len(text) // chars_per_second)
    
    async def _merge_audio_files(self, audio_files: List[Dict[str, Any]], session_id: str) -> Optional[str]:
        """合并所有音频文件"""
        try:
            if len(audio_files) <= 1:
                return None
            
            merged_filename = f"{session_id}_full_podcast.mp3"
            merged_path = self.audio_dir / merged_filename
            
            # 提取所有音频文件路径
            file_paths = [af["audio_file"] for af in audio_files if af["audio_file"]]
            
            if not file_paths:
                return None
            
            return await self._merge_audio_files_list([Path(fp) for fp in file_paths], merged_path)
            
        except Exception as e:
            print(f"音频文件合并失败: {e}")
            return None
    
    async def _merge_audio_files_list(self, input_files: List[Path], output_path: Path) -> Optional[str]:
        """合并音频文件列表"""
        try:
            if len(input_files) == 0:
                return None
            elif len(input_files) == 1:
                # 只有一个文件，直接复制
                import shutil
                shutil.copy2(input_files[0], output_path)
                return str(output_path)
            
            # 使用 ffmpeg 合并音频文件
            # 创建文件列表
            list_file = output_path.parent / f"{output_path.stem}_list.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for input_file in input_files:
                    f.write(f"file '{input_file.absolute()}'\n")
            
            # 使用 ffmpeg 合并
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', 
                '-i', str(list_file), '-c', 'copy', str(output_path), '-y'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 清理临时文件
            list_file.unlink()
            
            print(f"✅ 音频文件合并成功: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"音频文件合并失败: {e}")
            return None

# 全局播客音频生成器
podcast_audio_generator = PodcastAudioGenerator()

def get_podcast_audio_generator() -> PodcastAudioGenerator:
    """获取播客音频生成器实例"""
    return podcast_audio_generator

async def generate_podcast_audio(script: str, session_id: str) -> Dict[str, Any]:
    """生成播客音频的便捷函数"""
    generator = get_podcast_audio_generator()
    return await generator.generate_podcast_audio(script, session_id)