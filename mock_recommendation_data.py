"""
模拟推荐数据生成器
为测试和演示目的生成模拟的书籍推荐数据
"""

MOCK_BOOKS_DATABASE = [
    {
        'title': '乌合之众',
        'author': '古斯塔夫·勒庞',
        'category_name': '心理学',
        'description': '群体心理学的经典之作，深刻剖析了群体行为的特点和规律',
        'cover_url': '',
        'popularity_score': 0.9
    },
    {
        'title': '被讨厌的勇气',
        'author': '岸见一郎/古贺史健',
        'category_name': '心理学',
        'description': '基于阿德勒心理学的自我成长指南，教你如何获得真正的勇气',
        'cover_url': '',
        'popularity_score': 0.85
    },
    {
        'title': '思考，快与慢',
        'author': '丹尼尔·卡尼曼',
        'category_name': '心理学',
        'description': '诺贝尔经济学奖得主关于思维模式的深度分析',
        'cover_url': '',
        'popularity_score': 0.88
    },
    {
        'title': '人类简史',
        'author': '尤瓦尔·赫拉利',
        'category_name': '历史',
        'description': '从石器时代到21世纪，人类发展的宏大叙事',
        'cover_url': '',
        'popularity_score': 0.92
    },
    {
        'title': '未来简史',
        'author': '尤瓦尔·赫拉利',
        'category_name': '历史',
        'description': '人类未来发展的预测和思考',
        'cover_url': '',
        'popularity_score': 0.86
    },
    {
        'title': '万历十五年',
        'author': '黄仁宇',
        'category_name': '历史',
        'description': '以小见大，从万历十五年看中国历史的深层结构',
        'cover_url': '',
        'popularity_score': 0.83
    },
    {
        'title': '第二性',
        'author': '西蒙娜·德·波伏娃',
        'category_name': '哲学',
        'description': '女性主义哲学的奠基之作',
        'cover_url': '',
        'popularity_score': 0.84
    },
    {
        'title': '存在与时间',
        'author': '马丁·海德格尔',
        'category_name': '哲学',
        'description': '20世纪最重要的哲学著作之一',
        'cover_url': '',
        'popularity_score': 0.75
    },
    {
        'title': '沉默的大多数',
        'author': '王小波',
        'category_name': '散文',
        'description': '王小波的杂文集，独特的思维和幽默的文字',
        'cover_url': '',
        'popularity_score': 0.87
    },
    {
        'title': '百年孤独',
        'author': '加西亚·马尔克斯',
        'category_name': '小说',
        'description': '魔幻现实主义的经典之作',
        'cover_url': '',
        'popularity_score': 0.91
    },
    {
        'title': '1984',
        'author': '乔治·奥威尔',
        'category_name': '小说',
        'description': '反乌托邦文学的经典代表',
        'cover_url': '',
        'popularity_score': 0.89
    },
    {
        'title': '三体',
        'author': '刘慈欣',
        'category_name': '科幻',
        'description': '中国科幻文学的里程碑之作',
        'cover_url': '',
        'popularity_score': 0.93
    },
    {
        'title': '人工智能简史',
        'author': '尼克·博斯特罗姆',
        'category_name': '科技',
        'description': '人工智能发展的历史和未来展望',
        'cover_url': '',
        'popularity_score': 0.82
    },
    {
        'title': '原则',
        'author': '瑞·达利欧',
        'category_name': '管理',
        'description': '桥水基金创始人的成功原则',
        'cover_url': '',
        'popularity_score': 0.81
    },
    {
        'title': '从0到1',
        'author': '彼得·蒂尔',
        'category_name': '创业',
        'description': '关于创新和创业的深度思考',
        'cover_url': '',
        'popularity_score': 0.85
    }
]

def get_mock_recommendations_for_category(category: str, exclude_titles: list = None, limit: int = 5):
    """根据分类获取模拟推荐"""
    if exclude_titles is None:
        exclude_titles = []
    
    # 筛选指定分类的书籍
    category_books = [book for book in MOCK_BOOKS_DATABASE 
                     if book['category_name'] == category 
                     and book['title'] not in exclude_titles]
    
    # 按流行度排序
    category_books.sort(key=lambda x: x['popularity_score'], reverse=True)
    
    return category_books[:limit]

def get_diversified_mock_recommendations(exclude_titles: list = None, limit: int = 5):
    """获取多样化的模拟推荐"""
    if exclude_titles is None:
        exclude_titles = []
    
    # 按分类分组
    categories = {}
    for book in MOCK_BOOKS_DATABASE:
        if book['title'] not in exclude_titles:
            category = book['category_name']
            if category not in categories:
                categories[category] = []
            categories[category].append(book)
    
    # 每个分类选一本最受欢迎的
    recommendations = []
    for category, books in categories.items():
        if books:
            best_book = max(books, key=lambda x: x['popularity_score'])
            recommendations.append(best_book)
        
        if len(recommendations) >= limit:
            break
    
    # 如果不够，补充剩余的高分书籍
    if len(recommendations) < limit:
        remaining_books = [book for book in MOCK_BOOKS_DATABASE 
                          if book['title'] not in exclude_titles 
                          and book not in recommendations]
        remaining_books.sort(key=lambda x: x['popularity_score'], reverse=True)
        
        needed = limit - len(recommendations)
        recommendations.extend(remaining_books[:needed])
    
    return recommendations[:limit]

def get_mock_recommendations_by_preference(user_preferences: dict, exclude_titles: list = None, limit: int = 5):
    """根据用户偏好获取模拟推荐"""
    if exclude_titles is None:
        exclude_titles = []
    
    if not user_preferences:
        return get_diversified_mock_recommendations(exclude_titles, limit)
    
    # 找到用户最感兴趣的分类
    top_category = max(user_preferences, key=user_preferences.get)
    
    recommendations = []
    
    # 先推荐用户感兴趣分类的书籍
    top_category_books = get_mock_recommendations_for_category(top_category, exclude_titles, limit // 2 + 1)
    recommendations.extend(top_category_books)
    
    # 再推荐其他分类的书籍以增加多样性
    other_books = [book for book in MOCK_BOOKS_DATABASE 
                   if book['category_name'] != top_category 
                   and book['title'] not in exclude_titles
                   and book not in recommendations]
    
    other_books.sort(key=lambda x: x['popularity_score'], reverse=True)
    
    remaining_slots = limit - len(recommendations)
    if remaining_slots > 0:
        recommendations.extend(other_books[:remaining_slots])
    
    return recommendations[:limit]
