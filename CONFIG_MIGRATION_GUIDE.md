# 配置迁移指南

## 概述

为了提高安全性，本项目已将所有 API Key 和敏感配置移至环境变量管理。

## 快速开始

### 1. 安装依赖

```bash
pip install python-dotenv
```

### 2. 创建配置文件

复制示例配置文件：

```bash
cp .env.example .env
```

### 3. 填写配置

编辑 `.env` 文件，填入你的 API Key：

```bash
# 选择你使用的 AI 模型服务（至少配置一个）

# 如果使用 Google Gemini
GEMINI_API_KEY=your_actual_gemini_key

# 如果使用 OpenAI 或 OpenRouter
OPENAI_API_KEY=sk-your_actual_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# 如果使用百度千帆
BAIDU_API_KEY=your_actual_baidu_key

# 其他服务按需配置...
```

### 4. 更新代码引用

在你的 Python 文件中，使用新的配置模块：

```python
# 旧方式（不推荐）
# credentials = json.load(open("credentials.json"))
# API_KEY = credentials["API_KEY"]

# 新方式（推荐）
from env_config import config, API_KEY, BASE_URL, MODEL

# 使用配置
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
```

## 配置项说明

### AI 模型配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `GEMINI_API_KEY` | Google Gemini API Key | `AIza...` |
| `OPENAI_API_KEY` | OpenAI/OpenRouter API Key | `sk-...` |
| `BAIDU_API_KEY` | 百度千帆 API Key | `bce-v3/...` |
| `QWEN_API_KEY` | 阿里通义千问 API Key | `ms-...` |

### 语音服务配置

| 配置项 | 说明 |
|--------|------|
| `XUNFEI_APP_ID` | 讯飞语音 App ID |
| `XUNFEI_API_KEY` | 讯飞语音 API Key |
| `XUNFEI_API_SECRET` | 讯飞语音 API Secret |
| `FISH_API_KEY` | Fish Audio API Key |

### 认证配置

| 配置项 | 说明 |
|--------|------|
| `JWT_SECRET_KEY` | JWT 签名密钥（生产环境必须修改） |
| `JWT_ALGORITHM` | JWT 算法（默认 HS256） |

## 向后兼容

如果你暂时无法迁移，`credentials.json` 仍然可以使用，但建议尽快迁移到环境变量方式。

配置优先级：
1. 环境变量（`.env` 文件或系统环境变量）
2. `credentials.json` 文件（向后兼容）

## 安全建议

1. ✅ **永远不要**将 `.env` 文件提交到 Git
2. ✅ **永远不要**将 `credentials.json` 提交到 Git
3. ✅ 在生产环境使用强随机的 `JWT_SECRET_KEY`
4. ✅ 定期轮换 API Key
5. ✅ 使用不同的 Key 用于开发和生产环境

## 生产环境部署

### Docker 部署

在 `docker-compose.yml` 中使用环境变量：

```yaml
services:
  app:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      # ... 其他配置
```

### 服务器部署

直接设置系统环境变量：

```bash
export GEMINI_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

或在 systemd service 文件中配置：

```ini
[Service]
Environment="GEMINI_API_KEY=your_key"
Environment="OPENAI_API_KEY=your_key"
```

## 故障排查

### 问题：提示 "未配置有效的 API Key"

**解决方案：**
1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中的 Key 是否正确
3. 确保已安装 `python-dotenv`

### 问题：无法加载 .env 文件

**解决方案：**
```bash
pip install python-dotenv
```

### 问题：想要使用多个 AI 模型

**解决方案：**
在 `.env` 中配置多个 Key，代码会自动选择可用的服务。

## 需要帮助？

如有问题，请查看：
- `.env.example` - 完整的配置示例
- `env_config.py` - 配置管理代码
- 项目文档或提交 Issue
