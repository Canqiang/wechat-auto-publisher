# 微信公众号自动运营系统

<div align="center">

![Logo](https://img.shields.io/badge/WeChatAuto-Publisher-blue?style=for-the-badge&logo=wechat)

[![GitHub Stars](https://img.shields.io/github/stars/Canqiang/wechat-auto-publisher?style=social)](https://github.com/Canqiang/wechat-auto-publisher/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Canqiang/wechat-auto-publisher?style=social)](https://github.com/Canqiang/wechat-auto-publisher/network/members)


[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**一个功能完整的微信公众号自动运营系统，支持AI内容生成、智能改写、定时发布等功能**

[快速开始](#快速开始) • [功能特性](#功能特性) • [部署指南](#部署指南) • [API文档](#api文档) • [贡献指南](#贡献指南)

</div>

## 📋 目录

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [使用教程](#使用教程)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性

### 🤖 AI内容生成
- 支持 OpenAI GPT-4/3.5 和 Claude 3 系列模型
- 自定义 API Base URL，支持各种 API 代理
- 智能内容生成，可配置风格、长度、关键词
- 自动标题生成和内容优化

### 🕷️ 智能爬虫改写
- 爬取指定公众号文章内容
- AI智能改写，保持原意的同时避免重复
- 自动保留和优化配图
- 支持批量爬取和定时任务

### 🎨 图片处理功能
- 集成 DALL-E 3 和 Stable Diffusion
- 自动生成文章封面图
- 图片压缩和格式优化
- 支持图片拼贴和排版

### 📝 Markdown转换
- 专为微信公众号优化的HTML转换
- 美观的样式模板和排版
- 代码高亮和表格支持
- 响应式设计适配

### ⏰ 定时发布系统
- 可视化发布计划管理
- 支持单次和周期性发布
- 最佳发布时间分析
- 自动发布状态监控

### 📊 数据分析dashboard
- 文章表现数据统计
- 阅读量、点赞、评论分析
- 内容推荐和趋势分析
- 运营报告生成

### 🎛️ Web管理界面
- 现代化的React前端界面
- 响应式设计，支持移动端
- 实时数据更新
- 用户权限管理

### 🔒 企业级特性
- Docker容器化部署
- 完整的日志系统
- 异常处理和监控
- 数据备份和恢复
- SSL/HTTPS支持

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ React Frontend  │────│   Nginx Proxy   │────│  External APIs  │
│ (Port: 3000)    │    │  (Port: 80/443) │    │ (OpenAI/Claude) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Flask Backend  │────│  PostgreSQL DB  │    │   Redis Cache   │
│   (Port: 5000)  │    │   (Port: 5432)  │    │   (Port: 6379)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 项目结构

```
wechat-auto-publisher/
├── 📂 backend/                    # 后端服务
│   ├── 📄 app.py                 # Flask主应用
│   ├── 📄 config.py              # 配置管理
│   ├── 📄 models.py              # 数据模型
│   ├── 📄 tasks.py               # 定时任务
│   ├── 📂 services/              # 业务服务
│   │   ├── 📄 llm_service.py     # LLM服务
│   │   ├── 📄 crawler.py         # 爬虫服务
│   │   ├── 📄 image_service.py   # 图片处理
│   │   ├── 📄 wechat_api.py      # 微信API
│   │   ├── 📄 markdown_converter.py # MD转换
│   │   ├── 📄 analytics_service.py  # 数据分析
│   │   └── 📄 content_optimizer.py # 内容优化
│   ├── 📂 utils/                 # 工具类
│   │   ├── 📄 logger.py          # 日志工具
│   │   ├── 📄 exceptions.py      # 异常处理
│   │   └── 📄 validators.py      # 数据验证
│   ├── 📄 requirements.txt       # Python依赖
│   └── 📄 Dockerfile            # 后端容器
├── 📂 frontend/                   # 前端应用
│   ├── 📂 src/
│   │   ├── 📂 components/        # React组件
│   │   ├── 📂 pages/            # 页面组件
│   │   ├── 📂 contexts/         # 状态管理
│   │   ├── 📂 services/         # API服务
│   │   └── 📂 utils/            # 工具函数
│   ├── 📂 public/               # 静态资源
│   ├── 📄 package.json          # Node.js依赖
│   ├── 📄 Dockerfile           # 前端容器
│   └── 📄 nginx.conf           # Nginx配置
├── 📂 data/                      # 数据目录
│   ├── 📂 sql/                  # SQL脚本
│   ├── 📂 logs/                 # 日志文件
│   ├── 📂 images/               # 图片存储
│   └── 📂 uploads/              # 上传文件
├── 📂 scripts/                   # 部署脚本
│   ├── 📄 init-project.sh       # 项目初始化
│   ├── 📄 generate-ssl.sh       # SSL证书生成
│   └── 📄 backup.sh            # 数据备份
├── 📂 ssl/                      # SSL证书
├── 📄 docker-compose.yml        # Docker编排
├── 📄 nginx.conf               # 主Nginx配置
├── 📄 .env.example             # 环境变量示例
└── 📄 README.md                # 项目文档
```

## 🚀 快速开始

### 环境要求

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** 2.0+
- **域名** (可选，用于SSL证书)

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/wechat-auto-publisher.git
cd wechat-auto-publisher

# 2. 运行初始化脚本
chmod +x scripts/init-project.sh
./scripts/init-project.sh

# 3. 编辑环境变量
cp .env.example .env
nano .env  # 配置API密钥等信息

# 4. 启动服务
docker-compose up -d
```

### 手动部署

<details>
<summary>点击展开手动部署步骤</summary>

```bash
# 1. 创建必要目录
mkdir -p data/{logs,images,uploads} ssl

# 2. 生成SSL证书
chmod +x scripts/generate-ssl.sh
./scripts/generate-ssl.sh

# 3. 配置环境变量
cp .env.example .env

# 4. 构建镜像
docker-compose build

# 5. 启动数据库
docker-compose up -d db redis

# 6. 初始化数据库
docker-compose exec db psql -U user -d wechat_auto -f /var/lib/postgresql/data/init.sql

# 7. 启动所有服务
docker-compose up -d
```

</details>

### 访问系统

启动完成后，打开浏览器访问：

- 🌐 **主界面**: https://localhost
- 🔧 **API文档**: https://localhost/api/docs
- 📊 **监控面板**: http://localhost:8080/nginx_status

**默认登录信息**:
- 用户名: `admin`
- 密码: `admin123`

> ⚠️ **重要**: 首次登录后请立即修改默认密码！

## ⚙️ 配置说明

### 环境变量配置

编辑 `.env` 文件，配置以下信息：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/wechat_auto

# OpenAI配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Claude配置  
CLAUDE_API_KEY=sk-ant-your-claude-api-key-here
CLAUDE_BASE_URL=https://api.anthropic.com

# 微信公众号配置
WECHAT_APP_ID=wx1234567890123456
WECHAT_APP_SECRET=your_wechat_app_secret_here

# 图片生成配置
DALLE_API_KEY=your_dalle_api_key_here
STABLE_DIFFUSION_API=https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image
```

### 微信公众号配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "基本配置"
3. 获取 AppID 和 AppSecret
4. 设置服务器配置URL: `https://your-domain.com/api/wechat/callback`
5. 配置IP白名单

### LLM API配置

支持以下AI服务商：

<details>
<summary>OpenAI 配置</summary>

```bash
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
```

</details>

<details>
<summary>Claude 配置</summary>

```bash
CLAUDE_API_KEY=sk-ant-xxx
CLAUDE_BASE_URL=https://api.anthropic.com
```

</details>

<details>
<summary>自定义API配置</summary>

```bash
# 支持兼容OpenAI格式的API
OPENAI_API_KEY=your-custom-key
OPENAI_BASE_URL=https://your-custom-api.com/v1
```

</details>

## 📖 使用教程

### 1. 基础设置

登录后首先完成基础配置：

1. **系统设置** → **LLM配置**：配置AI API密钥
2. **系统设置** → **微信配置**：配置公众号信息
3. **系统设置** → **爬虫配置**：添加爬取源

### 2. 内容创作

#### AI生成文章

```bash
1. 进入"文章管理" → 点击"AI生成"
2. 输入主题和关键词
3. 选择文章风格和长度
4. 点击生成，系统将自动创建文章
```

#### 爬取改写文章

```bash
1. 配置爬取源URL
2. 进入"文章管理" → 点击"爬取文章"
3. 选择要爬取的文章
4. 系统自动改写并保存
```

### 3. 发布管理

#### 即时发布

```bash
1. 在文章列表中选择文章
2. 点击"发布"按钮
3. 确认发布信息
4. 文章将立即发布到公众号
```

#### 定时发布

```bash
1. 进入"发布计划"页面
2. 点击"新建计划"
3. 选择文章和发布时间
4. 设置重复频率（可选）
5. 保存计划，系统将自动执行
```

### 4. 数据分析

系统提供详细的运营数据分析：

- **文章表现**: 阅读量、点赞、评论、分享
- **趋势分析**: 数据变化趋势图表
- **内容推荐**: 基于数据的内容建议
- **最佳时间**: 发布时间效果分析

## 🔧 开发指南

### 本地开发环境

```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# 前端开发
cd frontend
npm install
npm start
```

### API开发

后端API遵循RESTful设计，主要端点：

```
GET    /api/articles          # 获取文章列表
POST   /api/articles          # 创建文章
PUT    /api/articles/{id}     # 更新文章
DELETE /api/articles/{id}     # 删除文章

GET    /api/schedules         # 获取发布计划
POST   /api/schedules         # 创建发布计划

GET    /api/analytics         # 获取分析数据
POST   /api/config            # 保存配置
```

### 扩展开发

系统支持插件化扩展：

1. **自定义LLM服务**: 继承 `LLMService` 基类
2. **新增爬虫源**: 实现 `CrawlerInterface`
3. **扩展数据分析**: 添加新的分析指标
4. **自定义模板**: 修改Markdown转换模板

## 🐳 Docker部署

### 生产环境部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/wechat-auto-publisher.git
cd wechat-auto-publisher

# 2. 配置生产环境变量
cp .env.example .env.prod
# 编辑生产环境配置

# 3. 使用生产配置启动
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. 配置域名和SSL
# 编辑nginx.conf，设置正确的域名
# 使用Let's Encrypt获取正式SSL证书
```

### 服务扩展

```bash
# 扩展后端服务
docker-compose up -d --scale backend=3

# 扩展前端服务
docker-compose up -d --scale frontend=2
```

### 监控和维护

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 备份数据
./scripts/backup.sh

# 更新服务
docker-compose pull
docker-compose up -d
```

## 🔐 安全配置

### SSL/TLS配置

生产环境建议使用正式SSL证书：

```bash
# 使用Certbot获取Let's Encrypt证书
sudo certbot --nginx -d your-domain.com

# 或者使用自定义证书
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

### 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 数据库安全

```bash
# 修改默认密码
docker-compose exec db psql -U user -d wechat_auto
ALTER USER user WITH PASSWORD 'new-strong-password';

# 限制数据库访问
# 编辑docker-compose.yml，移除数据库端口映射
```

## ❓ 常见问题

<details>
<summary><strong>Q: 如何更换AI服务商？</strong></summary>

A: 在系统设置中切换LLM提供商，并配置相应的API密钥和Base URL。系统支持OpenAI、Claude以及兼容OpenAI格式的自定义API。

</details>

<details>
<summary><strong>Q: 爬虫功能不工作怎么办？</strong></summary>

A: 
1. 检查目标网站是否有反爬机制
2. 调整爬虫延迟设置
3. 检查网络连接和代理配置
4. 查看logs目录下的错误日志

</details>

<details>
<summary><strong>Q: 如何备份数据？</strong></summary>

A: 
```bash
# 自动备份
./scripts/backup.sh

# 手动备份数据库
docker-compose exec db pg_dump -U user wechat_auto > backup.sql

# 备份上传文件
tar -czf uploads-backup.tar.gz data/uploads/
```

</details>

<details>
<summary><strong>Q: 微信发布失败怎么办？</strong></summary>

A: 
1. 检查微信公众号配置是否正确
2. 确认IP白名单设置
3. 检查access_token是否有效
4. 查看微信API返回的错误信息

</details>

<details>
<summary><strong>Q: 如何自定义文章模板？</strong></summary>

A: 编辑 `backend/services/markdown_converter.py` 文件中的样式配置，可以自定义微信公众号文章的样式模板。

</details>

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

1. **报告Bug**: 使用GitHub Issues报告问题
2. **功能建议**: 提出新功能需求
3. **代码贡献**: 提交Pull Request
4. **文档改进**: 完善项目文档
5. **测试**: 帮助测试新功能

### 开发流程

```bash
# 1. Fork项目到你的GitHub
# 2. 克隆Fork的项目
git clone https://github.com/your-username/wechat-auto-publisher.git

# 3. 创建特性分支
git checkout -b feature/your-feature-name

# 4. 提交更改
git commit -m "Add: your feature description"

# 5. 推送到分支
git push origin feature/your-feature-name

# 6. 创建Pull Request
```

### 代码规范

- **Python**: 遵循PEP8规范
- **JavaScript**: 使用ESLint配置
- **提交信息**: 使用约定式提交格式
- **文档**: 更新相应的README和注释

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和服务：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [React](https://reactjs.org/) - 前端框架
- [Ant Design](https://ant.design/) - UI组件库
- [PostgreSQL](https://postgresql.org/) - 数据库
- [Docker](https://docker.com/) - 容器化
- [OpenAI](https://openai.com/) - AI服务
- [Anthropic](https://anthropic.com/) - Claude AI

## 📧 联系方式

- **项目主页**: https://github.com/Canqiang/wechat-auto-publisher
- **问题反馈**: https://github.com/Canqiang/wechat-auto-publisher/issues
- **邮箱**: canqiangxu@yeah.net

## 💖 支持项目

如果这个项目对你有帮助，欢迎支持一下作者！你的支持是我持续开发的动力 ❤️

### ⭐ 给项目点个Star

如果你觉得这个项目不错，请在GitHub上给个⭐️，这对我来说意义重大！

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Canqiang/wechat-auto-publisher&type=Date)](https://www.star-history.com/#Canqiang/wechat-auto-publisher&Date)
### 🎯 其他支持方式

- **分享项目**: 帮忙分享给需要的朋友
- **提交Issue**: 发现问题或建议都可以提出
- **贡献代码**: 欢迎提交PR改进项目
- **写使用教程**: 分享你的使用经验

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个⭐️！**

Made with ❤️ by [Canqiang Xu](https://github.com/Canqiang)

</div>

