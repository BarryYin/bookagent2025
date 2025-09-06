#!/usr/bin/env python3
"""
测试新的三种完全不同的PPT布局
"""
import json

# 测试数据
test_slides = [
    {"title": "小王子", "content": "欢迎来到《小王子》的精彩解读"},
    {"title": "作者介绍", "content": "安东尼·德·圣-埃克苏佩里，法国作家和飞行员"},
    {"title": "核心主题", "content": ["成长与纯真", "友谊与爱情", "责任与担当"]},
    {"title": "经典语录", "content": "真正重要的东西，用眼睛是看不见的"},
    {"title": "现实意义", "content": "在成人世界中保持童心的重要性"}
]

test_narrations = [
    "欢迎大家，今天我们来分享《小王子》这部经典作品",
    "让我们先了解一下这位传奇作家的人生经历", 
    "这本书探讨了许多深刻的人生主题",
    "书中有许多令人难忘的经典语句",
    "最后让我们思考这本书对现代人的启发意义"
]

test_book_data = {
    "title": "小王子",
    "author": "安东尼·德·圣-埃克苏佩里"
}

def generate_new_layout_html(slides, narrations, book_data, book_title, video_style):
    """生成新的布局HTML"""
    
    # 处理幻灯片数据
    processed_slides = []
    for slide in slides:
        processed_slides.append({
            'title': slide.get('title', ''),
            'content': slide.get('content', '')
        })
    
    # 根据视频风格生成完全不同的幻灯片布局
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        narration_text = narrations[i] if i < len(narrations) else ""
        narration_text = str(narration_text).replace('"', '&quot;').replace('\n', ' ').replace('\r', '')
        
        if i == 0:
            # 首页 - 三种完全不同的布局
            if video_style == "storytelling":
                slides_html += f'''
                    <div class="slide {active_class}" data-speech="{narration_text}">
                        <div style="display: flex; height: 100%; align-items: center;">
                            <div style="flex: 1; padding: 2rem;">
                                <div style="background: linear-gradient(45deg, #8B4513, #D2691E); padding: 3rem; border-radius: 50px; text-align: center; box-shadow: 0 20px 40px rgba(139,69,19,0.3); position: relative; overflow: hidden;">
                                    <div style="position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; animation: float 6s ease-in-out infinite;"></div>
                                    <div style="position: absolute; bottom: -30px; left: -30px; width: 80px; height: 80px; background: rgba(255,255,255,0.1); border-radius: 50%; animation: float 8s ease-in-out infinite reverse;"></div>
                                    <h1 style="font-size: 3rem; color: #FFF8DC; margin-bottom: 1rem; font-family: 'Georgia', serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); position: relative; z-index: 2;">{book_title}</h1>
                                    <div style="width: 60px; height: 4px; background: #FFD700; margin: 1.5rem auto; border-radius: 2px; position: relative; z-index: 2;"></div>
                                    <p style="font-size: 1.2rem; color: #FFF8DC; font-style: italic; position: relative; z-index: 2;">📚 一段温暖的阅读旅程</p>
                                </div>
                            </div>
                        </div>
                    </div>'''
            elif video_style == "modern_presentation":
                slides_html += f'''
                    <div class="slide {active_class}" data-speech="{narration_text}">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; height: 100%; gap: 2rem; padding: 2rem;">
                            <div style="display: flex; flex-direction: column; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 3rem; position: relative; overflow: hidden;">
                                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: url('data:image/svg+xml,<svg xmlns=\\"http://www.w3.org/2000/svg\\" viewBox=\\"0 0 100 100\\"><defs><pattern id=\\"grid\\" width=\\"10\\" height=\\"10\\" patternUnits=\\"userSpaceOnUse\\"><path d=\\"M 10 0 L 0 0 0 10\\" fill=\\"none\\" stroke=\\"%23ffffff\\" stroke-width=\\"0.5\\" opacity=\\"0.1\\"/></pattern></defs><rect width=\\"100\\" height=\\"100\\" fill=\\"url(%23grid)\\"/></svg>'); opacity: 0.3;"></div>
                                <h1 style="font-size: 3.5rem; color: white; margin-bottom: 1rem; font-weight: 900; position: relative; z-index: 2; text-transform: uppercase; letter-spacing: 2px;">{book_title}</h1>
                                <div style="width: 100px; height: 6px; background: linear-gradient(90deg, #FF6B6B, #4ECDC4); margin-bottom: 1rem; position: relative; z-index: 2;"></div>
                                <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; position: relative; z-index: 2;">🚀 NEXT-GEN KNOWLEDGE</p>
                            </div>
                            <div style="display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.05); border-radius: 20px; border: 2px solid rgba(255,255,255,0.1);">
                                <div style="text-align: center; padding: 2rem;">
                                    <div style="width: 120px; height: 120px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border-radius: 50%; margin: 0 auto 2rem; display: flex; align-items: center; justify-content: center; font-size: 3rem; animation: pulse 2s infinite;">📚</div>
                                    <p style="color: white; font-size: 1.2rem; opacity: 0.8;">Interactive Reading Experience</p>
                                </div>
                            </div>
                        </div>
                    </div>'''
            else:  # classic_ppt
                slides_html += f'''
                    <div class="slide {active_class}" data-speech="{narration_text}">
                        <div style="padding: 4rem; text-align: center; background: linear-gradient(to bottom, #f8f9fa, #ffffff); border: 3px solid #1565C0; border-radius: 15px; margin: 2rem;">
                            <div style="background: #1565C0; color: white; padding: 1rem 2rem; border-radius: 8px; display: inline-block; margin-bottom: 2rem; box-shadow: 0 4px 8px rgba(21,101,192,0.3);">
                                <h1 style="font-size: 2.5rem; margin: 0; font-weight: 600;">{book_title}</h1>
                            </div>
                            <div style="border-top: 3px solid #1565C0; border-bottom: 3px solid #1565C0; padding: 2rem; margin: 2rem 0; background: rgba(21,101,192,0.05);">
                                <p style="font-size: 1.3rem; color: #37474F; margin: 0; font-weight: 500;">📚 Professional Book Analysis</p>
                            </div>
                            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;">
                                <div style="width: 60px; height: 60px; background: #1565C0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">📖</div>
                                <div style="width: 60px; height: 60px; background: #1565C0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">💡</div>
                                <div style="width: 60px; height: 60px; background: #1565C0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">🎯</div>
                            </div>
                        </div>
                    </div>'''
        else:
            # 内容页 - 三种完全不同的布局
            content = slide.get('content', '')
            title = slide.get('title', f'第{i+1}页')
            
            if video_style == "storytelling":
                # 故事书风格 - 左右分栏，像翻开的书页
                if isinstance(content, list):
                    content_html = '<div style="display: grid; gap: 1rem;">'
                    for idx, item in enumerate(content):
                        content_html += f'<div style="background: linear-gradient(135deg, #FFF8DC, #F5DEB3); padding: 1.5rem; border-radius: 15px; border-left: 5px solid #D2691E; box-shadow: 0 4px 8px rgba(0,0,0,0.1); position: relative;"><div style="position: absolute; top: 10px; right: 15px; color: #D2691E; font-size: 1.5rem;">📝</div><p style="margin: 0; color: #8B4513; font-size: 1.1rem; line-height: 1.6;">{str(item)}</p></div>'
                    content_html += '</div>'
                else:
                    content_html = f'<div style="background: linear-gradient(135deg, #FFF8DC, #F5DEB3); padding: 2rem; border-radius: 20px; border: 2px solid #D2691E; box-shadow: 0 8px 16px rgba(0,0,0,0.1); position: relative;"><div style="position: absolute; top: -10px; left: 20px; background: #D2691E; color: white; padding: 0.5rem 1rem; border-radius: 15px; font-size: 0.9rem;">Story</div><p style="color: #8B4513; font-size: 1.2rem; line-height: 1.8; margin: 1rem 0 0 0; font-family: Georgia, serif;">{str(content).replace(chr(10), "<br>")}</p></div>'
                
                slides_html += f'''
                    <div class="slide {active_class}" data-speech="{narration_text}">
                        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; height: 100%; padding: 2rem;">
                            <div style="background: linear-gradient(45deg, #8B4513, #D2691E); border-radius: 20px; padding: 2rem; display: flex; flex-direction: column; justify-content: center; text-align: center; box-shadow: 0 10px 20px rgba(139,69,19,0.3);">
                                <h2 style="color: #FFF8DC; font-size: 2rem; margin-bottom: 1rem; font-family: Georgia, serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{title}</h2>
                                <div style="width: 50px; height: 3px; background: #FFD700; margin: 0 auto;"></div>
                            </div>
                            <div style="display: flex; align-items: center;">
                                {content_html}
                            </div>
                        </div>
                    </div>'''
                    
            elif video_style == "modern_presentation":
                # 现代科技风格 - 卡片式布局
                if isinstance(content, list):
                    content_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">'
                    for idx, item in enumerate(content):
                        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                        color = colors[idx % len(colors)]
                        content_html += f'<div style="background: linear-gradient(135deg, {color}, {color}dd); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; transform: translateY(0); transition: transform 0.3s ease; box-shadow: 0 8px 16px rgba(0,0,0,0.1);" onmouseover="this.style.transform=\'translateY(-5px)\'" onmouseout="this.style.transform=\'translateY(0)\';"><div style="font-size: 2rem; margin-bottom: 1rem;">{["🚀", "💡", "⚡", "🎯", "✨"][idx % 5]}</div><p style="margin: 0; font-weight: 500; font-size: 1rem;">{str(item)}</p></div>'
                    content_html += '</div>'
                else:
                    content_html = f'<div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); padding: 2rem; border-radius: 20px; border: 1px solid rgba(102,126,234,0.2); backdrop-filter: blur(10px);"><p style="color: #2c3e50; font-size: 1.2rem; line-height: 1.7; margin: 0;">{str(content).replace(chr(10), "<br>")}</p></div>'
                
                slides_html += f'''
                    <div class="slide {active_class}" data-speech="{narration_text}">
                        <div style="padding: 2rem; height: 100%;">
                            <div style="text-align: center; margin-bottom: 2rem;">
                                <h2 style="font-size: 2.5rem; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px;">{title}</h2>
                                <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 0 auto; border-radius: 2px;"></div>
                            </div>
                            <div style="display: flex; align-items: center; justify-content: center; min-height: 60%;">
                                {content_html}
                            </div>
                        </div>
                    </div>'''
                    
            else:  # classic_ppt
                # 经典商务风格 - 表格式布局
                if isinstance(content, list):
                    content_html = '<div style="background: white; border: 2px solid #1565C0; border-radius: 10px; overflow: hidden;">'
                    for idx, item in enumerate(content):
                        bg_color = '#f8f9fa' if idx % 2 == 0 else 'white'
                        content_html += f'<div style="padding: 1rem 1.5rem; border-bottom: 1px solid #e9ecef; background: {bg_color}; display: flex; align-items: center;"><div style="width: 30px; height: 30px; background: #1565C0; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold; font-size: 0.9rem;">{idx + 1}</div><p style="margin: 0; color: #37474F; font-size: 1rem;">{str(item)}</p></div>'
                    content_html += '</div>'
                else:
                    content_html = f'<div style="background: white; border: 2px solid #1565C0; border-radius: 10px; padding: 2rem;"><p style="color: #37474F; font-size: 1.1rem; line-height: 1.6; margin: 0; text-align: justify;">{str(content).replace(chr(10), "<br>")}</p></div>'
                
                slides_html += f'''
                    <div class="slide {active_class}" data-speech="{narration_text}">
                        <div style="padding: 2rem; height: 100%;">
                            <div style="background: #1565C0; color: white; padding: 1rem 2rem; border-radius: 8px; margin-bottom: 2rem; text-align: center;">
                                <h2 style="margin: 0; font-size: 2rem; font-weight: 600;">{title}</h2>
                            </div>
                            <div style="display: flex; align-items: center; justify-content: center; min-height: 70%;">
                                {content_html}
                            </div>
                        </div>
                    </div>'''

    # 根据视频风格生成不同的背景样式
    def get_background_style(style):
        if style == "storytelling":
            return "background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 25%, #FFCC80 50%, #FFB74D 75%, #FF9800 100%);"
        elif style == "modern_presentation":
            return "background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 25%, #90CAF9 50%, #64B5F6 75%, #2196F3 100%);"
        else:  # classic_ppt
            return "background: linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 25%, #BDBDBD 50%, #9E9E9E 75%, #757575 100%);"
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title} - 新布局演示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            font-family: "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            {get_background_style(video_style)}
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

        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-20px);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                transform: scale(1);
            }}
            50% {{
                transform: scale(1.05);
            }}
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
        }}

        .logo-title {{
            font-size: 24px;
            font-weight: bold;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }}

        .nav-button {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px 20px;
            color: white;
            cursor: pointer;
            text-align: center;
            font-size: 16px;
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
        }}

        .slide-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .slide {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            width: 100%;
            height: 100%;
            display: none;
            position: relative;
        }}

        .slide.active {{
            display: block;
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
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: white;
            font-size: 20px;
            margin: 0 auto;
        }}

        .narration-display {{
            background: rgba(0, 0, 0, 0.8);
            color: #FFD700;
            padding: 25px 40px;
            text-align: center;
            font-size: 18px;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <div class="nav-sidebar">
            <div class="logo-title">新布局演示</div>
            <button class="nav-button">🎨 {video_style}</button>
            <div class="slide-counter">
                <div>第 1 页 / {len(processed_slides)} 页</div>
            </div>
        </div>

        <div class="main-content">
            <div class="slide-container">
                {slides_html}
            </div>
            <div class="narration-display">
                <div>新的{video_style}布局风格演示</div>
            </div>
        </div>

        <div class="nav-right">
            <button class="nav-arrow" onclick="prevSlide()">❮</button>
            <button class="nav-arrow" onclick="nextSlide()">❯</button>
        </div>
    </div>

    <script>
        let currentSlide = 0;
        let totalSlides = {len(processed_slides)};

        function nextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                currentSlide++;
                showSlide(currentSlide);
            }}
        }}

        function prevSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
                showSlide(currentSlide);
            }}
        }}

        function showSlide(slideIndex) {{
            const slides = document.querySelectorAll('.slide');
            slides.forEach(slide => slide.classList.remove('active'));
            if (slides[slideIndex]) {{
                slides[slideIndex].classList.add('active');
            }}
        }}

        document.addEventListener('keydown', function(event) {{
            if (event.key === 'ArrowLeft') {{
                prevSlide();
            }} else if (event.key === 'ArrowRight') {{
                nextSlide();
            }}
        }});
    </script>
</body>
</html>'''
    
    return html_template

def test_new_layouts():
    """测试新的三种布局"""
    print("🚀 开始测试全新的三种PPT布局...")
    
    styles = [
        ("经典商务", "classic_ppt"),
        ("故事叙述", "storytelling"), 
        ("现代演示", "modern_presentation")
    ]
    
    for style_name, video_style in styles:
        print(f"\n=== 生成 {style_name} 新布局 ===")
        
        try:
            html_content = generate_new_layout_html(
                test_slides, 
                test_narrations, 
                test_book_data, 
                "小王子",
                video_style
            )
            
            filename = f"new_layout_{video_style}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ {style_name} 新布局生成成功")
            print(f"📁 文件保存为: {filename}")
            print(f"📏 HTML长度: {len(html_content)} 字符")
            
        except Exception as e:
            print(f"❌ {style_name} 新布局生成失败: {e}")
    
    print(f"\n🎉 新布局测试完成！")
    print("💡 现在三种风格有完全不同的布局结构：")
    print("   📊 经典商务：表格式布局，标题栏+内容区")
    print("   📖 故事叙述：左右分栏布局，像翻开的书页")
    print("   🚀 现代演示：网格卡片布局，科技感十足")

if __name__ == "__main__":
    test_new_layouts()