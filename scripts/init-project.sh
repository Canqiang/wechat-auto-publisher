#!/bin/bash

# 微信公众号自动运营系统初始化脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_NAME="微信公众号自动运营系统"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env.example"

echo -e "${BLUE}🚀 $PROJECT_NAME 初始化脚本${NC}"
echo "=================================================="

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}1. 检查系统依赖...${NC}"
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装，请先安装Docker${NC}"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装，请先安装Docker Compose${NC}"
        exit 1
    fi
    
    # 检查OpenSSL（用于生成SSL证书）
    if ! command -v openssl &> /dev/null; then
        echo -e "${YELLOW}⚠️  OpenSSL 未安装，将跳过SSL证书生成${NC}"
        SKIP_SSL=true
    fi
    
    echo -e "${GREEN}✅ 系统依赖检查完成${NC}"
}

# 创建环境变量文件
create_env_file() {
    echo -e "${YELLOW}2. 创建环境变量文件...${NC}"
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE_FILE" ]; then
            cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
            echo -e "${GREEN}✅ 已从 $ENV_EXAMPLE_FILE 创建 $ENV_FILE${NC}"
        else
            echo -e "${RED}❌ $ENV_EXAMPLE_FILE 不存在${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  $ENV_FILE 已存在，跳过创建${NC}"
    fi
    
    echo -e "${BLUE}📝 请编辑 $ENV_FILE 文件，配置以下信息：${NC}"
    echo "   - OpenAI/Claude API Key"
    echo "   - 微信公众号 App ID 和 App Secret"
    echo "   - 数据库密码等"
}

# 创建必要目录
create_directories() {
    echo -e "${YELLOW}3. 创建项目目录...${NC}"
    
    directories=(
        "data/logs"
        "data/images"
        "data/articles"
        "data/uploads"
        "ssl"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo "   创建目录: $dir"
        fi
    done
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 生成SSL证书
generate_ssl_cert() {
    if [ "$SKIP_SSL" = true ]; then
        echo -e "${YELLOW}4. 跳过SSL证书生成${NC}"
        return
    fi
    
    echo -e "${YELLOW}4. 生成SSL证书...${NC}"
    
    if [ -f "scripts/generate-ssl.sh" ]; then
        chmod +x scripts/generate-ssl.sh
        ./scripts/generate-ssl.sh
    else
        echo -e "${RED}❌ SSL证书生成脚本不存在${NC}"
    fi
}

# 构建Docker镜像
build_images() {
    echo -e "${YELLOW}5. 构建Docker镜像...${NC}"
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "   构建后端镜像..."
        docker-compose build backend
        
        echo "   构建前端镜像..."
        docker-compose build frontend
        
        echo -e "${GREEN}✅ Docker镜像构建完成${NC}"
    else
        echo -e "${RED}❌ $DOCKER_COMPOSE_FILE 不存在${NC}"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    echo -e "${YELLOW}6. 初始化数据库...${NC}"
    
    # 启动数据库服务
    docker-compose up -d db
    echo "   等待数据库启动..."
    sleep 10
    
    # 执行初始化SQL
    if [ -f "data/sql/init.sql" ]; then
        docker-compose exec -T db psql -U user -d wechat_auto -f /var/lib/postgresql/data/init.sql
        echo -e "${GREEN}✅ 数据库初始化完成${NC}"
    else
        echo -e "${YELLOW}⚠️  初始化SQL文件不存在，跳过数据库初始化${NC}"
    fi
}

# 启动服务
start_services() {
    echo -e "${YELLOW}7. 启动所有服务...${NC}"
    
    docker-compose up -d
    
    echo "   等待服务启动..."
    sleep 15
    
    # 检查服务状态
    echo -e "${BLUE}📊 服务状态：${NC}"
    docker-compose ps
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "=================================================="
    echo -e "${GREEN}🎉 $PROJECT_NAME 初始化完成！${NC}"
    echo "=================================================="
    echo -e "${BLUE}访问信息：${NC}"
    echo "   🌐 前端界面: https://localhost"
    echo "   🔧 API接口: https://localhost/api"
    echo "   📊 系统监控: http://localhost:8080/nginx_status"
    echo ""
    echo -e "${BLUE}默认账号：${NC}"
    echo "   👤 用户名: admin"
    echo "   🔑 密码: admin123"
    echo ""
    echo -e "${YELLOW}⚠️  注意事项：${NC}"
    echo "   1. 首次访问可能需要接受自签名证书"
    echo "   2. 请及时修改默认密码"
    echo "   3. 请在设置中配置API密钥"
    echo ""
    echo -e "${BLUE}常用命令：${NC}"
    echo "   启动服务: docker-compose up -d"
    echo "   停止服务: docker-compose down"
    echo "   查看日志: docker-compose logs -f"
    echo "   重新构建: docker-compose build"
    echo ""
    echo -e "${GREEN}祝您使用愉快！🎊${NC}"
}

# 错误处理
handle_error() {
    echo -e "${RED}❌ 初始化过程中出现错误！${NC}"
    echo "请检查错误信息并重新运行脚本。"
    exit 1
}

# 主函数
main() {
    # 设置错误处理
    trap handle_error ERR
    
    # 执行初始化步骤
    check_dependencies
    create_env_file
    create_directories
    generate_ssl_cert
    build_images
    init_database
    start_services
    show_access_info
}

# 确认执行
echo -e "${YELLOW}即将开始初始化 $PROJECT_NAME${NC}"
echo "这将会："
echo "  - 检查系统依赖"
echo "  - 创建必要的文件和目录"
echo "  - 生成SSL证书"
echo "  - 构建Docker镜像"
echo "  - 初始化数据库"
echo "  - 启动所有服务"
echo ""
read -p "确认继续吗？(y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    main
else
    echo "初始化已取消。"
    exit 0
fi
