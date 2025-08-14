#!/usr/bin/env python3
"""
通用 PPT 配音工具
从 HTML 文件中提取 data-speech 文本并生成配音到 ppt_audio/
优先使用 Fish Audio（如安装并配置），否则回退到 macOS 系统语音（say）
用法: python ppt_voice_generator.py <html_file> <audio_prefix>
默认: html_file=高效人士的7个习惯PPT演示.html, audio_prefix=habit_slide
"""

import os
import sys
import re
import json
import time
import subprocess
from pathlib import Path
import importlib


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


BS4_AVAILABLE = _module_available('bs4')
FISH_AUDIO_AVAILABLE = _module_available('fish_audio_sdk')


class PPTVoiceGenerator:
    def __init__(self, html_file: str = "高效人士的7个习惯PPT演示.html", audio_prefix: str = "habit_slide"):
        self.html_file = html_file
        self.audio_prefix = audio_prefix
        self.audio_dir = Path("./ppt_audio")
        self.audio_dir.mkdir(exist_ok=True)

        # Fish Audio 配置（可由环境变量覆盖）
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
                self.fish_session = None
        else:
            print("⚠️ 未检测到 fish_audio_sdk，将使用系统语音")

    def extract_speech_texts(self):
        """从 HTML 中提取所有 data-speech 内容"""
        try:
            content = Path(self.html_file).read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ 读取 HTML 失败: {e}")
            return []

        speech_texts = []
        try:
            if BS4_AVAILABLE:
                bs4_mod = importlib.import_module('bs4')
                BeautifulSoup = bs4_mod.BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                slides = soup.find_all(attrs={'data-speech': True})
                for i, slide in enumerate(slides, start=1):
                    speech_text = (slide.get('data-speech') or '').strip()
                    if speech_text:
                        speech_texts.append({'index': i, 'title': f'第{i}页', 'text': speech_text})
            else:
                # 正则回退方案
                matches = re.findall(r'data-speech="([\s\S]*?)"', content)
                for i, t in enumerate(matches, start=1):
                    t = (t or '').strip()
                    if t:
                        speech_texts.append({'index': i, 'title': f'第{i}页', 'text': t})
        except Exception as e:
            print(f"❌ 解析 HTML 失败: {e}")
            return []

        print(f"✅ 提取到 {len(speech_texts)} 页配音文本")
        return speech_texts

    def _try_fish_audio(self, text: str, output_file: Path) -> bool:
        if not self.fish_session or not self._fish_mod:
            return False
        try:
            print("🔄 使用 Fish Audio 生成语音…")
            with open(output_file, 'wb') as f:
                req = self._fish_mod.TTSRequest(
                    reference_id=self.fish_reference_id,
                    text=text,
                    backend="s1",
                )
                for chunk in self.fish_session.tts(req):
                    f.write(chunk)
            return output_file.exists() and output_file.stat().st_size > 0
        except Exception as e:
            print(f"❌ Fish Audio 生成失败: {e}")
            return False

    def _generate_system_audio(self, text: str, output_file: Path) -> str | None:
        try:
            aiff = self.audio_dir / "temp_tts.aiff"
            # 生成 AIFF
            r = subprocess.run(["say", "-v", "Tingting", "-r", "160", "-o", str(aiff), text],
                               capture_output=True, text=True)
            if r.returncode != 0 or not aiff.exists():
                return None
            # 转 MP3
            r2 = subprocess.run([
                "ffmpeg", "-y", "-i", str(aiff),
                "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", str(output_file)
            ], capture_output=True)
            try:
                if aiff.exists():
                    aiff.unlink()
            finally:
                pass
            if r2.returncode == 0 and output_file.exists():
                return str(output_file)
            return None
        except Exception as e:
            print(f"❌ 系统语音生成失败: {e}")
            return None

    def get_audio_duration(self, audio_file: Path) -> float:
        try:
            p = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(audio_file)
            ], capture_output=True, text=True)
            if p.returncode == 0:
                info = json.loads(p.stdout)
                return float(info.get('format', {}).get('duration', 0.0))
        except Exception:
            pass
        return 0.0

    def generate_audio_for_slide(self, slide: dict, use_fish_audio: bool = True) -> str | None:
        index = slide['index']
        text = slide['text']
        out = self.audio_dir / f"{self.audio_prefix}_{index:02d}.mp3"

        print(f"🎵 第{index}页: {min(len(text), 80)} 字")
        if use_fish_audio and self.fish_session:
            if self._try_fish_audio(text, out):
                print(f"✅ Fish Audio: {out.name}")
                return str(out)
            else:
                print("🔁 Fish Audio 失败，改用系统语音…")
        return self._generate_system_audio(text, out)

    def generate_all_audio(self) -> list[dict]:
        print("=" * 60)
        print("🎵 PPT 配音生成器")
        print("=" * 60)
        print(f"📄 HTML: {self.html_file}")
        print(f"🔖 前缀: {self.audio_prefix}")

        slides = self.extract_speech_texts()
        if not slides:
            print("❌ 没有配音文本")
            return []

        results: list[dict] = []
        total = 0.0
        for slide in slides:
            audio_path = self.generate_audio_for_slide(slide, use_fish_audio=True)
            if audio_path:
                dur = self.get_audio_duration(audio_path)
                total += dur
                results.append({
                    'index': slide['index'],
                    'title': slide['title'],
                    'audio_file': audio_path,
                    'duration': dur,
                    'text_preview': (slide['text'][:50] + '...') if len(slide['text']) > 50 else slide['text']
                })
            else:
                print(f"❌ 第{slide['index']}页 生成失败")
            print("-" * 40)

        print("\n📊 统计")
        print(f"✅ 成功: {len(results)}/{len(slides)} 页")
        print(f"⏱️ 总时长: {total:.1f} 秒 (≈{total/60:.1f} 分钟)")
        print(f"📁 输出目录: {self.audio_dir}")
        return results

    def create_playlist(self, generated: list[dict]) -> str:
        stem = Path(self.html_file).stem
        m3u = self.audio_dir / f"{stem}配音列表.m3u"
        with open(m3u, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"# {stem} 配音列表 - {len(generated)} 个文件\n\n")
            for item in generated:
                dur = int(item.get('duration') or 0)
                title = item.get('title') or ''
                name = Path(item['audio_file']).name
                f.write(f"#EXTINF:{dur},{title}\n{name}\n")
        print(f"📝 播放列表: {m3u}")
        return str(m3u)


def main():
    html_file = sys.argv[1] if len(sys.argv) > 1 else "高效人士的7个习惯PPT演示.html"
    audio_prefix = sys.argv[2] if len(sys.argv) > 2 else "habit_slide"
    gen = PPTVoiceGenerator(html_file, audio_prefix)

    if not Path(gen.html_file).exists():
        print(f"❌ 找不到 HTML 文件: {gen.html_file}")
        sys.exit(1)

    generated = gen.generate_all_audio()
    if generated:
        gen.create_playlist(generated)
        print("\n🎉 完成！可在 ppt_audio 目录查看")
        print(f"📱 可用播放列表: {Path(gen.html_file).stem}配音列表.m3u")
        sys.exit(0)
    else:
        print("❌ 未生成任何音频")
        sys.exit(2)


if __name__ == "__main__":
    main()
