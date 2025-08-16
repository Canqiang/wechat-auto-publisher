from app import scheduler, db
from models import PublishSchedule, Article
from services.llm_service import LLMService
from services.wechat_api import WeChatAPI
from services.crawler import ArticleCrawler
from services.markdown_converter import MarkdownToWeChatHTML
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@scheduler.task('cron', id='auto_generate', hour=9, minute=0)
def auto_generate_article():
    """每天早上9点自动生成文章"""
    try:
        llm = LLMService()
        
        # 获取今日热点话题（可以从热搜API获取）
        topics = get_trending_topics()
        
        for topic in topics[:3]:  # 生成3篇文章
            article_data = llm.generate_article({
                'topic': topic,
                'style': 'informative',
                'length': 1500
            })
            
            if article_data:
                # 转换为HTML
                converter = MarkdownToWeChatHTML()
                html_content = converter.convert(article_data['content'])
                
                # 保存到数据库
                article = Article(
                    title=article_data['title'],
                    content=article_data['content'],
                    markdown_content=article_data['content'],
                    html_content=html_content,
                    status='draft',
                    tags=article_data.get('keywords', [])
                )
                db.session.add(article)
        
        db.session.commit()
        logger.info(f"自动生成{len(topics[:3])}篇文章")
        
    except Exception as e:
        logger.error(f"自动生成文章失败: {str(e)}")

@scheduler.task('cron', id='auto_publish', hour='*/4')
def auto_publish_scheduled():
    """每4小时检查并发布预定的文章"""
    try:
        now = datetime.now()
        schedules = PublishSchedule.query.filter(
            PublishSchedule.scheduled_time <= now,
            PublishSchedule.status == 'pending'
        ).all()
        
        wechat = WeChatAPI()
        
        for schedule in schedules:
            article = schedule.article
            if article.status == 'approved':
                result = wechat.publish(article.to_dict())
                
                if result['success']:
                    article.status = 'published'
                    article.published_at = now
                    schedule.status = 'completed'
                    logger.info(f"成功发布文章: {article.title}")
                else:
                    schedule.status = 'failed'
                    logger.error(f"发布失败: {article.title} - {result['message']}")
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"自动发布失败: {str(e)}")

@scheduler.task('cron', id='crawl_articles', hour=6, minute=0)
def daily_crawl():
    """每天早上6点爬取指定公众号文章"""
    try:
        # 从配置中获取要爬取的公众号列表
        sources = get_crawl_sources()
        crawler = ArticleCrawler()
        llm = LLMService()
        
        for source in sources:
            articles = crawler.crawl_wechat_article(source['url'])
            
            for article_data in articles:
                # 使用LLM改写
                rewritten_content = llm.rewrite_article(
                    article_data['content'],
                    style='creative'
                )
                
                # 转换格式
                converter = MarkdownToWeChatHTML()
                html_content = converter.convert(rewritten_content)
                
                # 保存到数据库
                article = Article(
                    title=article_data['title'],
                    content=rewritten_content,
                    markdown_content=rewritten_content,
                    html_content=html_content,
                    source_url=article_data['source_url'],
                    images=article_data.get('images', []),
                    status='draft'
                )
                db.session.add(article)
        
        db.session.commit()
        logger.info(f"爬取并改写了{len(articles)}篇文章")
        
    except Exception as e:
        logger.error(f"爬取文章失败: {str(e)}")

def get_trending_topics():
    """获取热门话题"""
    # 这里可以接入微博热搜、百度热搜等API
    # 示例返回
    return [
        "人工智能最新进展",
        "健康生活方式",
        "投资理财技巧"
    ]

def get_crawl_sources():
    """获取爬取源配置"""
    from models import Config
    sources = Config.query.filter_by(key='crawl_sources').first()
    if sources:
        import json
        return json.loads(sources.value)
    return []