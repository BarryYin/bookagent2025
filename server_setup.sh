#!/bin/bash

# 服务器端设置脚本
# 用于在服务器上配置 Fogsight 应用

set -e

echo "🚀 开始设置 Fogsight 服务器环境..."

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 安装必要的软件包
echo "🔧 安装必要的软件包..."
apt install -y python3 python3-pip python3-venv nginx curl wget git supervisor

# 创建应用用户
echo "👤 创建应用用户..."
if ! id "fogsight" &>/dev/null; then
    useradd -r -s /bin/false -d /opt/fogsight fogsight
fi

# 创建应用目录
echo "📁 创建应用目录..."
mkdir -p /opt/fogsight
chown fogsight:fogsight /opt/fogsight

# 创建日志目录
mkdir -p /var/log/fogsight
chown fogsight:fogsight /var/log/fogsight

# 创建输出目录
mkdir -p /opt/fogsight/outputs
chown fogsight:fogsight /opt/fogsight/outputs

# 设置 Python 虚拟环境
echo "🐍 设置 Python 环境..."
cd /opt/fogsight
python3 -m venv venv
chown -R fogsight:fogsight venv

# 安装 Python 依赖
echo "📚 安装 Python 依赖..."
sudo -u fogsight /opt/fogsight/venv/bin/pip install --upgrade pip
sudo -u fogsight /opt/fogsight/venv/bin/pip install -r requirements.txt

# 配置 systemd 服务
echo "⚙️ 配置 systemd 服务..."
cat > /etc/systemd/system/fogsight.service << 'EOF'
[Unit]
Description=Fogsight Book PPT Generator
After=network.target

[Service]
Type=simple
User=fogsight
Group=fogsight
WorkingDirectory=/opt/fogsight
Environment=PATH=/opt/fogsight/venv/bin
ExecStart=/opt/fogsight/venv/bin/uvicorn appbook:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/fogsight/outputs /var/log/fogsight

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
systemctl daemon-reload

# 配置 Nginx
echo "🌐 配置 Nginx..."
cat > /etc/nginx/sites-available/fogsight << 'EOF'
server {
    listen 80;
    server_name _;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    # SSL 配置 (需要替换为实际的证书路径)
    ssl_certificate /etc/ssl/certs/fogsight.crt;
    ssl_certificate_key /etc/ssl/private/fogsight.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 客户端最大上传大小
    client_max_body_size 10M;
    
    # 代理到 FastAPI 应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件缓存
    location /static/ {
        proxy_pass http://127.0.0.1:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 输出文件访问
    location /outputs/ {
        proxy_pass http://127.0.0.1:8000/outputs/;
        expires 1h;
        add_header Cache-Control "public";
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/fogsight /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
nginx -t

# 配置防火墙
echo "🔥 配置防火墙..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 创建 SSL 证书目录
mkdir -p /etc/ssl/certs /etc/ssl/private

# 生成自签名证书（临时使用）
echo "🔐 生成临时 SSL 证书..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/fogsight.key \
    -out /etc/ssl/certs/fogsight.crt \
    -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"

# 设置证书权限
chmod 600 /etc/ssl/private/fogsight.key
chmod 644 /etc/ssl/certs/fogsight.crt

# 启动服务
echo "🚀 启动服务..."
systemctl enable fogsight
systemctl start fogsight
systemctl enable nginx
systemctl restart nginx

# 创建日志轮转配置
echo "📝 配置日志轮转..."
cat > /etc/logrotate.d/fogsight << 'EOF'
/var/log/fogsight/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 fogsight fogsight
    postrotate
        systemctl reload fogsight
    endscript
}
EOF

# 创建备份脚本
echo "💾 创建备份脚本..."
cat > /opt/fogsight/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/fogsight"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/fogsight_$DATE.tar.gz -C /opt/fogsight outputs/
find $BACKUP_DIR -name "fogsight_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/fogsight/backup.sh

# 添加到 crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/fogsight/backup.sh") | crontab -

echo "✅ 服务器设置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 上传应用文件到 /opt/fogsight/"
echo "2. 配置 credentials.json 文件"
echo "3. 重启服务: systemctl restart fogsight"
echo "4. 检查服务状态: systemctl status fogsight"
echo ""
echo "🌐 访问地址: https://your-server-ip/"
echo "📚 图书馆页面: https://your-server-ip/library"
echo ""
echo "⚠️  注意：当前使用的是自签名证书，生产环境请替换为正式的 SSL 证书" 