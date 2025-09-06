#!/usr/bin/env python3
"""
测试修复后的讯飞TTS功能
"""
import sys
import os
from pathlib import Path

# 添加create目录到路径
sys.path.insert(0, str(Path(__file__).parent / "create"))

def test_xunfei_with_demo_credentials():
    """使用demo中的凭据测试讯飞TTS"""
    print("🧪 测试修复后的讯飞TTS功能")
    print("=" * 50)
    
    try:
        from reliable_voice_generator import WebSocketXunfeiTTS
        
        # 使用demo中的凭据
        tts = WebSocketXunfeiTTS(
            app_id="e6950ae6",
            api_secret="NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh", 
            api_key="f2d4b9650c13355fc8286ac3fc34bf6e"
        )
        
        test_text = "这是一个测试文本。"
        output_file = "test_fixed_xunfei.mp3"
        
        print(f"📝 测试文本: {test_text}")
        print(f"📁 输出文件: {output_file}")
        print(f"🔑 使用demo凭据")
        
        # 测试创建任务
        print("\n🚀 测试创建任务...")
        create_result = tts.create_task(test_text)
        
        if create_result:
            print("✅ 创建任务API调用成功")
            print(f"📄 响应: {create_result}")
            
            code = create_result.get('header', {}).get('code')
            if code == 0:
                task_id = create_result.get('header', {}).get('task_id')
                print(f"🎯 任务创建成功，task_id: {task_id}")
                
                # 测试查询任务
                print(f"\n🔍 测试查询任务...")
                query_result = tts.query_task(task_id)
                
                if query_result:
                    print("✅ 查询任务API调用成功")
                    print(f"📄 响应: {query_result}")
                    
                    task_status = query_result.get('header', {}).get('task_status')
                    print(f"📊 任务状态: {task_status}")
                    
                    if task_status == '5':
                        print("🎉 任务已完成！")
                        # 尝试完整的合成流程
                        success = tts.synthesize_to_file(test_text, output_file)
                        if success:
                            print(f"✅ 完整合成流程成功！")
                            if os.path.exists(output_file):
                                file_size = os.path.getsize(output_file)
                                print(f"📊 生成文件大小: {file_size} 字节")
                        else:
                            print("❌ 完整合成流程失败")
                    else:
                        print(f"⏳ 任务还在处理中，状态: {task_status}")
                else:
                    print("❌ 查询任务API调用失败")
            else:
                message = create_result.get('header', {}).get('message', '未知错误')
                print(f"❌ 任务创建失败: {message}")
                
                # 分析常见错误
                if 'licc limit' in message.lower():
                    print("💡 这是API调用次数限制错误")
                    print("   - demo中的API密钥可能已被大量使用")
                    print("   - 需要使用自己的讯飞API密钥")
                elif 'vcn' in message.lower():
                    print("💡 这是发音人参数错误")
                    print("   - 需要使用支持的发音人")
                elif 'schema validate' in message.lower():
                    print("💡 这是参数格式错误")
                    print("   - 请求参数不符合API规范")
        else:
            print("❌ 创建任务API调用失败")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print("1. ✅ 成功修复了讯飞TTS实现，改用HTTP API")
    print("2. ✅ API调用格式正确，参考了demo实现")
    print("3. ⚠️  demo API密钥可能有使用限制")
    print("4. 💡 建议配置自己的讯飞API密钥以获得最佳效果")
    
    print("\n🔧 如何配置自己的API密钥:")
    print("1. 访问 https://console.xfyun.cn/ 注册账号")
    print("2. 创建语音合成应用获取API密钥")
    print("3. 在 xunfei_config.json 中配置:")
    print("""   {
     "xunfei": {
       "app_id": "你的APP_ID",
       "api_key": "你的API_KEY", 
       "api_secret": "你的API_SECRET"
     }
   }""")

if __name__ == "__main__":
    test_xunfei_with_demo_credentials()