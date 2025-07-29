# 📚 书籍分类系统

## 🎯 系统概述

新的分类系统使用 **CSV文件** 统一管理所有书籍的分类信息，解决了之前数据分散、无法检索和过滤的问题。

## 📁 文件结构

```
fogsight/
├── books_categories.csv          # 分类数据库 (核心文件)
├── book_category_manager.py      # 分类管理器
├── appbook.py                    # 主应用 (已集成分类功能)
├── outputs/                      # PPT文件存储
│   ├── session_id_1/
│   │   ├── data.json            # 包含分类信息
│   │   └── presentation.html
│   └── session_id_2/
└── covers/                       # 封面图片存储
```

## 🗄️ CSV数据库格式

```csv
title,author,category_id,category_name,category_color,category_icon,created_at,ppt_path
时间管理大师,吉姆·兰德尔,efficiency,效率提升类,#27AE60,⚡,2024-01-15,1f466011-9817-4100-b32c-a5cee38296b0
风声,麦家,literature,文学类,#E74C3C,📖,2024-01-14,335a076e-4d8c-4c68-b79a-f1dc0fd5f93f
```

## 📊 分类体系

| 分类ID | 分类名称 | 颜色 | 图标 | 示例书籍 |
|--------|----------|------|------|----------|
| `literature` | 文学类 | `#E74C3C` | 📖 | 《活着》、《百年孤独》 |
| `efficiency` | 效率提升类 | `#27AE60` | ⚡ | 《时间管理大师》 |
| `fiction` | 虚构类 | `#9B59B6` | 🔮 | 《三体》、《小王子》 |
| `biography` | 自传类 | `#F39C12` | 👤 | 《乔布斯传》 |
| `textbook` | 教材类 | `#34495E` | 📚 | 《高等数学》 |

## 🔧 核心功能

### 1. 自动分类
- 使用LLM对每本书进行智能分类
- 生成PPT时自动添加到分类数据库
- 支持置信度评估

### 2. 数据管理
- **统一存储**: 所有分类信息集中在CSV文件
- **快速检索**: 支持按分类、作者、书名搜索
- **统计分析**: 提供分类统计信息

### 3. API接口
```python
# 获取分类统计
GET /api/categories

# 获取所有书籍
GET /api/books

# 按分类筛选
GET /api/books?category_id=efficiency

# 搜索书籍
GET /api/books?search=时间

# 获取指定分类的书籍
GET /api/categories/{category_id}/books
```

## 🚀 使用方法

### 1. 生成新PPT
```python
# 自动分类并保存到数据库
python appbook.py
# 访问 http://localhost:8000 生成PPT
```

### 2. 查看分类统计
```python
python test_category_manager.py
```

### 3. 测试API
```python
python test_category_api.py
```

## 📈 优势对比

### 之前的问题
- ❌ 数据分散在各个 `data.json` 文件中
- ❌ 无法统一检索和过滤
- ❌ 首页和图书馆无法按分类显示
- ❌ 扩展性差，难以添加新功能

### 现在的解决方案
- ✅ **统一数据库**: CSV文件集中管理所有分类信息
- ✅ **快速检索**: 支持按分类、作者、书名搜索
- ✅ **API支持**: 提供完整的REST API
- ✅ **统计分析**: 实时分类统计
- ✅ **易于扩展**: 可以轻松添加新分类和功能

## 🔄 数据流程

1. **生成PPT** → LLM分类 → 保存到CSV数据库
2. **前端显示** → 调用API → 获取分类信息 → 显示标签
3. **用户筛选** → 选择分类 → API返回结果 → 更新界面

## 🛠️ 技术实现

### 核心组件
- `BookCategoryManager`: 分类管理器类
- `add_book_to_category()`: 添加书籍到数据库
- `get_books_by_category_id()`: 按分类获取书籍
- `search_books_by_keyword()`: 搜索书籍

### 集成点
- `appbook.py`: 主应用集成分类功能
- `save_generated_content()`: 保存时自动添加到数据库
- API端点: 提供分类数据服务

## 📋 测试验证

运行以下测试确保功能正常：

```bash
# 1. 测试分类管理器
python test_category_manager.py

# 2. 生成新PPT测试分类
python test_new_ppt.py

# 3. 测试API功能
python test_category_api.py
```

## 🎯 未来扩展

- [ ] 分类管理界面
- [ ] 批量重新分类
- [ ] 分类统计图表
- [ ] 推荐系统
- [ ] 标签系统

---

**总结**: 新的分类系统解决了数据分散的问题，提供了统一的数据库管理和完整的API支持，为后续功能扩展奠定了坚实基础。 