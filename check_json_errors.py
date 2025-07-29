"""
检查哪些PPT的JSON文件有问题
"""
import json
import os
from pathlib import Path

def check_json_errors():
    """检查JSON文件错误"""
    outputs_dir = Path("outputs")
    
    print("🔍 检查JSON文件错误")
    print("=" * 50)
    
    error_sessions = []
    valid_sessions = []
    
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            data_file = session_dir / "data.json"
            html_file = session_dir / "presentation.html"
            
            if data_file.exists() and html_file.exists():
                try:
                    # 尝试读取JSON文件
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查必要字段
                    topic = data.get("topic")
                    book_data = data.get("book_data", {})
                    
                    if not topic:
                        print(f"❌ {session_dir.name}: 缺少topic字段")
                        error_sessions.append(session_dir.name)
                    else:
                        valid_sessions.append(session_dir.name)
                        
                except json.JSONDecodeError as e:
                    print(f"❌ {session_dir.name}: JSON解析错误 - {e}")
                    error_sessions.append(session_dir.name)
                except Exception as e:
                    print(f"❌ {session_dir.name}: 其他错误 - {e}")
                    error_sessions.append(session_dir.name)
            else:
                print(f"❌ {session_dir.name}: 文件缺失")
                error_sessions.append(session_dir.name)
    
    print(f"\n📊 统计结果:")
    print(f"  有效PPT: {len(valid_sessions)}")
    print(f"  错误PPT: {len(error_sessions)}")
    
    if error_sessions:
        print(f"\n❌ 有问题的PPT:")
        for session_id in error_sessions:
            print(f"  - {session_id}")
    
    return error_sessions, valid_sessions

if __name__ == "__main__":
    check_json_errors() 