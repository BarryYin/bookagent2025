# 测试默认封面生成功能
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

# 测试
if __name__ == "__main__":
    test_books = ["月亮与六便士", "百年孤独", "活着", "三体"]
    for book in test_books:
        cover = get_default_book_cover(book)
        print(f"{book}: {cover}")