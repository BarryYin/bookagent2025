# 项目配置指南

## 🚀 快速开始

### 1. 克隆项目后的首次配置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 创建配置文件
cp .env.example .env

# 3. 编辑 .env 文件，填入你的 API Key
nano .env  # 或使用你喜欢的编辑器
```

### 2. 配置 API Key

在 `.env` 文件中，至少配置一个 AI 模型服务：

```bash
# 方案 1: 使用 Google Gemini（推荐用于开发）
GEMINI_API_KEY=你的_Gemini_API_Key

# 方案 2: 使用 OpenAI
OPENAI_API_KEY=sk-你的_OpenAI_API_Key
OPENAI_BASE_URL=https://api.openai.com/v1

# 方案 3: 使用百度千帆
BAIDU_API_KEY=你的_百度_API_Key

# 方案 4: 使用阿里通义千问
QWEN_API_KEY=你的_Qwen_API_Key
```

### 3. 启动应用

```bash
# 开发模式
python app.py

# 或使用 uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📝 配置说明

### 必需配置

- **AI 模型 API Key**：至少配置一个（Gemini/OpenAI/百度/Qwen）

### 可选配置

- **语音服务**：讯飞语音、Fish Audio（用于语音生成功能）
- **OCR 服务**：百度 OCR（用于书籍封面识别）
- **JWT 密钥**：用于用户认证（生产环境必须修改）

## 🔒 安全提示

1. ⚠️ **不要**将 `.env` 文件提交到 Git
2. ⚠️ **不要**在代码中硬编码 API Key
3. ⚠️ 生产环境使用强随机的 JWT 密钥
4. ✅ 定期轮换 API Key

## 🐳 Docker 部署

```bash
# 使用 docker-compose
docker-compose up -d
```

确保在 `docker-compose.yml` 中配置环境变量或使用 `.env` 文件。

## 📚 更多信息

- 详细配置说明：查看 `CONFIG_MIGRATION_GUIDE.md`
- 配置示例：查看 `.env.example`
- 配置代码：查看 `env_config.py`

## ❓ 常见问题

### Q: 提示 "未配置有效的 API Key"

A: 检查 `.env` 文件是否存在，以及 API Key 是否正确填写。

### Q: 可以同时配置多个 AI 模型吗？

A: 可以！系统会自动选择可用的服务。

### Q: 旧的 credentials.json 还能用吗？

A: 可以，但建议迁移到 `.env` 方式以提高安全性。

## 🆘 需要帮助？

如有问题，请：
1. 查看 `CONFIG_MIGRATION_GUIDE.md`
2. 检查 `.env.example` 中的配置示例
3. 提交 Issue 或联系维护者
