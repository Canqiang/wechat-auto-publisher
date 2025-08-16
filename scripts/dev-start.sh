#!/bin/bash

# 开发环境启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 启动微信公众号自动运营系统 - 开发模式${NC}"
echo "=================================================="

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 创建环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 创建环境变量文件...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ 已创建 .env 文件，请编辑配置API密钥${NC}"
fi

# 启动开发服务
echo -e "${YELLOW}🔧 启动开发服务...${NC}"

# 启动后端 (在后台)
echo -e "${BLUE}启动后端服务...${NC}"
cd backend
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py > ../data/logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端 (在后台)
echo -e "${BLUE}启动前端服务...${NC}"
cd frontend
npm start > ../data/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}🎉 开发服务启动成功！${NC}"
echo "=================================================="
echo -e "${BLUE}访问地址：${NC}"
echo "   🌐 前端开发服务器: http://localhost:3000"
echo "   🔧 后端API服务: http://localhost:8000"
echo "   📄 API健康检查: http://localhost:8000/api/health"
echo ""
echo -e "${BLUE}日志文件：${NC}"
echo "   📋 后端日志: data/logs/backend.log"
echo "   📋 前端日志: data/logs/frontend.log"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   - 编辑 .env 文件配置API密钥"
echo "   - 按 Ctrl+C 停止所有服务"
echo ""

# 创建停止脚本
cat > scripts/dev-stop.sh << 'EOF'
#!/bin/bash
echo "🛑 停止开发服务..."
pkill -f "python app.py"
pkill -f "npm start"
echo "✅ 所有服务已停止"
EOF
chmod +x scripts/dev-stop.sh

# 等待用户中断
trap 'echo -e "\n${YELLOW}🛑 正在停止服务...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e "${GREEN}✅ 所有服务已停止${NC}"; exit 0' INT

echo -e "${GREEN}服务正在运行中... 按 Ctrl+C 停止${NC}"

# 监控服务状态
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ 后端服务异常退出${NC}"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ 前端服务异常退出${NC}"
        break
    fi
    sleep 5
done
