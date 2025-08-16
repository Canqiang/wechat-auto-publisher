import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LLM API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_BASE_URL = os.getenv('CLAUDE_BASE_URL', 'https://api.anthropic.com')
    
    # 微信公众号配置
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')
    
    # 定时任务配置
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    
    # 爬虫配置
    CRAWLER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    CRAWLER_TIMEOUT = 30
    
    # 图片生成配置
    DALLE_API_KEY = os.getenv('DALLE_API_KEY')
    STABLE_DIFFUSION_API = os.getenv('STABLE_DIFFUSION_API')