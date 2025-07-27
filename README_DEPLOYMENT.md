# Fogsight 部署指南

## 概述
Fogsight 是一个基于 FastAPI 的书籍 PPT 生成应用，支持多种部署方式。

## 前置要求

### 1. 系统要求
- Linux 服务器（推荐 Ubuntu 20.04+ 或 CentOS 8+）
- Python 3.11+
- 至少 2GB RAM
- 至少 10GB 磁盘空间

### 2. 必需文件
- `credentials.json` - API 密钥配置文件
- `appbook.py` - 主应用文件
- `requirements.txt` - Python 依赖

## 部署方案

### 方案一：Docker 部署（推荐）

#### 1. 安装 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. 安装 Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. 配置 credentials.json
```json
{
  "API_KEY": "your-api-key-here",
  "BASE_URL": "https://api.openai.com/v1"
}
```

#### 4. 部署应用
```bash
# 克隆项目
git clone <your-repo-url>
cd fogsight

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

#### 5. 验证部署
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试访问
curl http://localhost:8000/
```

### 方案二：直接部署

#### 1. 安装 Python 依赖
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置环境
```bash
# 创建应用目录
sudo mkdir -p /opt/fogsight
sudo cp -r . /opt/fogsight/
sudo chown -R fogsight:fogsight /opt/fogsight

# 创建用户
sudo useradd -r -s /bin/false fogsight
```

#### 3. 配置 systemd 服务
```bash
# 复制服务文件
sudo cp systemd.service /etc/systemd/system/fogsight.service

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable fogsight
sudo systemctl start fogsight
```

### 方案三：使用 Nginx 反向代理

#### 1. 安装 Nginx
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. 配置 Nginx
```bash
# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/fogsight
sudo ln -s /etc/nginx/sites-available/fogsight /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 3. 配置 SSL（可选）
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 生产环境优化

### 1. 性能优化
```python
# 在 appbook.py 中添加
import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        "appbook:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 根据 CPU 核心数调整
        loop="uvloop",  # 使用 uvloop 提升性能
        http="httptools"  # 使用 httptools 提升性能
    )
```

### 2. 监控配置
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 设置日志轮转
sudo cp logrotate.conf /etc/logrotate.d/fogsight
```

### 3. 备份策略
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/fogsight"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/fogsight_$DATE.tar.gz outputs/
find $BACKUP_DIR -name "fogsight_*.tar.gz" -mtime +7 -delete
EOF

# 添加到 crontab
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep :8000

# 杀死占用进程
sudo kill -9 <PID>
```

#### 2. 权限问题
```bash
# 修复权限
sudo chown -R fogsight:fogsight /opt/fogsight
sudo chmod -R 755 /opt/fogsight
```

#### 3. API 密钥问题
```bash
# 检查 credentials.json
cat credentials.json | jq .

# 测试 API 连接
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h

# 增加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 安全建议

### 1. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. 定期更新
```bash
# 更新系统
sudo apt update && sudo apt upgrade

# 更新 Docker 镜像
docker-compose pull
docker-compose up -d
```

### 3. 日志监控
```bash
# 设置日志监控
sudo apt install fail2ban
sudo cp jail.local /etc/fail2ban/jail.local
sudo systemctl restart fail2ban
```

## 维护命令

```bash
# 查看服务状态
sudo systemctl status fogsight

# 重启服务
sudo systemctl restart fogsight

# 查看日志
sudo journalctl -u fogsight -f

# 更新代码
git pull
sudo systemctl restart fogsight

# 清理旧文件
find outputs/ -type f -mtime +30 -delete
```

## 联系支持

如果遇到问题，请检查：
1. 日志文件
2. 系统资源使用情况
3. 网络连接状态
4. API 密钥有效性 