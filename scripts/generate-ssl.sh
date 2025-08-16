#!/bin/bash

# SSL证书生成脚本
# 用于开发环境的自签名证书生成

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
SSL_DIR="./ssl"
COUNTRY="CN"
STATE="Beijing"
CITY="Beijing"
ORGANIZATION="WeChat Auto Publisher"
UNIT="IT Department"
COMMON_NAME="localhost"
EMAIL="admin@localhost"

echo -e "${GREEN}🔐 生成SSL证书...${NC}"

# 创建SSL目录
mkdir -p $SSL_DIR

# 生成私钥
echo -e "${YELLOW}1. 生成私钥...${NC}"
openssl genpkey -algorithm RSA -out $SSL_DIR/key.pem -pkcs8 -pass pass:

# 生成证书签名请求 (CSR)
echo -e "${YELLOW}2. 生成证书签名请求...${NC}"
openssl req -new -key $SSL_DIR/key.pem -out $SSL_DIR/cert.csr -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"

# 生成自签名证书
echo -e "${YELLOW}3. 生成自签名证书...${NC}"
openssl x509 -req -days 365 -in $SSL_DIR/cert.csr -signkey $SSL_DIR/key.pem -out $SSL_DIR/cert.pem -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
)

# 清理临时文件
rm $SSL_DIR/cert.csr

# 设置权限
chmod 600 $SSL_DIR/key.pem
chmod 644 $SSL_DIR/cert.pem

echo -e "${GREEN}✅ SSL证书生成成功！${NC}"
echo -e "${YELLOW}证书位置: $SSL_DIR/cert.pem${NC}"
echo -e "${YELLOW}私钥位置: $SSL_DIR/key.pem${NC}"
echo -e "${YELLOW}有效期: 365天${NC}"
echo ""
echo -e "${RED}⚠️  注意：这是自签名证书，仅适用于开发环境！${NC}"
echo -e "${RED}   生产环境请使用来自受信任CA的证书。${NC}"
