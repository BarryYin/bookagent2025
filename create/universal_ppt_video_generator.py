#!/usr/bin/env python3
"""
通用PPT视频生成器
支持任意HTML PPT文件的视频生成
只需要修改配置部分即可
"""
import os
import sys
import time
import subprocess
from pathlib import Path
import tempfile
from datetime import datetime
import re
import html

# 可选：用于分析截图亮度，自动选择字幕黑/白色
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class UniversalPPTVideoGenerator:
    def __init__(self, html_file, audio_prefix="slide"):
        """
        初始化视频生成器
        :param html_file: HTML PPT文件路径（可以是相对路径或绝对路径）
        :param audio_prefix: 音频文件前缀 (如 "slide" 或 "musk_slide")
        """
        self.html_file = html_file
        self.audio_prefix = audio_prefix
        self.audio_dir = Path("./ppt_audio")
        self.output_dir = Path("./videos")
        self.temp_dir = Path("./temp_ppt_assets")
        self.slides_data = []
        
        # 从HTML文件名推断输出文件名前缀
        html_path = Path(html_file)
        self.output_prefix = html_path.stem.replace("PPT演示", "PPT").replace("presentation", "PPT")
        
        # 创建目录
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        print(f"🎯 目标文件: {self.html_file}")
        print(f"🎵 音频前缀: {self.audio_prefix}")
        print(f"📁 输出前缀: {self.output_prefix}")
        print(f"🎵 音频目录: {self.audio_dir}")
        print(f"📁 输出目录: {self.output_dir}")

    def check_dependencies(self):
        """检查系统依赖"""
        print("🔍 检查系统工具...")
        
        # 检查FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            print("✅ FFmpeg 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ FFmpeg 未安装或不在PATH中")
            return False
        
        # 检查Chrome
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_found = True
                break
        
        if chrome_found:
            print("✅ Chrome 可用")
        else:
            print("❌ Chrome 未找到")
            return False
            
        print("✅ 依赖检查通过")
        return True

    def parse_html_content(self):
        """解析HTML文件，提取幻灯片内容"""
        print("📄 解析HTML文件，提取语音内容...")
        
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式提取幻灯片
            slide_pattern = r'<div[^>]*class[^>]*slide[^>]*data-speech="([^"]*)"[^>]*>'
            slides = re.findall(slide_pattern, content)
            
            # 如果没找到data-speech，尝试其他方法
            if not slides:
                # 寻找所有class包含slide的div
                div_pattern = r'<div[^>]*class[^>]*slide[^>]*>(.*?)</div>'
                slide_contents = re.findall(div_pattern, content, re.DOTALL)
                slides = []
                for slide_content in slide_contents:
                    # 提取文本内容（简单去除HTML标签）
                    text_content = re.sub(r'<[^>]+>', '', slide_content)
                    text_content = text_content.strip()[:100]
                    slides.append(text_content)
            
            self.slides_data = []
            
            for i, speech_text in enumerate(slides):
                # 估算持续时间（每字0.15秒，最少5秒）
                duration = max(5.0, len(speech_text) * 0.15)
                
                self.slides_data.append({
                    "index": i,
                    "narration": speech_text,
                    "duration": duration
                })
                
                print(f"📄 第{i+1}页: {speech_text[:50]}... ({duration:.1f}秒)")
            
            print(f"📊 发现 {len(self.slides_data)} 页幻灯片的语音内容")
            return len(self.slides_data) > 0
            
        except Exception as e:
            print(f"❌ 解析HTML失败: {e}")
            return False

    def capture_ppt_screenshots(self):
        """使用Chrome无头模式截取每页PPT画面"""
        print("📸 开始截取PPT页面画面...")
        
        html_path = Path(self.html_file).absolute()
        slide_count = len(self.slides_data)
        
        for i in range(slide_count):
            print(f"📷 截取第 {i+1}/{slide_count} 页...")
            
            screenshot_path = self.temp_dir / f"slide_{i+1:03d}.png"
            
            # 创建临时HTML文件，自动显示指定的幻灯片
            success = self.take_chrome_screenshot(html_path, i, screenshot_path)
            
            if success:
                self.slides_data[i]['screenshot'] = screenshot_path
                print(f"   ✅ 截图成功: {screenshot_path.name}")
            else:
                print(f"   ❌ 截图失败: 第{i+1}页")
                return False
        
        return True

    def take_chrome_screenshot(self, html_path, slide_index, output_path, max_retries=3):
        """使用Chrome headless截图，只截取PPT内容区域"""
        for attempt in range(max_retries):
            try:
                # 创建临时HTML文件，自动显示指定的幻灯片，并优化为视频导出
                temp_html_content = f"""
                <style>
                /* 完全隐藏所有非PPT内容 */
                .nav-sidebar,
                .navigation,
                .speech-indicator,
                .subtitle-container,
                .subtitle-controls,
                .theme-selector,
                .slide-counter,
                .control-panel,
                .header,
                .footer,
                .sidebar {{ display: none !important; visibility: hidden !important; }}
                
                /* 重置所有容器样式，确保PPT内容占满全屏 */
                * {{
                    box-sizing: border-box !important;
                }}
                
                html, body {{
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    background: white !important;
                    overflow: hidden !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                }}
                
                .presentation-container {{
                    display: block !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    background: white !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    position: relative !important;
                }}
                
                .main-content {{
                    width: 100vw !important;
                    height: 100vh !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    background: white !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                }}
                
                .slide-container {{
                    width: 100vw !important;
                    height: 100vh !important;
                    background: white !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                }}
                
                .slide {{
                    width: 90vw !important;
                    height: 90vh !important;
                    max-width: 1200px !important;
                    background: white !important;
                    padding: 3rem !important;
                    box-sizing: border-box !important;
                    display: flex !important;
                    flex-direction: column !important;
                    justify-content: center !important;
                    align-items: center !important;
                    text-align: center !important;
                    border-radius: 0 !important;
                    box-shadow: none !important;
                }}
                
                .slide.active {{
                    display: flex !important;
                }}
                
                .slide:not(.active) {{
                    display: none !important;
                }}
                
                /* 优化文字样式，确保清晰可读 */
                .slide h1 {{
                    color: #1D1D1F !important;
                    font-size: 3.5rem !important;
                    font-weight: 700 !important;
                    margin: 0 0 2rem 0 !important;
                    line-height: 1.2 !important;
                    text-shadow: none !important;
                }}
                
                .slide h2 {{
                    color: #1D1D1F !important;
                    font-size: 2.5rem !important;
                    font-weight: 600 !important;
                    margin: 0 0 1.5rem 0 !important;
                    line-height: 1.3 !important;
                    text-shadow: none !important;
                }}
                
                .slide h3 {{
                    color: #1D1D1F !important;
                    font-size: 2rem !important;
                    font-weight: 500 !important;
                    margin: 0 0 1rem 0 !important;
                    line-height: 1.4 !important;
                    text-shadow: none !important;
                }}
                
                .slide p, .slide div, .slide li {{
                    color: #333 !important;
                    font-size: 1.5rem !important;
                    line-height: 1.6 !important;
                    margin: 0.5rem 0 !important;
                    text-shadow: none !important;
                }}
                
                .slide ul, .slide ol {{
                    text-align: left !important;
                    max-width: 800px !important;
                    margin: 1rem auto !important;
                }}
                
                /* 确保图片和其他元素也适配 */
                .slide img {{
                    max-width: 100% !important;
                    height: auto !important;
                    margin: 1rem 0 !important;
                }}
                </style>
                <script>
                // 禁用所有confirm和alert对话框
                window.confirm = function() {{ return false; }};
                window.alert = function() {{}};
                
                setTimeout(function() {{
                    // 强制隐藏所有可能的导航元素
                    const elementsToHide = [
                        '.nav-sidebar', '.navigation', '.speech-indicator',
                        '.subtitle-container', '.subtitle-controls', '.theme-selector',
                        '.slide-counter', '.control-panel', '.header', '.footer', '.sidebar'
                    ];
                    
                    elementsToHide.forEach(selector => {{
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {{
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                            el.style.opacity = '0';
                        }});
                    }});
                    
                    // 调整主内容区域
                    const mainContent = document.querySelector('.main-content');
                    if (mainContent) {{
                        mainContent.style.width = '100vw';
                        mainContent.style.height = '100vh';
                        mainContent.style.marginLeft = '0';
                        mainContent.style.marginTop = '0';
                        mainContent.style.padding = '0';
                    }}
                    
                    // 显示指定的幻灯片
                    if (typeof showSlide === 'function') {{
                        showSlide({slide_index});
                        console.log('显示第{slide_index + 1}页幻灯片');
                    }} else {{
                        // 如果没有showSlide函数，尝试其他方法
                        const slides = document.querySelectorAll('.slide');
                        if (slides.length > {slide_index}) {{
                            slides.forEach((s, idx) => {{
                                if (idx === {slide_index}) {{
                                    s.classList.add('active');
                                    s.style.display = 'flex';
                                }} else {{
                                    s.classList.remove('active');
                                    s.style.display = 'none';
                                }}
                            }});
                        }}
                    }}
                    
                    // 确保页面完全加载后再截图
                    console.log('PPT页面准备完成，可以截图');
                }}, 5000);  // 增加等待时间确保样式完全应用
                </script>
                """
                
                # 读取原HTML文件
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 在</body>前插入脚本
                modified_html = html_content.replace('</body>', temp_html_content + '</body>')
                
                # 创建临时文件
                temp_html_path = self.temp_dir / f"temp_slide_{slide_index}.html"
                with open(temp_html_path, 'w', encoding='utf-8') as f:
                    f.write(modified_html)
                
                temp_url = f"file://{temp_html_path.absolute()}"
                
                # Chrome headless命令 - 优化截图参数，确保只截取内容区域
                cmd = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--headless",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-background-networking",
                    "--window-size=1920,1080",  # 16:9 标准分辨率
                    "--force-device-scale-factor=1",  # 使用1倍缩放确保清晰度
                    "--screenshot=" + str(output_path),
                    "--virtual-time-budget=20000",  # 增加到20秒确保完全加载
                    "--run-all-compositor-stages-before-draw",  # 确保渲染完成
                    "--disable-background-timer-throttling",  # 禁用后台限制
                    temp_url
                ]
                
                # 启动Chrome进程
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # 等待截图完成
                process.wait(timeout=45)  # 增加超时时间到45秒确保完全渲染
                
                # 检查截图是否成功
                if output_path.exists() and output_path.stat().st_size > 1000:
                    # 清理临时HTML文件
                    if temp_html_path.exists():
                        temp_html_path.unlink()
                    return True
                else:
                    print(f"   ⚠️  截图文件异常，重试 {attempt+1}/{max_retries}")
                    if output_path.exists():
                        output_path.unlink()
                    
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  Chrome超时，重试 {attempt+1}/{max_retries}")
                if 'process' in locals():
                    process.kill()
            except Exception as e:
                print(f"   ⚠️  Chrome截图失败: {e}, 重试 {attempt+1}/{max_retries}")
            finally:
                # 清理临时HTML文件
                if 'temp_html_path' in locals() and temp_html_path.exists():
                    temp_html_path.unlink()
        
        return False

    def create_slide_video(self, slide_data):
        """创建单页视频（带字幕）"""
        print(f"🎬 生成视频: 第{slide_data['index']+1}页")
        
        # 检查截图是否存在
        if 'screenshot' not in slide_data or not slide_data['screenshot'].exists():
            print(f"   ❌ 截图文件不存在")
            return False
        
        # 检查是否有现成的音频文件
        audio_file = self.audio_dir / f"{self.audio_prefix}_{slide_data['index']+1:02d}.mp3"
        
        if audio_file.exists():
            # 使用现有的音频文件
            audio_path = audio_file
            print(f"   🔊 使用现有音频: {audio_file.name}")
        else:
            # 生成新音频
            audio_path = self.temp_dir / f"audio_{slide_data['index']:03d}.aac"
            if not self.generate_audio(slide_data['narration'], audio_path, slide_data['duration']):
                return False
            print(f"   🎤 生成新音频: {audio_path.name}")
        
        # 生成带字幕的视频
        video_path = self.temp_dir / f"video_{slide_data['index']:03d}.mp4"

        # 准备字幕文本（限制长度避免过长，去除换行避免超出）
        raw_text = slide_data['narration']
        raw_text = raw_text.replace('\n', ' ').replace('\r', ' ').strip()
        subtitle_text = raw_text[:100] if len(raw_text) > 100 else raw_text

        # 写入临时字幕文本文件，避免 ffmpeg drawtext 转义问题
        subtitle_txt_path = self.temp_dir / f"subtitle_{slide_data['index']:03d}.txt"
        try:
            with open(subtitle_txt_path, 'w', encoding='utf-8') as tf:
                tf.write(subtitle_text)
        except Exception as e:
            print(f"   ⚠️ 写入字幕文本失败，将直接内联文本: {e}")
            subtitle_txt_path = None

        # 自动选择字幕颜色（默认白字+黑描边），需要 PIL 可用
        font_color = 'white'
        border_color = 'black'
        try:
            if PIL_AVAILABLE and 'screenshot' in slide_data and slide_data['screenshot'].exists():
                img = Image.open(slide_data['screenshot']).convert('L')
                w, h = img.size
                # 取底部 15% 区域
                crop_h = max(1, int(h * 0.15))
                bottom = img.crop((0, h - crop_h, w, h))
                # 降采样提高速度
                bottom_small = bottom.resize((max(1, w // 20), max(1, crop_h // 20)))
                # 计算平均亮度
                pixels = list(bottom_small.getdata())
                avg_luma = sum(pixels) / len(pixels)
                # 阈值：亮背景用黑字，暗背景用白字
                if avg_luma >= 160:
                    font_color, border_color = 'black', 'white'
                else:
                    font_color, border_color = 'white', 'black'
        except Exception as e:
            print(f"   ⚠️ 自动选择字幕颜色失败，使用默认白字: {e}")

        # 构造 drawtext 过滤器（无底色框，保留描边与阴影，提高可读性）
        text_source = (
            f"textfile='{subtitle_txt_path}'" if subtitle_txt_path else f"text='{subtitle_text}'"
        )
        drawtext = (
            f"drawtext={text_source}:fontfile=/System/Library/Fonts/PingFang.ttc:"
            f"fontsize=36:fontcolor={font_color}:x=(w-text_w)/2:y=h-th-80:"
            f"borderw=2:bordercolor={border_color}:shadowcolor=black@0.5:shadowx=2:shadowy=2"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(slide_data['screenshot']),
            "-i", str(audio_path),
            "-vf", drawtext,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and video_path.exists():
                slide_data['video'] = video_path
                print(f"   ✅ 视频片段生成成功（带字幕）")
                return True
            else:
                print(f"   ❌ 视频生成失败: {result.stderr}")
                # 如果字幕失败，尝试不加字幕的版本
                print(f"   🔄 尝试生成无字幕版本...")
                return self.create_slide_video_no_subtitle(slide_data)
        except Exception as e:
            print(f"   ❌ 视频生成异常: {e}")
            # 如果字幕失败，尝试不加字幕的版本
            print(f"   🔄 尝试生成无字幕版本...")
            return self.create_slide_video_no_subtitle(slide_data)

    def create_slide_video_no_subtitle(self, slide_data):
        """创建无字幕的视频（备用方案）"""
        audio_file = self.audio_dir / f"{self.audio_prefix}_{slide_data['index']+1:02d}.mp3"
        
        if audio_file.exists():
            audio_path = audio_file
        else:
            audio_path = self.temp_dir / f"audio_{slide_data['index']:03d}.aac"
        
        video_path = self.temp_dir / f"video_{slide_data['index']:03d}.mp4"
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(slide_data['screenshot']),
            "-i", str(audio_path),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and video_path.exists():
                slide_data['video'] = video_path
                print(f"   ✅ 视频片段生成成功（无字幕）")
                return True
            else:
                print(f"   ❌ 无字幕视频生成失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ 无字幕视频生成异常: {e}")
            return False

    def generate_audio(self, text, output_path, duration):
        """生成语音音频"""
        try:
            # 使用系统TTS生成音频
            cmd = ["say", "-v", "Tingting", "-o", str(output_path.with_suffix('.aiff')), text]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                # 转换为AAC格式
                convert_cmd = [
                    "ffmpeg", "-y", "-i", str(output_path.with_suffix('.aiff')),
                    "-c:a", "aac", "-b:a", "128k", str(output_path)
                ]
                convert_result = subprocess.run(convert_cmd, capture_output=True)
                
                # 清理临时文件
                if output_path.with_suffix('.aiff').exists():
                    output_path.with_suffix('.aiff').unlink()
                
                return convert_result.returncode == 0
            return False
            
        except Exception as e:
            print(f"   ❌ 音频生成失败: {e}")
            return False

    def merge_videos(self, video_files, output_path):
        """合并视频文件"""
        print("🔗 合并视频片段...")
        
        # 创建文件列表
        file_list_path = self.temp_dir / "video_list.txt"
        with open(file_list_path, 'w') as f:
            for video_file in video_files:
                f.write(f"file '{video_file.absolute()}'\n")
        
        # 合并视频
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(file_list_path),
            "-c", "copy", str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 视频合并成功")
                return True
            else:
                print(f"❌ 视频合并失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 视频合并异常: {e}")
            return False

    def cleanup(self):
        """清理临时文件"""
        print("🗑️  清理临时文件...")
        if self.temp_dir.exists():
            for file in self.temp_dir.iterdir():
                try:
                    file.unlink()
                except:
                    pass

    def generate_video(self):
        """生成完整视频"""
        # 解析HTML内容
        if not self.parse_html_content():
            return False
        
        # 截取PPT画面
        if not self.capture_ppt_screenshots():
            return False
        
        # 生成各页视频
        video_files = []
        for slide_data in self.slides_data:
            if self.create_slide_video(slide_data):
                video_files.append(slide_data['video'])
            else:
                return False
        
        # 合并视频
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        final_output = self.output_dir / f"{self.output_prefix}_截图版_{timestamp}.mp4"
        
        if not self.merge_videos(video_files, final_output):
            self.cleanup()
            return False
        
        # 清理临时文件
        self.cleanup()
        
        # 检查结果
        if final_output.exists():
            return final_output
        else:
            return False

def main():
    """主函数"""
    print("📸 通用PPT视频生成工具")
    print("=" * 50)
    
    # ================== 配置区域 ==================
    # 只需要修改这两行即可切换不同的PPT
    
    # 白鹿原配置
    # html_file = "白鹿原PPT演示.html"
    # audio_prefix = "slide"
    
    # 《高效人士的7个习惯》配置
    html_file = "高效人士的7个习惯PPT演示.html"
    audio_prefix = "habit_slide"
    
    # ================== 配置区域结束 ==================
    
    try:
        # 创建生成器实例
        generator = UniversalPPTVideoGenerator(html_file, audio_prefix)
        
        # 检查依赖
        if not generator.check_dependencies():
            return
        
        # 生成视频
        result = generator.generate_video()
        
        if result:
            print(f"\n🎉 视频生成完成！")
            file_size = result.stat().st_size / (1024 * 1024)  # MB
            print(f"📁 文件: {result}")
            print(f"📊 大小: {file_size:.1f} MB")
            
            # 获取视频时长
            try:
                duration_result = subprocess.run([
                    "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                    "-of", "csv=p=0", str(result)
                ], capture_output=True, text=True)
                if duration_result.returncode == 0:
                    duration = float(duration_result.stdout.strip())
                    print(f"⏱️  时长: {duration:.1f} 秒")
            except:
                pass
                
            print(f"📄 页数: {len(generator.slides_data)} 页")
            
            # 打开视频
            try:
                subprocess.run(["open", str(result)])
                print("📺 视频已自动打开")
            except:
                print("📺 请手动打开视频文件")
        else:
            print("\n❌ 视频生成失败")
            
    except KeyboardInterrupt:
        print("\n👋 用户取消")
        if 'generator' in locals():
            generator.cleanup()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if 'generator' in locals():
            generator.cleanup()

if __name__ == "__main__":
    main()
