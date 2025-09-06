def generate_standard_html_template(final_book_title, slides_html, narration_data_js, total_slides):
    """生成标准风格的完整HTML模板"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{final_book_title} - Bookagent 智能演示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            font-family: "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, 
                #667eea 0%, 
                #764ba2 25%, 
                #f093fb 50%, 
                #f5576c 75%, 
                #4facfe 100%);
            background-size: 400% 400%;
            animation: gradientShift 10s ease infinite;
            min-height: 100vh;
            overflow: hidden;
            color: #333;
        }}

        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        .presentation-container {{
            display: flex;
            height: 100vh;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}

        .nav-sidebar {{
            width: 250px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .logo-section {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}

        .logo-title {{
            font-size: 24px;
            font-weight: bold;
            color: white;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .nav-button {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px 20px;
            color: white;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: center;
            font-size: 16px;
            font-weight: 500;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }}

        .nav-button:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }}

        .nav-button.playing {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .slide-counter {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            color: white;
            font-size: 14px;
            margin-top: auto;
        }}

        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .slide-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
        }}

        .slide {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 60px;
            max-width: 900px;
            width: 100%;
            min-height: 600px;
            display: none;
            flex-direction: column;
            justify-content: center;
            position: relative;
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .slide.active {{
            display: flex;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        .slide h1 {{
            font-size: 2.5em;
            margin-bottom: 30px;
            color: #2c3e50;
            text-align: center;
            line-height: 1.3;
            font-weight: 600;
        }}

        .slide h2 {{
            font-size: 2em;
            margin-bottom: 25px;
            color: #34495e;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        .slide p {{
            font-size: 1.2em;
            line-height: 1.8;
            margin-bottom: 20px;
            color: #555;
            text-align: justify;
        }}

        .slide ul {{
            margin: 20px 0;
            padding-left: 30px;
        }}

        .slide li {{
            font-size: 1.1em;
            line-height: 1.7;
            margin-bottom: 12px;
            color: #666;
        }}

        .nav-right {{
            width: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .nav-arrow {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: white;
            font-size: 20px;
            margin: 0 auto;
        }}

        .nav-arrow:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }}

        .nav-arrow:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }}

        .narration-display {{
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            color: #FFD700;
            padding: 25px 40px;
            text-align: center;
            font-size: 18px;
            line-height: 1.6;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }}

        .sentence {{
            opacity: 0;
            transition: opacity 0.8s ease-in-out;
            font-weight: 500;
        }}

        .sentence.active {{
            opacity: 1;
        }}

        @media (max-width: 1024px) {{
            .nav-sidebar {{
                width: 200px;
            }}
            
            .slide {{
                padding: 40px;
                max-width: 700px;
            }}
        }}

        @media (max-width: 768px) {{
            .presentation-container {{
                flex-direction: column;
            }}
            
            .nav-sidebar {{
                width: 100%;
                height: auto;
                flex-direction: row;
                justify-content: space-around;
                padding: 15px;
            }}
            
            .nav-right {{
                width: 100%;
                flex-direction: row;
                justify-content: center;
                height: auto;
                padding: 15px;
            }}
            
            .slide {{
                padding: 30px;
                margin: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <div class="nav-sidebar">
            <div class="logo-section">
                <div class="logo-title">Bookagent</div>
            </div>
            
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