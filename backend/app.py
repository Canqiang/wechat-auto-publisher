from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_apscheduler import APScheduler
from datetime import datetime
import logging
import os

# 确保必要目录存在
os.makedirs('data/logs', exist_ok=True)
os.makedirs('data/images', exist_ok=True)
os.makedirs('data/uploads', exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')

# 开发环境强制使用SQLite
if not os.getenv('PRODUCTION'):
    # 使用绝对路径确保数据库创建在正确位置
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# 导入模型和数据库
from models import db
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API路由
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    if request.method == 'GET':
        from models import Config
        configs = Config.query.all()
        return jsonify([c.to_dict() for c in configs])
    else:
        data = request.json
        # 保存配置逻辑
        return jsonify({'message': 'Config saved successfully'})

@app.route('/api/articles', methods=['GET', 'POST'])
def manage_articles():
    if request.method == 'GET':
        from models import Article
        articles = Article.query.order_by(Article.created_at.desc()).all()
        return jsonify([a.to_dict() for a in articles])
    else:
        # 创建新文章
        from services.llm_service import LLMService
        llm = LLMService()
        article = llm.generate_article(request.json)
        return jsonify(article)

@app.route('/api/publish/<int:article_id>', methods=['POST'])
def publish_article(article_id):
    from services.wechat_api import WeChatAPI
    from models import Article
    
    article = Article.query.get_or_404(article_id)
    wechat = WeChatAPI()
    result = wechat.publish(article)
    
    if result['success']:
        article.status = 'published'
        article.published_at = datetime.now()
        db.session.commit()
    
    return jsonify(result)

@app.route('/api/crawl', methods=['POST'])
def crawl_articles():
    from services.crawler import ArticleCrawler
    data = request.json
    crawler = ArticleCrawler()
    articles = crawler.crawl(data.get('source_url'))
    return jsonify({'count': len(articles), 'articles': articles})

# 认证API
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 简单的默认用户认证
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'success': True,
            'token': 'demo-token-12345',
            'user': {
                'id': 1,
                'username': 'admin',
                'role': 'admin',
                'name': '管理员'
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # 简单的注册响应（在实际环境中需要数据库验证）
    if username and password:
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': {
                'id': 2,
                'username': username,
                'email': email,
                'role': 'user'
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名和密码不能为空'
        }), 400

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({
        'success': True,
        'message': '登出成功'
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    # 获取当前用户信息
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token == 'demo-token-12345':
            return jsonify({
                'success': True,
                'user': {
                    'id': 1,
                    'username': 'admin',
                    'role': 'admin',
                    'name': '管理员'
                }
            })
    
    return jsonify({
        'success': False,
        'message': '未授权'
    }), 401

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    # 验证token有效性
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token == 'demo-token-12345':
            return jsonify({
                'success': True,
                'valid': True,
                'user': {
                    'id': 1,
                    'username': 'admin',
                    'role': 'admin',
                    'name': '管理员'
                }
            })
    
    return jsonify({
        'success': False,
        'valid': False,
        'message': 'Invalid token'
    }), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)