"""
书籍介绍系统 - 配置
"""
import os
import json
from typing import Dict, Any, Optional

# 默认配置
DEFAULT_CONFIG = {
    # API配置
    "api": {
        "llm_provider": "openai",  # 'openai', 'gemini', 'mock'
        "tts_provider": "mock",    # 'openai', 'google', 'mock'
        "search_provider": "mock", # 'google', 'bing', 'mock'
    },
    
    # 系统配置
    "system": {
        "max_concurrent_sessions": 10,
        "session_timeout_minutes": 30,
        "debug_mode": False,
    },
    
    # 内容生成配置
    "content": {
        "default_language": "zh",
        "default_style": "professional",
        "min_slides": 5,
        "max_slides": 15,
        "available_styles": [
            "professional",
            "academic",
            "creative",
            "minimalist",
            "colorful"
        ],
    },
    
    # 前端配置
    "frontend": {
        "theme": "light",
        "animation_enabled": True,
        "auto_play": True,
    }
}

# 加载配置
def load_config() -> Dict[str, Any]:
    """加载配置"""
    config = DEFAULT_CONFIG.copy()
    
    # 尝试从配置文件加载
    config_path = os.environ.get("CONFIG_PATH", "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # 递归更新配置
                deep_update(config, user_config)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
    
    # 从环境变量加载API密钥
    if os.environ.get("OPENAI_API_KEY"):
        config["api"]["openai_api_key"] = os.environ.get("OPENAI_API_KEY")
    
    if os.environ.get("GOOGLE_API_KEY"):
        config["api"]["google_api_key"] = os.environ.get("GOOGLE_API_KEY")
    
    return config

def deep_update(source: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """递归更新字典"""
    for key, value in update.items():
        if key in source and isinstance(source[key], dict) and isinstance(value, dict):
            deep_update(source[key], value)
        else:
            source[key] = value
    return source

# 全局配置实例
CONFIG = load_config()

def get_config(path: Optional[str] = None) -> Any:
    """获取配置项"""
    if not path:
        return CONFIG
    
    parts = path.split(".")
    current = CONFIG
    for part in parts:
        if part not in current:
            return None
        current = current[part]
    
    return current