from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_apscheduler import APScheduler
from datetime import datetime
import logging
import os
import json

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
from models import db, Article
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
    try:
        from services.crawler import ArticleCrawler
        from services.llm_service import LLMService
        
        data = request.json
        source_url = data.get('source_url', '')
        source_type = data.get('source_type', 'auto')
        max_count = data.get('max_count', 5)
        enable_rewrite = data.get('enable_rewrite', True)
        
        if not source_url:
            return jsonify({
                'success': False,
                'message': '请提供爬取源URL'
            }), 400
        
        # 爬取文章
        crawler = ArticleCrawler()
        articles = crawler.crawl(source_url, source_type, max_count)
        
        if not articles:
            return jsonify({
                'success': False,
                'message': '未能爬取到任何内容，请检查URL是否正确'
            }), 400
        
        # LLM改写（如果启用）
        if enable_rewrite:
            llm_service = LLMService()
            articles = llm_service.rewrite_batch(articles)
        
        # 保存到数据库
        saved_articles = []
        for article_data in articles:
            try:
                article = Article(
                    title=article_data.get('title', ''),
                    content=article_data.get('content', ''),
                    status='draft',
                    ai_generated=article_data.get('rewritten', False),
                    source_url=article_data.get('source_url', ''),
                    meta_data=json.dumps({
                        'source_type': article_data.get('source_type', ''),
                        'original_title': article_data.get('original_title', ''),
                        'crawl_time': datetime.now().isoformat(),
                        'rewritten': article_data.get('rewritten', False),
                        'meta': article_data.get('meta', {})
                    })
                )
                db.session.add(article)
                db.session.commit()
                
                saved_articles.append({
                    'id': article.id,
                    'title': article.title,
                    'content': article.content[:200] + '...' if len(article.content) > 200 else article.content,
                    'status': article.status,
                    'source_type': article_data.get('source_type', ''),
                    'rewritten': article_data.get('rewritten', False)
                })
                
            except Exception as e:
                logger.error(f"保存文章失败: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'count': len(saved_articles),
            'articles': saved_articles,
            'message': f'成功爬取并保存 {len(saved_articles)} 篇文章' + 
                      ('（已进行LLM改写）' if enable_rewrite else '')
        })
        
    except Exception as e:
        logger.error(f"爬取文章失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'爬取失败: {str(e)}'
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_article():
    try:
        from services.llm_service import LLMService
        data = request.json
        topic = data.get('topic', '')
        style = data.get('style', 'professional')
        length = data.get('length', 'medium')
        
        if not topic:
            return jsonify({
                'success': False,
                'message': '请提供文章主题'
            }), 400
        
        llm_service = LLMService()
        
        # 构建提示词
        prompts = {
            'short': '写一篇500字左右的短文章',
            'medium': '写一篇1000字左右的中等篇幅文章', 
            'long': '写一篇2000字左右的长文章'
        }
        
        styles = {
            'professional': '专业严谨的风格',
            'casual': '轻松随意的风格',
            'creative': '创意有趣的风格'
        }
        
        prompt = f"请以{styles.get(style, '专业严谨的风格')}，{prompts.get(length, '写一篇1000字左右的中等篇幅文章')}，主题是：{topic}"
        
        # 生成内容
        content = llm_service.generate_content(prompt)
        title = llm_service.generate_title(content)
        
        # 创建文章记录
        article = Article(
            title=title,
            content=content,
            status='draft',
            ai_generated=True
        )
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'article': {
                'id': article.id,
                'title': article.title,
                'content': article.content,
                'status': article.status,
                'created_at': article.created_at.isoformat()
            },
            'message': '文章生成成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成失败: {str(e)}'
        }), 500

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_stats():
    try:
        from services.analytics_service import AnalyticsService
        analytics = AnalyticsService()
        
        # 基础统计
        total_articles = Article.query.count()
        published_articles = Article.query.filter_by(status='published').count()
        draft_articles = Article.query.filter_by(status='draft').count()
        scheduled_articles = Article.query.filter_by(status='scheduled').count()
        
        # 获取最近文章
        recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
        recent_articles_data = [
            {
                'id': article.id,
                'title': article.title,
                'status': article.status,
                'created_at': article.created_at.isoformat(),
                'views': getattr(article, 'views', 0),
                'likes': getattr(article, 'likes', 0), 
                'comments': getattr(article, 'comments', 0)
            }
            for article in recent_articles
        ]
        
        # 获取性能数据
        performance_data = analytics.get_article_performance()
        
        return jsonify({
            'success': True,
            'data': {
                'stats': {
                    'total_articles': total_articles,
                    'published': published_articles,
                    'draft': draft_articles,
                    'scheduled': scheduled_articles
                },
                'recent_articles': recent_articles_data,
                'performance': performance_data,
                'notifications': [
                    {
                        'id': 1,
                        'type': 'success',
                        'title': '系统运行正常',
                        'message': '所有服务运行正常',
                        'time': '刚刚'
                    }
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        }), 500

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