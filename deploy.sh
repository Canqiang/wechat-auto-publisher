
#!/bin/bash

echo "🚀 开始部署微信公众号自动运营系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p data/logs data/articles data/images

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cat > .env << EOF
# LLM API配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
CLAUDE_API_KEY=your-claude-api-key
CLAUDE_BASE_URL=https://api.anthropic.com

# 微信公众号配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# 数据库配置
DATABASE_URL=postgresql://user:password@db:5432/wechat_auto

# 图片生成配置
DALLE_API_KEY=your-dalle-api-key
STABLE_DIFFUSION_API=your-sd-api-url

# Redis配置
REDIS_URL=redis://redis:6379/0
EOF
    echo "⚠️  请编辑 .env 文件，填入您的API密钥"
    exit 1
fi

# 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️ 初始化数据库..."
docker-compose exec backend python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ 数据库初始化成功')
"

echo "✅ 部署完成！"
echo "📱 管理界面: http://localhost:3000"