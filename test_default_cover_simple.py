# 简化版本的默认封面生成函数（复制自appbook.py）
def get_default_book_cover(book_title: str) -> str:
    """
    生成默认书籍封面
    基于书名生成一个美观的默认封面样式
    """
    # 预定义的渐变色方案
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "linear-gradient(135deg, #ff8a80 0%, #ea4c89 100%)",
        "linear-gradient(135deg, #8fd3f4 0%, #84fab0 100%)"
    ]
    
    # 根据书名哈希选择渐变
    gradient_index = hash(book_title) % len(gradients)
    gradient = gradients[gradient_index]
    
    # 返回CSS渐变字符串，前端可以直接使用
    return f"gradient:{gradient}"

# 测试书籍标题
test_books = [
    "月亮与六便士",
    "百年孤独",
    "活着",
    "三体",
    "围城",
    "红楼梦",
    "西游记",
    "水浒传",
    "三国演义",
    "傲慢与偏见",
    "战争与和平",
    "追风筝的人"
]

# 生成测试HTML
html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>默认封面测试</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .cover-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        .book-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .book-card:hover {
            transform: translateY(-5px);
        }
        .book-cover {
            width: 100%;
            height: 350px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .default-cover {
            width: 100%;
            height: 100%;
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
        }
        .default-cover::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
        }
        .default-cover-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            z-index: 1;
        }
        .default-cover-title {
            font-size: 1.2rem;
            line-height: 1.4;
            word-break: break-word;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            z-index: 1;
            max-width: 100%;
            padding: 0 5px;
            box-sizing: border-box;
        }
        .default-cover-subtitle {
            font-size: 0.9rem;
            margin-top: 8px;
            opacity: 0.9;
            z-index: 1;
        }
        .book-info {
            padding: 15px;
            text-align: center;
        }
        .book-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0 0 5px 0;
            color: #333;
        }
        .cover-type {
            font-size: 0.8rem;
            color: #666;
            background: #f0f0f0;
            padding: 3px 8px;
            border-radius: 12px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 改进后的默认书籍封面效果测试</h1>
        <div class="cover-grid">
'''

# 为每本书生成封面
for book_title in test_books:
    # 获取默认封面CSS
    cover_css = get_default_book_cover(book_title)
    # 提取CSS渐变部分
    if cover_css.startswith("gradient:"):
        gradient_css = cover_css.replace("gradient:", "")
    else:
        gradient_css = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    
    html_content += f'''
            <div class="book-card">
                <div class="book-cover">
                    <div class="default-cover" style="background: {gradient_css};">
                        <div class="default-cover-icon">📚</div>
                        <div class="default-cover-title">{book_title}</div>
                        <div class="default-cover-subtitle">书籍封面</div>
                    </div>
                </div>
                <div class="book-info">
                    <h3 class="book-title">{book_title}</h3>
                    <span class="cover-type">默认封面</span>
                </div>
            </div>
'''

html_content += '''
        </div>
    </div>
</body>
</html>'''

# 保存HTML文件
with open("test_default_cover_simple.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("测试HTML文件已生成: test_default_cover_simple.html")