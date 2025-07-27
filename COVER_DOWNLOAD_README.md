# 书籍封面下载功能

这个项目现在包含了从 Google Books API 搜索并下载书籍封面到本地的功能。

## 功能特性

- 🔍 使用 Google Books API 搜索书籍封面
- 📥 自动下载封面图片到本地 `covers/` 目录
- 🎯 多种搜索策略，提高成功率
- 📁 自动生成安全的文件名
- ⚡ 异步处理，提高性能

## 文件说明

- `test_cover.py` - 主要的封面搜索和下载功能
- `demo_cover_download.py` - 演示脚本，批量下载多本书的封面
- `covers/` - 下载的封面图片存储目录

## 使用方法

### 1. 基本使用

```python
import asyncio
from test_cover import search_book_cover

async def main():
    # 搜索并下载封面
    result = await search_book_cover("月亮与六便士", "毛姆", download=True)
    print(f"结果: {result}")

asyncio.run(main())
```

### 2. 只搜索不下载

```python
# 只返回封面URL，不下载
result = await search_book_cover("百年孤独", "加西亚·马尔克斯", download=False)
```

### 3. 批量下载

运行演示脚本：
```bash
python demo_cover_download.py
```

## 参数说明

`search_book_cover(book_title, author=None, download=False)`

- `book_title` (str): 书籍标题
- `author` (str, optional): 作者姓名
- `download` (bool): 是否下载到本地，默认 False

## 返回值

- 如果 `download=True` 且下载成功：返回本地文件路径 (如 `"covers/月亮与六便士_毛姆.jpg"`)
- 如果 `download=False` 或下载失败：返回封面URL
- 如果未找到封面：返回 `"default_cover"`

## 文件命名规则

下载的文件会按照以下格式命名：
- 格式：`{书名}_{作者}.{扩展名}`
- 特殊字符会被过滤，空格替换为下划线
- 扩展名从原始URL中提取，默认为 `.jpg`

## 示例输出

```
🔍 搜索查询: 月亮与六便士 毛姆
📚 找到书籍数量: 1000000
✅ 策略1成功找到封面URL: https://books.google.com/...
📥 正在下载图片: https://books.google.com/...
✅ 图片已保存到: covers/月亮与六便士_毛姆.jpg
```

## 依赖要求

- `httpx` - 异步HTTP客户端
- `asyncio` - 异步编程支持

安装依赖：
```bash
pip install httpx
```

## 注意事项

1. 需要网络连接访问 Google Books API
2. 下载的图片质量取决于API返回的版本
3. 某些书籍可能没有封面图片
4. 文件名会自动处理特殊字符以确保兼容性 