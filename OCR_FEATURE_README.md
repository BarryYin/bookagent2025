# 书籍封面OCR识别功能

## 功能概述

新增了书籍封面扫描识别功能，用户可以通过上传书籍封面图片，自动识别书名和作者信息，无需手动输入。

## 使用方法

### 1. 在增强生成器页面使用

1. 访问 `/enhanced-generator` 页面
2. 在"书籍信息"步骤中，找到"扫描书籍封面"区域
3. 点击"选择封面图片"按钮，上传书籍封面照片
4. 点击"开始识别"按钮
5. 系统会自动识别并填充书名和作者信息
6. 如果识别不准确，可以手动修改

### 2. API调用方式

```python
import httpx

# 上传图片进行识别
async def recognize_book_cover(image_path):
    async with httpx.AsyncClient() as client:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = await client.post(
                'http://localhost:8000/api/recognize-book-cover',
                files=files
            )
            return response.json()

# 使用示例
result = await recognize_book_cover('book_cover.jpg')
print(f"书名: {result['title']}")
print(f"作者: {result['author']}")
```

## 技术实现

### 后端实现

1. **OCR识别模块** (`book_cover_ocr.py`)
   - 使用百度OCR API进行文字识别
   - 智能解析识别结果，提取书名和作者
   - 支持中英文混合识别

2. **API端点** (`/api/recognize-book-cover`)
   - 接收图片文件上传
   - 调用OCR识别模块
   - 返回识别结果

### 前端实现

1. **UI组件**
   - 文件上传按钮
   - 图片预览
   - 识别按钮
   - 结果显示

2. **JavaScript功能**
   - `handleCoverUpload()`: 处理图片上传和预览
   - `scanCover()`: 调用API进行识别
   - 自动填充表单字段

## 识别策略

### 书名识别
- 选择前5行中最长的文本作为书名
- 过滤掉太短的文本（可能是出版社等信息）

### 作者识别
- 查找包含"著"、"作者"、"编著"等关键词的行
- 如果没有找到，尝试从第二行或第三行提取
- 移除"著"、"编著"等后缀

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- 其他常见图片格式

## 限制

- 图片大小限制: 5MB
- 需要清晰的封面图片以获得最佳识别效果
- 建议使用正面拍摄的封面照片

## 错误处理

如果识别失败，系统会：
1. 显示错误提示
2. 允许用户手动输入书名和作者
3. 保留已上传的图片预览

## 未来改进

1. 支持更多OCR服务提供商
2. 添加图片预处理（旋转、裁剪、增强）
3. 支持批量识别
4. 添加识别历史记录
5. 优化识别算法，提高准确率

## 依赖

- `httpx`: 用于异步HTTP请求
- 百度OCR API: 文字识别服务

## 配置

OCR API密钥配置在 `book_cover_ocr.py` 中：

```python
self.api_key = "your_baidu_ocr_api_key"
```

## 测试

运行测试脚本：

```bash
python test_ocr.py
```

注意：需要准备一张测试用的书籍封面图片。
