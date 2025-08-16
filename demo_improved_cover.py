# 测试改进后的默认封面效果

# 生成的默认封面CSS
default_cover_css = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"

# 完整的HTML模板
html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试默认封面效果</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1D1D1F;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            padding: 20px;
            box-sizing: border-box;
        }}
        
        h1 {{
            color: white;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .demo-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            width: 100%;
        }}
        
        .demo-title {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .demo-content {{
            font-size: 1.1rem;
            line-height: 1.6;
            color: #333;
            margin-bottom: 30px;
        }}
        
        /* 演示封面样式 */
        .cover-demo {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 40px;
            margin: 30px 0;
        }}
        
        .book-cover {{
            flex-shrink: 0;
            width: 200px;
            height: 280px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            transform: perspective(1000px) rotateY(-15deg);
            transition: transform 0.3s ease;
        }}
        
        .book-cover:hover {{
            transform: perspective(1000px) rotateY(-5deg) scale(1.05);
        }}
        
        /* 改进后的默认封面样式 */
        .default-cover {{
            background: {default_cover_css};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-radius: 12px;
        }}
        
        .default-cover::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }}
        
        .default-cover-icon {{
            font-size: 3.5rem;
            margin-bottom: 15px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            z-index: 1;
        }}
        
        .default-cover-title {{
            font-size: 1.3rem;
            line-height: 1.4;
            word-break: break-word;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            z-index: 1;
            max-width: 100%;
            padding: 0 5px;
            box-sizing: border-box;
        }}
        
        .default-cover-subtitle {{
            font-size: 0.9rem;
            margin-top: 8px;
            opacity: 0.9;
            z-index: 1;
        }}
        
        .code-block {{
            background: #2d2d2d;
            color: #f8f8f2;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        .improvements {{
            background: #e8f4ff;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .improvements h3 {{
            margin-top: 0;
            color: #2c5aa0;
        }}
        
        .improvements ul {{
            padding-left: 20px;
        }}
        
        .improvements li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 改进后的默认书籍封面效果演示</h1>
        
        <div class="demo-card">
            <div class="demo-title">默认封面改进效果</div>
            
            <div class="demo-content">
                <p>这是改进后的默认书籍封面效果演示。相比之前的简单渐变背景，新设计增加了以下视觉元素：</p>
            </div>
            
            <div class="improvements">
                <h3>✨ 改进亮点</h3>
                <ul>
                    <li><strong>图标元素</strong>：添加了书籍图标(📚)，增强视觉识别</li>
                    <li><strong>光影效果</strong>：添加了径向渐变光晕，营造立体感</li>
                    <li><strong>文字阴影</strong>：为书名添加阴影效果，提升可读性</li>
                    <li><strong>副标题</strong>：添加"书籍封面"副标题，明确标识</li>
                    <li><strong>悬停动画</strong>：鼠标悬停时封面会有轻微旋转和缩放效果</li>
                    <li><strong>多种渐变</strong>：预定义9种不同的渐变色方案，根据书名哈希值选择</li>
                </ul>
            </div>
            
            <div class="cover-demo">
                <div class="book-cover">
                    <div class="default-cover">
                        <div class="default-cover-icon">📚</div>
                        <div class="default-cover-title">测试书籍</div>
                        <div class="default-cover-subtitle">书籍封面</div>
                    </div>
                </div>
                
                <div class="book-cover">
                    <div class="default-cover">
                        <div class="default-cover-icon">📖</div>
                        <div class="default-cover-title">另一本书</div>
                        <div class="default-cover-subtitle">书籍封面</div>
                    </div>
                </div>
            </div>
            
            <div class="demo-content">
                <p>当网络问题导致无法获取真实书籍封面时，这个改进的默认封面将作为替代方案显示，确保用户始终能看到美观的封面效果。</p>
            </div>
            
            <div class="code-block">
/* 改进后的默认封面CSS样式 */
.default-cover {{
    background: {default_cover_css};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    text-align: center;
    padding: 30px;
    box-sizing: border-box;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    border-radius: 12px;
}}

.default-cover::before {{
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
    transform: rotate(30deg);
}}

.default-cover-icon {{
    font-size: 5rem;
    margin-bottom: 20px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    z-index: 1;
}}

.default-cover-title {{
    font-size: 1.8rem;
    line-height: 1.4;
    word-break: break-word;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    z-index: 1;
    max-width: 100%;
    padding: 0 10px;
    box-sizing: border-box;
}}
            </div>
        </div>
    </div>
</body>
</html>'''

# 保存到文件
with open("improved_default_cover_demo.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("改进后的默认封面演示页面已生成: improved_default_cover_demo.html")
print(f"使用的默认封面CSS: {default_cover_css}")