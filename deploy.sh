#!/bin/bash

# 部署脚本
echo "🚀 开始部署 Fogsight 应用..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 检查 credentials.json 文件
if [ ! -f "credentials.json" ]; then
    echo "❌ credentials.json 文件不存在，请创建该文件并配置 API 密钥"
    exit 1
fi

# 创建必要的目录
mkdir -p outputs
mkdir -p logs

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建新镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ 部署成功！"
    echo "🌐 访问地址: http://localhost:8000"
    echo "📚 图书馆页面: http://localhost:8000/library"
else
    echo "❌ 部署失败，请检查日志:"
    docker-compose logs
fi 