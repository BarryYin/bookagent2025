#!/bin/bash

# 本地文件上传脚本
# 用于将 Fogsight 应用文件上传到服务器

set -e

# 配置变量
SERVER_IP="your-server-ip"  # 替换为你的服务器IP
SERVER_USER="root"          # 替换为你的服务器用户名
SERVER_PORT="22"            # SSH 端口
REMOTE_DIR="/opt/fogsight"  # 远程目录

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 开始上传 Fogsight 应用到服务器...${NC}"

# 检查参数
if [ "$1" != "" ]; then
    SERVER_IP=$1
fi

if [ "$2" != "" ]; then
    SERVER_USER=$2
fi

# 验证服务器连接
echo -e "${YELLOW}🔍 测试服务器连接...${NC}"
if ! ssh -p $SERVER_PORT -o ConnectTimeout=10 -o BatchMode=yes $SERVER_USER@$SERVER_IP exit 2>/dev/null; then
    echo -e "${RED}❌ 无法连接到服务器 $SERVER_USER@$SERVER_IP:$SERVER_PORT${NC}"
    echo "请检查："
    echo "1. 服务器IP地址是否正确"
    echo "2. SSH 密钥是否已配置"
    echo "3. 服务器是否可访问"
    exit 1
fi

echo -e "${GREEN}✅ 服务器连接成功${NC}"

# 创建临时打包目录
echo -e "${YELLOW}📦 准备上传文件...${NC}"
TEMP_DIR=$(mktemp -d)
mkdir -p $TEMP_DIR/fogsight

# 复制核心文件
echo "复制核心应用文件..."
cp appbook.py $TEMP_DIR/fogsight/
cp requirements.txt $TEMP_DIR/fogsight/
cp -r templates $TEMP_DIR/fogsight/
cp -r static $TEMP_DIR/fogsight/
cp -r outputs $TEMP_DIR/fogsight/

# 创建 credentials.json 模板（如果不存在）
if [ ! -f "credentials.json" ]; then
    echo -e "${YELLOW}⚠️  credentials.json 不存在，创建模板...${NC}"
    cat > $TEMP_DIR/fogsight/credentials.json << 'EOF'
{
  "API_KEY": "your-api-key-here",
  "BASE_URL": "https://api.openai.com/v1"
}
EOF
    echo -e "${YELLOW}请在上传后编辑 /opt/fogsight/credentials.json 文件${NC}"
else
    cp credentials.json $TEMP_DIR/fogsight/
fi

# 创建 .gitkeep 文件
mkdir -p $TEMP_DIR/fogsight/outputs
touch $TEMP_DIR/fogsight/outputs/.gitkeep

# 创建上传脚本
cat > $TEMP_DIR/upload.sh << 'EOF'
#!/bin/bash
# 远程服务器上的上传脚本

set -e

REMOTE_DIR="/opt/fogsight"
BACKUP_DIR="/opt/fogsight/backup_$(date +%Y%m%d_%H%M%S)"

echo "🔄 开始更新 Fogsight 应用..."

# 创建备份
if [ -d "$REMOTE_DIR" ]; then
    echo "📦 创建备份..."
    mkdir -p $BACKUP_DIR
    cp -r $REMOTE_DIR/* $BACKUP_DIR/ 2>/dev/null || true
fi

# 停止服务
echo "🛑 停止服务..."
systemctl stop fogsight || true

# 清理旧文件（保留 outputs 目录）
echo "🧹 清理旧文件..."
rm -rf $REMOTE_DIR/appbook.py
rm -rf $REMOTE_DIR/requirements.txt
rm -rf $REMOTE_DIR/templates
rm -rf $REMOTE_DIR/static

# 复制新文件
echo "📁 复制新文件..."
cp -r fogsight/* $REMOTE_DIR/

# 设置权限
echo "🔐 设置文件权限..."
chown -R fogsight:fogsight $REMOTE_DIR
chmod +x $REMOTE_DIR/appbook.py

# 更新 Python 依赖
echo "📚 更新 Python 依赖..."
cd $REMOTE_DIR
sudo -u fogsight venv/bin/pip install -r requirements.txt

# 启动服务
echo "🚀 启动服务..."
systemctl start fogsight

# 检查服务状态
echo "🔍 检查服务状态..."
sleep 3
if systemctl is-active --quiet fogsight; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败，查看日志："
    journalctl -u fogsight -n 20
    exit 1
fi

echo "🎉 应用更新完成！"
echo "🌐 访问地址: https://$(hostname -I | awk '{print $1}')/"
echo "📚 图书馆页面: https://$(hostname -I | awk '{print $1}')/library"
EOF

chmod +x $TEMP_DIR/upload.sh

# 上传文件到服务器
echo -e "${YELLOW}📤 上传文件到服务器...${NC}"
scp -P $SERVER_PORT -r $TEMP_DIR/* $SERVER_USER@$SERVER_IP:/tmp/

# 在服务器上执行上传脚本
echo -e "${YELLOW}🔧 在服务器上执行更新...${NC}"
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "cd /tmp && chmod +x upload.sh && ./upload.sh"

# 清理临时文件
echo -e "${YELLOW}🧹 清理临时文件...${NC}"
rm -rf $TEMP_DIR
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "rm -rf /tmp/fogsight /tmp/upload.sh"

echo -e "${GREEN}✅ 上传完成！${NC}"
echo ""
echo -e "${GREEN}📋 服务信息：${NC}"
echo "🌐 主页面: https://$SERVER_IP/"
echo "📚 图书馆: https://$SERVER_IP/library"
echo "🔧 服务状态: ssh $SERVER_USER@$SERVER_IP 'systemctl status fogsight'"
echo "📝 查看日志: ssh $SERVER_USER@$SERVER_IP 'journalctl -u fogsight -f'"
echo ""
echo -e "${YELLOW}⚠️  注意事项：${NC}"
echo "1. 如果使用了 credentials.json 模板，请编辑文件配置真实的 API 密钥"
echo "2. 当前使用自签名证书，浏览器会显示安全警告"
echo "3. 生产环境建议使用正式的 SSL 证书" 