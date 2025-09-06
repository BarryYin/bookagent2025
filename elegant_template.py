def generate_elegant_art_template(final_book_title, slides_html, narration_data_js, total_slides):
    """生成优雅艺术风格的完整HTML模板"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{final_book_title} - 优雅艺术演示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            font-family: "Playfair Display", "Times New Roman", Georgia, serif;
            background: linear-gradient(135deg, #F8F6F0 0%, #E8E2D5 25%, #D4C4A8 50%, #C9B037 75%, #B8860B 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            overflow: hidden;
            color: #2C1810;
        }}

        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        @keyframes elegantFloat {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-15px) rotate(1deg); }}
        }}

        .presentation-container {{
            display: flex;
            height: 100vh;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}

        .nav-sidebar {{
            width: 250px;
            background: rgba(248, 246, 240, 0.9);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-right: 2px solid rgba(184, 134, 11, 0.3);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .logo-title {{
            font-size: 26px;
            font-weight: 400;
            color: #B8860B;
            text-align: center;
            margin-bottom: 2rem;
            font-style: italic;
        }}

        .nav-button {{
            background: linear-gradient(45deg, #F8F6F0, #E8E2D5);
            border: 2px solid #B8860B;
            border-radius: 25px;
            padding: 15px 20px;
            color: #B8860B;
            cursor: pointer;
            text-align: center;
            font-size: 16px;
            font-weight: 500;
            font-style: italic;
            transition: all 0.4s ease;
        }}

        .nav-button:hover {{
            background: linear-gradient(45deg, #B8860B, #C9B037);
            color: #F8F6F0;
            transform: translateY(-3px);
        }}

        .slide-counter {{
            background: rgba(248, 246, 240, 0.8);
            border: 1px solid #B8860B;
            border-radius: 15px;
            padding: 12px;
            text-align: center;
            color: #B8860B;
            font-size: 14px;
            margin-top: auto;
            font-style: italic;
        }}

        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}

        .slide-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .slide {{
            background: rgba(248, 246, 240, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 30px;
            box-shadow: 0 25px 70px rgba(44, 24, 16, 0.15);
            border: 3px solid rgba(184, 134, 11, 0.3);
            width: 100%;
            height: 100%;
            display: none;
            position: relative;
            overflow: hidden;
        }}

        .slide.active {{
            display: block;
            animation: elegantFloat 8s ease-in-out infinite;
        }}

        .nav-right {{
            width: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: rgba(248, 246, 240, 0.9);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-left: 2px solid rgba(184, 134, 11, 0.3);
        }}

        .nav-arrow {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(45deg, #F8F6F0, #E8E2D5);
            border: 2px solid #B8860B;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: #B8860B;
            font-size: 24px;
            margin: 0 auto;
            transition: all 0.4s ease;
        }}

        .nav-arrow:hover {{
            background: linear-gradient(45deg, #B8860B, #C9B037);
            color: #F8F6F0;
            transform: scale(1.1);
        }}

        .narration-display {{
            background: linear-gradient(90deg, #2C1810, #3D2817);
            color: #F8F6F0;
            padding: 25px 40px;
            text-align: center;
            font-size: 18px;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-top: 2px solid rgba(184, 134, 11, 0.3);
            font-style: italic;
            font-weight: 400;
        }}

        .ornament {{
            position: absolute;
            background: rgba(184, 134, 11, 0.1);
            border-radius: 50%;
        }}

        .ornament-1 {{
            width: 150px;
            height: 150px;
            top: -75px;
            right: -75px;
            animation: elegantFloat 12s ease-in-out infinite;
        }}

        .ornament-2 {{
            width: 100px;
            height: 100px;
            bottom: -50px;
            left: -50px;
            animation: elegantFloat 10s ease-in-out infinite reverse;
        }}

        .gold-accent {{
            background: linear-gradient(45deg, #B8860B, #C9B037, #DAA520);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <div class="nav-sidebar">
            <div class="logo-title">优雅艺术</div>
            
            <button id="playPauseButton" class="nav-button" onclick="toggleAudio()">
                🔊 播放解说
            </button>
            
            <button id="exportVideoButton" class="nav-button" onclick="exportVideo()" style="background: rgba(255, 200, 100, 0.2); margin-top: 10px;">
                🎬 导出视频
            </button>
            
            <button id="backButton" class="nav-button" onclick="goBack()" style="background: rgba(255, 255, 255, 0.2);">
                ← 返回主页
            </button>
            
            <div class="slide-counter">
                <div id="slideCounter">第 1 页 / {total_slides} 页</div>
            </div>
        </div>

        <div class="main-content">
            <div class="slide-container">
                {slides_html}
            </div>

            <div class="narration-display">
                <div id="currentNarration">点击"播放解说"开始自动播放演示</div>
            </div>
        </div>

        <div class="nav-right">
            <button class="nav-arrow" id="prevBtn" onclick="prevSlide()">❮</button>
            <button class="nav-arrow" id="nextBtn" onclick="nextSlide()">❯</button>
        </div>
    </div>

    <audio id="audioPlayer" preload="auto"></audio>

    <script>
        // 全局变量
        let currentSlide = 0;
        let totalSlides = {total_slides};
        let isAutoPlaying = false;
        let isPlaying = false;
        let sentenceTimers = [];

        // 解说词数据
        const narrationData = {narration_data_js};

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            updateSlideCounter();
            updateNavigationButtons();
        }});

        // 音频播放功能
        function toggleAudio() {{
            const playPauseButton = document.getElementById('playPauseButton');
            
            if (isAutoPlaying) {{
                stopAutoPlay();
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }} else {{
                startAutoPlay();
                playPauseButton.textContent = '⏸️ 停止播放';
                playPauseButton.classList.add('playing');
            }}
        }}
        
        function startAutoPlay() {{
            isAutoPlaying = true;
            showSlide(currentSlide);
            playCurrentSlide();
        }}
        
        function stopAutoPlay() {{
            isAutoPlaying = false;
            isPlaying = false;
            const audioPlayer = document.getElementById('audioPlayer');
            if (audioPlayer) {{
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
            }}
            clearSentenceTimers();
            resetNarrationDisplay();
        }}
        
        function playCurrentSlide() {{
            if (!isAutoPlaying) return;
            
            const audioPlayer = document.getElementById('audioPlayer');
            const sessionId = window.location.pathname.split('/')[2];
            const slideNumber = (currentSlide + 1).toString().padStart(2, '0');
            const audioPath = `/ppt_audio/${{sessionId}}_slide_${{slideNumber}}.mp3`;
            
            audioPlayer.src = audioPath;
            audioPlayer.play().then(() => {{
                isPlaying = true;
                startSentenceDisplay();
            }}).catch((error) => {{
                console.error('音频播放失败:', error);
                startSentenceDisplay();
                setTimeout(() => {{
                    if (isAutoPlaying) {{
                        goToNextSlide();
                    }}
                }}, 5000);
            }});
        }}

        // 导航功能
        function nextSlide() {{
            if (isAutoPlaying) {{
                stopAutoPlay();
                const playPauseButton = document.getElementById('playPauseButton');
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }}
            goToNextSlide();
        }}
        
        function prevSlide() {{
            if (isAutoPlaying) {{
                stopAutoPlay();
                const playPauseButton = document.getElementById('playPauseButton');
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }}
            goToPrevSlide();
        }}
        
        function goToNextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                currentSlide++;
                showSlide(currentSlide);
                if (isAutoPlaying) {{
                    setTimeout(() => playCurrentSlide(), 500);
                }}
            }} else if (isAutoPlaying) {{
                stopAutoPlay();
                const playPauseButton = document.getElementById('playPauseButton');
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }}
        }}
        
        function goToPrevSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
                showSlide(currentSlide);
                if (isAutoPlaying) {{
                    setTimeout(() => playCurrentSlide(), 500);
                }}
            }}
        }}

        function showSlide(slideIndex) {{
            const slides = document.querySelectorAll('.slide');
            
            slides.forEach(slide => slide.classList.remove('active'));
            
            if (slides[slideIndex]) {{
                slides[slideIndex].classList.add('active');
                currentSlide = slideIndex;
            }}
            
            updateSlideCounter();
            updateNavigationButtons();
            if (!isAutoPlaying) {{
                resetNarrationDisplay();
            }}
        }}

        function updateSlideCounter() {{
            const counter = document.getElementById('slideCounter');
            if (counter) {{
                counter.textContent = `第 ${{currentSlide + 1}} 页 / ${{totalSlides}} 页`;
            }}
        }}

        function updateNavigationButtons() {{
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            if (prevBtn) {{
                prevBtn.disabled = currentSlide === 0;
            }}
            if (nextBtn) {{
                nextBtn.disabled = currentSlide === totalSlides - 1;
            }}
        }}

        // 字幕显示功能
        function startSentenceDisplay() {{
            const slideData = narrationData[currentSlide];
            if (!slideData) return;
            
            clearSentenceTimers();
            
            slideData.sentences.forEach((sentence, index) => {{
                const delay = slideData.timings[index] * 1000;
                const timer = setTimeout(() => {{
                    if (isAutoPlaying || isPlaying) {{
                        displaySentence(sentence);
                    }}
                }}, delay);
                sentenceTimers.push(timer);
            }});

            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.onended = () => {{
                if (isAutoPlaying) {{
                    setTimeout(() => goToNextSlide(), 1000);
                }}
            }};
        }}

        function displaySentence(sentence) {{
            const narrationDiv = document.getElementById('currentNarration');
            if (narrationDiv) {{
                narrationDiv.innerHTML = `<span class="sentence active">${{sentence}}</span>`;
            }}
        }}

        function clearSentenceTimers() {{
            sentenceTimers.forEach(timer => clearTimeout(timer));
            sentenceTimers = [];
        }}

        function resetNarrationDisplay() {{
            const narrationDiv = document.getElementById('currentNarration');
            if (narrationDiv) {{
                narrationDiv.innerHTML = '点击"播放解说"开始自动播放演示';
            }}
        }}

        // 键盘导航
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'ArrowLeft') {{
                prevSlide();
            }} else if (event.key === 'ArrowRight') {{
                nextSlide();
            }} else if (event.key === ' ') {{
                event.preventDefault();
                toggleAudio();
            }}
        }});

        // 返回主页功能
        function goBack() {{
            window.location.href = '/';
        }}

        // 导出视频功能
        function exportVideo() {{
            const exportButton = document.getElementById('exportVideoButton');
            const originalText = exportButton.innerHTML;
            
            const currentPath = window.location.pathname;
            const sessionId = currentPath.split('/')[2];
            const htmlFileName = 'presentation.html';
            
            exportButton.innerHTML = '⏳ 准备中...';
            exportButton.disabled = true;
            exportButton.style.opacity = '0.6';
            
            fetch('/api/export-video', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    session_id: sessionId,
                    html_file: htmlFileName,
                    audio_prefix: sessionId + '_slide'
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    if (data.cached) {{
                        exportButton.innerHTML = '✅ 使用缓存';
                        showVideoDownload(data);
                    }} else if (data.status === 'started') {{
                        exportButton.innerHTML = '🔄 生成中 (0%)';
                        pollVideoStatus(data.task_id, exportButton);
                        showNotification('✨ 视频生成已开始！您可以继续使用其他功能，完成后会自动通知您。', 'info');
                    }} else if (data.status === 'processing') {{
                        exportButton.innerHTML = '🔄 生成中...';
                        pollVideoStatus(data.task_id || sessionId + '_' + sessionId + '_slide', exportButton);
                    }}
                }} else {{
                    exportButton.innerHTML = '❌ 生成失败';
                    showNotification('视频生成失败: ' + data.error, 'error');
                    setTimeout(() => {{
                        exportButton.innerHTML = originalText;
                        exportButton.disabled = false;
                        exportButton.style.opacity = '1';
                    }}, 3000);
                }}
            }})
            .catch(error => {{
                console.error('导出视频错误:', error);
                exportButton.innerHTML = '❌ 请求失败';
                showNotification('网络请求失败，请检查网络连接', 'error');
                setTimeout(() => {{
                    exportButton.innerHTML = originalText;
                    exportButton.disabled = false;
                    exportButton.style.opacity = '1';
                }}, 3000);
            }});
        }}

        function pollVideoStatus(taskId, button) {{
            const poll = () => {{
                fetch(`/api/export-video-status/${{taskId}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'processing') {{
                        const progress = data.progress || 0;
                        button.innerHTML = `🔄 生成中 (${{progress}}%)`;
                        setTimeout(poll, 2000);
                    }} else if (data.status === 'completed') {{
                        button.innerHTML = '✅ 生成完成';
                        showVideoDownload(data);
                        showNotification('🎉 视频生成完成！', 'success');
                    }} else if (data.status === 'failed') {{
                        button.innerHTML = '❌ 生成失败';
                        showNotification('视频生成失败: ' + data.error, 'error');
                        setTimeout(() => {{
                            button.innerHTML = '🎬 导出视频';
                            button.disabled = false;
                            button.style.opacity = '1';
                        }}, 3000);
                    }}
                }})
                .catch(error => {{
                    console.error('轮询状态错误:', error);
                    button.innerHTML = '❌ 状态查询失败';
                    setTimeout(() => {{
                        button.innerHTML = '🎬 导出视频';
                        button.disabled = false;
                        button.style.opacity = '1';
                    }}, 3000);
                }});
            }};
            
            setTimeout(poll, 1000);
        }}

        function showVideoDownload(data) {{
            const downloadLink = document.createElement('a');
            downloadLink.href = data.video_url;
            downloadLink.download = data.filename;
            downloadLink.click();
            
            const infoDiv = document.createElement('div');
            infoDiv.style.marginTop = '10px';
            infoDiv.style.padding = '10px';
            infoDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';
            infoDiv.style.borderRadius = '8px';
            infoDiv.style.fontSize = '14px';
            infoDiv.innerHTML = `
                <div style="color: #4caf50; font-weight: bold;">📹 视频信息</div>
                <div>文件名: ${{data.filename}}</div>
                <div>大小: ${{data.file_size}}</div>
                <div>时长: ${{data.duration}}秒</div>
            `;
            
            const button = document.getElementById('exportVideoButton');
            button.parentNode.insertBefore(infoDiv, button.nextSibling);
            
            setTimeout(() => {{
                button.innerHTML = '🎬 导出视频';
                button.disabled = false;
                button.style.opacity = '1';
            }}, 3000);
        }}

        function showNotification(message, type = 'info') {{
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                animation: slideInFromRight 0.3s ease;
            `;
            
            if (type === 'success') {{
                notification.style.backgroundColor = '#4caf50';
            }} else if (type === 'error') {{
                notification.style.backgroundColor = '#f44336';
            }} else {{
                notification.style.backgroundColor = '#2196f3';
            }}
            
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.style.animation = 'slideOutToRight 0.3s ease';
                setTimeout(() => {{
                    if (notification.parentNode) {{
                        notification.parentNode.removeChild(notification);
                    }}
                }}, 300);
            }}, 5000);
            
            if (!document.getElementById('notification-styles')) {{
                const style = document.createElement('style');
                style.id = 'notification-styles';
                style.textContent = `
                    @keyframes slideInFromRight {{
                        from {{ transform: translateX(100%); opacity: 0; }}
                        to {{ transform: translateX(0); opacity: 1; }}
                    }}
                    @keyframes slideOutToRight {{
                        from {{ transform: translateX(0); opacity: 1; }}
                        to {{ transform: translateX(100%); opacity: 0; }}
                    }}
                `;
                document.head.appendChild(style);
            }}
        }}
    </script>
</body>
</html>'''