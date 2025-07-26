#!/usr/bin/env python3
"""
生成简单但完整的PPT HTML
"""

def generate_simple_ppt_html(topic, slides_data, narrations_data):
    """生成简单但完整的PPT HTML"""
    
    # 确保slides_data是列表
    if not isinstance(slides_data, list):
        slides_data = [
            {"title": f"{topic}", "subtitle": "开场", "content": "欢迎"},
            {"title": "内容", "subtitle": "主要内容", "content": "核心观点"},
            {"title": "总结", "subtitle": "结束", "content": "谢谢"}
        ]
    
    # 确保narrations_data是列表
    if not isinstance(narrations_data, list):
        narrations_data = [
            f"欢迎来到《{topic}》的介绍",
            f"这是关于《{topic}》的主要内容",
            f"感谢您观看《{topic}》的介绍"
        ]
    
    # 生成幻灯片HTML
    slides_html = ""
    for i, slide in enumerate(slides_data):
        active_class = "active" if i == 0 else ""
        slides_html += f'''
        <div class="slide {active_class}" data-slide="{i}">
            <h1>{slide.get('title', f'第{i+1}页')}</h1>
            <h2>{slide.get('subtitle', '')}</h2>
            <p>{slide.get('content', '')}</p>
        </div>'''
    
    # 生成解说词JavaScript数组
    narrations_js = "[\n"
    for narration in narrations_data:
        narrations_js += f'        "{narration}",\n'
    narrations_js += "    ]"
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - PPT演示</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
            background: #FFFFFF;
            color: #1D1D1F;
            overflow: hidden;
        }}
        
        .presentation-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }}
        
        .slide {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            padding: 40px;
            box-sizing: border-box;
            text-align: center;
        }}
        
        .slide.active {{
            opacity: 1;
            transform: translateX(0);
        }}
        
        .slide h1 {{
            font-size: 4rem;
            font-weight: 300;
            margin-bottom: 20px;
            color: #1D1D1F;
        }}
        
        .slide h2 {{
            font-size: 2rem;
            font-weight: 400;
            color: #86868B;
            margin-bottom: 30px;
        }}
        
        .slide p {{
            font-size: 1.5rem;
            line-height: 1.6;
            max-width: 800px;
            color: #1D1D1F;
        }}
        
        .navigation {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            z-index: 1000;
        }}
        
        .navigation button {{
            background-color: #007AFF;
            color: #FFFFFF;
            border: none;
            padding: 12px 24px;
            margin: 0 15px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .navigation button:hover {{
            background-color: #0056b3;
            transform: translateY(-2px);
        }}
        
        .navigation button:disabled {{
            background-color: #86868B;
            cursor: not-allowed;
            transform: none;
        }}
        
        .dots {{
            display: flex;
            margin: 0 20px;
        }}
        
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.5);
            margin: 0 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .dot.active {{
            background-color: #007AFF;
            transform: scale(1.2);
        }}
        
        .narration-panel {{
            position: fixed;
            top: 30px;
            right: 30px;
            width: 350px;
            background-color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            font-size: 1rem;
            line-height: 1.5;
            color: #1D1D1F;
            z-index: 1000;
        }}
        
        .slide-counter {{
            position: fixed;
            top: 30px;
            left: 30px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 1rem;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="presentation-container">{slides_html}
    </div>
    
    <div class="slide-counter">
        <span id="currentSlideNum">1</span> / <span id="totalSlideNum">{len(slides_data)}</span>
    </div>
    
    <div class="navigation">
        <button id="prevButton" onclick="prevSlide()">← 上一页</button>
        <div class="dots" id="dotsContainer"></div>
        <button id="nextButton" onclick="nextSlide()">下一页 →</button>
    </div>
    
    <div class="narration-panel" id="narrationPanel">
        <strong>解说词：</strong><br>
        {narrations_data[0] if narrations_data else '欢迎观看PPT演示'}
    </div>
    
    <script>
        // 解说词数据
        const narrations = {narrations_js};
        
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        const dotsContainer = document.getElementById('dotsContainer');
        const prevButton = document.getElementById('prevButton');
        const nextButton = document.getElementById('nextButton');
        const narrationPanel = document.getElementById('narrationPanel');
        const currentSlideNum = document.getElementById('currentSlideNum');
        const totalSlideNum = document.getElementById('totalSlideNum');
        
        // 初始化
        totalSlideNum.textContent = totalSlides;
        
        // 生成导航点
        for (let i = 0; i < totalSlides; i++) {{
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', () => showSlide(i));
            dotsContainer.appendChild(dot);
        }}
        
        function showSlide(n) {{
            // 边界检查
            if (n < 0 || n >= totalSlides) return;
            
            // 移除所有活动状态
            slides.forEach(slide => slide.classList.remove('active'));
            
            // 设置当前页面
            slides[n].classList.add('active');
            currentSlide = n;
            
            // 更新UI
            updateNarration(n);
            updateDots(n);
            updateNavigationButtons();
            updateSlideCounter(n);
        }}
        
        function nextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                showSlide(currentSlide + 1);
            }}
        }}
        
        function prevSlide() {{
            if (currentSlide > 0) {{
                showSlide(currentSlide - 1);
            }}
        }}
        
        function updateNavigationButtons() {{
            prevButton.disabled = currentSlide === 0;
            nextButton.disabled = currentSlide === totalSlides - 1;
        }}
        
        function updateDots(n) {{
            const dots = document.querySelectorAll('.dot');
            dots.forEach((dot, index) => {{
                dot.classList.toggle('active', index === n);
            }});
        }}
        
        function updateNarration(slideIndex) {{
            if (narrations[slideIndex]) {{
                narrationPanel.innerHTML = `<strong>解说词：</strong><br>${{narrations[slideIndex]}}`;
            }}
        }}
        
        function updateSlideCounter(n) {{
            currentSlideNum.textContent = n + 1;
        }}
        
        // 键盘导航
        document.addEventListener('keydown', (e) => {{
            switch(e.key) {{
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    nextSlide();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    prevSlide();
                    break;
                case 'Home':
                    e.preventDefault();
                    showSlide(0);
                    break;
                case 'End':
                    e.preventDefault();
                    showSlide(totalSlides - 1);
                    break;
            }}
        }});
        
        // 初始化显示
        updateNavigationButtons();
        console.log('PPT初始化完成，共', totalSlides, '页');
    </script>
</body>
</html>'''
    
    return html_template

if __name__ == "__main__":
    # 测试生成
    html = generate_simple_ppt_html(
        "测试书籍",
        [
            {"title": "测试书籍", "subtitle": "开场介绍", "content": "欢迎来到测试"},
            {"title": "主要内容", "subtitle": "核心观点", "content": "这是主要内容"},
            {"title": "总结", "subtitle": "结束语", "content": "谢谢观看"}
        ],
        [
            "欢迎来到测试书籍的介绍",
            "这里是主要内容的解说",
            "感谢您的观看"
        ]
    )
    
    with open('simple_ppt_test.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("简单PPT已生成: simple_ppt_test.html")
    print(f"HTML长度: {len(html)} 字符")
    print("✅ HTML结构完整" if html.strip().endswith('</html>') else "❌ HTML结构不完整")