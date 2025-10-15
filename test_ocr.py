"""
测试OCR识别功能
"""

import asyncio
from book_cover_ocr import get_ocr_instance


async def test_ocr():
    """测试OCR识别"""
    ocr = get_ocr_instance()
    
    # 测试文件路径（需要替换为实际的测试图片）
    test_image_path = "test_book_cover.jpg"
    
    print("开始测试OCR识别...")
    result = await ocr.recognize_from_file(test_image_path)
    
    print("\n识别结果:")
    print(f"书名: {result.get('title')}")
    print(f"作者: {result.get('author')}")
    print(f"所有识别文字: {result.get('all_text')}")
    
    if result.get('error'):
        print(f"错误: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_ocr())
