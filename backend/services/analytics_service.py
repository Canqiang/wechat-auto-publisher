
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import random
from sqlalchemy import func, desc
from models import Article, PublishSchedule, db

logger = logging.getLogger(__name__)

class AnalyticsService:
    """数据分析服务"""
    
    def __init__(self):
        self.db = db
    
    def get_article_performance(self, article_id: int) -> Dict:
        """获取文章表现数据"""
        try:
            article = Article.query.get(article_id)
            if not article:
                return {}
                
            # 从数据库获取实际数据，这里暂时使用模拟数据
            # 实际项目中这些数据应该从微信API或数据库中获取
            performance_data = {
                'article_id': article_id,
                'title': article.title,
                'publish_date': article.published_at.isoformat() if article.published_at else None,
                'views': self._get_mock_views(article_id),
                'likes': self._get_mock_likes(article_id),
                'comments': self._get_mock_comments(article_id),
                'shares': self._get_mock_shares(article_id),
                'read_time_avg': self._calculate_read_time(article.content),
                'bounce_rate': self._calculate_bounce_rate(article_id),
                'engagement_rate': self._calculate_engagement_rate(article_id),
                'peak_hours': self._get_peak_reading_hours(article_id),
                'audience_demographics': self._get_audience_demographics(article_id)
            }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"获取文章数据失败: {str(e)}")
            return {}
    
    def _get_mock_views(self, article_id: int) -> int:
        """模拟阅读量数据"""
        import random
        return random.randint(1000, 10000)
    
    def _get_mock_likes(self, article_id: int) -> int:
        """模拟点赞数据"""
        import random
        return random.randint(50, 500)
    
    def _get_mock_comments(self, article_id: int) -> int:
        """模拟评论数据"""
        import random
        return random.randint(10, 100)
    
    def _get_mock_shares(self, article_id: int) -> int:
        """模拟分享数据"""
        import random
        return random.randint(20, 200)
    
    def _calculate_read_time(self, content: str) -> int:
        """计算平均阅读时间（秒）"""
        # 假设平均阅读速度为每分钟300字
        word_count = len(content)
        read_time = (word_count / 300) * 60
        return int(read_time)
    
    def _calculate_bounce_rate(self, article_id: int) -> float:
        """计算跳出率"""
        import random
        return round(random.uniform(0.15, 0.45), 2)
    
    def _calculate_engagement_rate(self, article_id: int) -> float:
        """计算互动率"""
        views = self._get_mock_views(article_id)
        likes = self._get_mock_likes(article_id)
        comments = self._get_mock_comments(article_id)
        shares = self._get_mock_shares(article_id)
        
        engagement = likes + comments + shares
        return round(engagement / views, 3) if views > 0 else 0
    
    def _get_peak_reading_hours(self, article_id: int) -> List[int]:
        """获取阅读高峰时段"""
        import random
        peak_hours = []
        for _ in range(3):
            hour = random.randint(0, 23)
            if hour not in peak_hours:
                peak_hours.append(hour)
        return sorted(peak_hours)
    
    def _get_audience_demographics(self, article_id: int) -> Dict:
        """获取读者画像数据"""
        return {
            'age_groups': {
                '18-25': 0.25,
                '26-35': 0.40,
                '36-45': 0.25,
                '46+': 0.10
            },
            'gender': {
                'male': 0.55,
                'female': 0.45
            },
            'regions': {
                '北京': 0.15,
                '上海': 0.12,
                '广州': 0.10,
                '深圳': 0.08,
                '其他': 0.55
            }
        }
    
    def get_best_publish_time(self) -> List[Dict]:
        """分析最佳发布时间"""
        try:
            # 从数据库获取已发布文章的时间和表现数据
            published_articles = Article.query.filter(
                Article.status == 'published',
                Article.published_at.isnot(None)
            ).all()
            
            if not published_articles:
                # 返回默认推荐时间
                return self._get_default_publish_times()
            
            # 按星期和小时统计表现
            time_performance = {}
            
            for article in published_articles:
                publish_time = article.published_at
                weekday = publish_time.strftime('%A')
                hour = publish_time.hour
                
                key = f"{weekday}_{hour}"
                if key not in time_performance:
                    time_performance[key] = {
                        'day': weekday,
                        'hour': hour,
                        'articles': [],
                        'total_engagement': 0
                    }
                
                # 模拟计算互动率
                engagement = self._calculate_engagement_rate(article.id)
                time_performance[key]['articles'].append(article.id)
                time_performance[key]['total_engagement'] += engagement
            
            # 计算平均表现并排序
            best_times = []
            for key, data in time_performance.items():
                avg_engagement = data['total_engagement'] / len(data['articles'])
                best_times.append({
                    'day': data['day'],
                    'hour': data['hour'],
                    'engagement': round(avg_engagement, 3),
                    'sample_size': len(data['articles'])
                })
            
            # 按互动率排序，返回前5个
            best_times.sort(key=lambda x: x['engagement'], reverse=True)
            return best_times[:5]
            
        except Exception as e:
            logger.error(f"分析发布时间失败: {str(e)}")
            return self._get_default_publish_times()
    
    def _get_default_publish_times(self) -> List[Dict]:
        """获取默认推荐发布时间"""
        return [
            {'day': 'Monday', 'hour': 9, 'engagement': 0.25, 'sample_size': 0},
            {'day': 'Wednesday', 'hour': 14, 'engagement': 0.22, 'sample_size': 0},
            {'day': 'Friday', 'hour': 20, 'engagement': 0.28, 'sample_size': 0},
            {'day': 'Sunday', 'hour': 10, 'engagement': 0.30, 'sample_size': 0}
        ]
    
    def get_content_recommendations(self) -> List[Dict]:
        """获取内容推荐"""
        try:
            # 分析表现最好的文章标签
            top_performing_articles = Article.query.filter(
                Article.status == 'published',
                Article.tags.isnot(None)
            ).order_by(desc(Article.created_at)).limit(50).all()
            
            if not top_performing_articles:
                return self._get_default_content_recommendations()
            
            # 统计标签频率和表现
            tag_performance = {}
            for article in top_performing_articles:
                if article.tags:
                    engagement = self._calculate_engagement_rate(article.id)
                    for tag in article.tags:
                        if tag not in tag_performance:
                            tag_performance[tag] = {
                                'count': 0,
                                'total_engagement': 0,
                                'articles': []
                            }
                        tag_performance[tag]['count'] += 1
                        tag_performance[tag]['total_engagement'] += engagement
                        tag_performance[tag]['articles'].append(article.id)
            
            # 计算推荐话题
            recommendations = []
            for tag, data in tag_performance.items():
                if data['count'] >= 3:  # 至少有3篇文章
                    avg_engagement = data['total_engagement'] / data['count']
                    trend = self._analyze_topic_trend(tag, data['articles'])
                    
                    recommendations.append({
                        'topic': tag,
                        'trend': trend,
                        'predicted_engagement': round(avg_engagement, 3),
                        'keywords': self._extract_keywords_for_topic(tag),
                        'sample_size': data['count'],
                        'confidence': min(1.0, data['count'] / 10)  # 置信度
                    })
            
            # 按预期互动率排序
            recommendations.sort(key=lambda x: x['predicted_engagement'], reverse=True)
            return recommendations[:10]
            
        except Exception as e:
            logger.error(f"获取内容推荐失败: {str(e)}")
            return self._get_default_content_recommendations()
    
    def _get_default_content_recommendations(self) -> List[Dict]:
        """获取默认内容推荐"""
        return [
            {
                'topic': 'AI应用实践',
                'trend': 'rising',
                'predicted_engagement': 0.35,
                'keywords': ['ChatGPT', '自动化', '效率提升'],
                'sample_size': 0,
                'confidence': 0.5
            },
            {
                'topic': '投资理财策略',
                'trend': 'stable',
                'predicted_engagement': 0.28,
                'keywords': ['基金', '股票', '资产配置'],
                'sample_size': 0,
                'confidence': 0.5
            },
            {
                'topic': '健康生活方式',
                'trend': 'rising',
                'predicted_engagement': 0.32,
                'keywords': ['运动', '饮食', '睡眠'],
                'sample_size': 0,
                'confidence': 0.5
            }
        ]
    
    def _analyze_topic_trend(self, topic: str, article_ids: List[int]) -> str:
        """分析话题趋势"""
        # 简化的趋势分析，实际中可以使用更复杂的算法
        import random
        trends = ['rising', 'stable', 'declining']
        return random.choice(trends)
    
    def _extract_keywords_for_topic(self, topic: str) -> List[str]:
        """为话题提取关键词"""
        # 简化版本，实际中可以使用NLP技术
        keyword_map = {
            'AI': ['人工智能', '机器学习', '深度学习', 'ChatGPT'],
            '投资': ['基金', '股票', '理财', '资产配置'],
            '健康': ['运动', '饮食', '睡眠', '养生'],
            '科技': ['创新', '数字化', '互联网', '技术'],
            '职场': ['工作', '职业发展', '技能', '管理']
        }
        
        for key, keywords in keyword_map.items():
            if key in topic:
                return keywords
        
        return [topic]
    
    def generate_report(self, period: str = 'weekly') -> Dict:
        """生成运营报告"""
        try:
            # 计算时间范围
            if period == 'weekly':
                date_range = '过去7天'
                start_date = datetime.now() - timedelta(days=7)
            elif period == 'monthly':
                date_range = '过去30天'
                start_date = datetime.now() - timedelta(days=30)
            elif period == 'daily':
                date_range = '今天'
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                date_range = '过去7天'
                start_date = datetime.now() - timedelta(days=7)
            
            # 获取时间范围内的文章
            articles_in_period = Article.query.filter(
                Article.published_at >= start_date,
                Article.status == 'published'
            ).all()
            
            # 计算总览数据
            total_articles = len(articles_in_period)
            total_views = sum(self._get_mock_views(article.id) for article in articles_in_period)
            total_engagement = sum(
                self._get_mock_likes(article.id) + 
                self._get_mock_comments(article.id) + 
                self._get_mock_shares(article.id)
                for article in articles_in_period
            )
            
            # 获取表现最好的文章
            top_articles = []
            for article in articles_in_period:
                views = self._get_mock_views(article.id)
                top_articles.append({
                    'id': article.id,
                    'title': article.title,
                    'views': views,
                    'engagement': self._calculate_engagement_rate(article.id),
                    'publish_date': article.published_at.strftime('%Y-%m-%d')
                })
            
            top_articles.sort(key=lambda x: x['views'], reverse=True)
            top_articles = top_articles[:5]
            
            # 计算增长数据（与上一个周期对比）
            prev_start = start_date - (datetime.now() - start_date)
            prev_articles = Article.query.filter(
                Article.published_at >= prev_start,
                Article.published_at < start_date,
                Article.status == 'published'
            ).all()
            
            prev_views = sum(self._get_mock_views(article.id) for article in prev_articles)
            prev_engagement = sum(
                self._get_mock_likes(article.id) + 
                self._get_mock_comments(article.id) + 
                self._get_mock_shares(article.id)
                for article in prev_articles
            )
            
            views_growth = self._calculate_growth_rate(total_views, prev_views)
            engagement_growth = self._calculate_growth_rate(total_engagement, prev_engagement)
            
            # 生成建议
            recommendations = self._generate_recommendations(articles_in_period)
            
            return {
                'period': date_range,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
                'summary': {
                    'total_articles': total_articles,
                    'total_views': total_views,
                    'total_engagement': total_engagement,
                    'avg_views_per_article': total_views // max(1, total_articles),
                    'avg_engagement_rate': round(total_engagement / max(1, total_views), 3),
                    'avg_read_time': sum(self._calculate_read_time(article.content) for article in articles_in_period) // max(1, total_articles)
                },
                'top_articles': top_articles,
                'growth': {
                    'views': views_growth,
                    'engagement': engagement_growth,
                    'articles': f"+{total_articles - len(prev_articles)}"
                },
                'content_analysis': self._analyze_content_performance(articles_in_period),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            return self._get_default_report()
    
    def _calculate_growth_rate(self, current: int, previous: int) -> str:
        """计算增长率"""
        if previous == 0:
            return "+100%" if current > 0 else "0%"
        
        growth = ((current - previous) / previous) * 100
        sign = "+" if growth > 0 else ""
        return f"{sign}{growth:.1f}%"
    
    def _analyze_content_performance(self, articles: List) -> Dict:
        """分析内容表现"""
        if not articles:
            return {}
        
        # 按标签分析
        tag_performance = {}
        for article in articles:
            if article.tags:
                for tag in article.tags:
                    if tag not in tag_performance:
                        tag_performance[tag] = {
                            'count': 0,
                            'total_views': 0,
                            'total_engagement': 0
                        }
                    
                    tag_performance[tag]['count'] += 1
                    tag_performance[tag]['total_views'] += self._get_mock_views(article.id)
                    tag_performance[tag]['total_engagement'] += (
                        self._get_mock_likes(article.id) + 
                        self._get_mock_comments(article.id) + 
                        self._get_mock_shares(article.id)
                    )
        
        # 计算平均表现
        for tag, data in tag_performance.items():
            data['avg_views'] = data['total_views'] // data['count']
            data['avg_engagement'] = data['total_engagement'] // data['count']
        
        return {
            'by_topic': tag_performance,
            'total_topics': len(tag_performance),
            'most_popular_topic': max(tag_performance.keys(), key=lambda k: tag_performance[k]['avg_views']) if tag_performance else None
        }
    
    def _generate_recommendations(self, articles: List) -> List[str]:
        """生成运营建议"""
        recommendations = []
        
        if not articles:
            recommendations.append("建议开始发布更多内容以获得数据洞察")
            return recommendations
        
        # 分析发布频率
        if len(articles) < 3:
            recommendations.append("建议增加发布频率，保持与读者的互动")
        
        # 分析内容长度
        avg_length = sum(len(article.content) for article in articles) / len(articles)
        if avg_length < 500:
            recommendations.append("文章内容偏短，建议增加深度和详细度")
        elif avg_length > 3000:
            recommendations.append("文章内容较长，建议适当精简或分段发布")
        
        # 分析图片使用
        articles_with_images = sum(1 for article in articles if article.images)
        if articles_with_images / len(articles) < 0.5:
            recommendations.append("建议为更多文章添加配图，提升阅读体验")
        
        # 分析发布时间
        publish_hours = [article.published_at.hour for article in articles if article.published_at]
        if publish_hours:
            from collections import Counter
            hour_counts = Counter(publish_hours)
            most_common_hour = hour_counts.most_common(1)[0][0]
            if most_common_hour < 8 or most_common_hour > 22:
                recommendations.append(f"当前主要在{most_common_hour}点发布，建议尝试黄金时段（8-22点）")
        
        return recommendations[:5]  # 最多返回5条建议
    
    def _get_default_report(self) -> Dict:
        """获取默认报告"""
        return {
            'period': '暂无数据',
            'summary': {
                'total_articles': 0,
                'total_views': 0,
                'total_engagement': 0,
                'avg_views_per_article': 0,
                'avg_engagement_rate': 0,
                'avg_read_time': 0
            },
            'top_articles': [],
            'growth': {
                'views': '0%',
                'engagement': '0%',
                'articles': '0'
            },
            'content_analysis': {},
            'recommendations': ['请先发布一些文章以获得数据分析']
        }
    
    def get_competitor_analysis(self, competitor_urls: List[str]) -> Dict:
        """竞品分析"""
        try:
            # 这里可以集成爬虫来分析竞品数据
            # 暂时返回模拟数据
            analysis = {
                'competitors': [],
                'comparison': {
                    'avg_engagement': {},
                    'popular_topics': [],
                    'posting_frequency': {}
                },
                'insights': []
            }
            
            for i, url in enumerate(competitor_urls[:5]):
                competitor_data = {
                    'name': f'竞品{i+1}',
                    'url': url,
                    'avg_posts_per_week': 5 + i,
                    'estimated_engagement': round(0.1 + i * 0.05, 2),
                    'top_topics': ['科技', '生活', '教育'][i % 3],
                    'follower_growth': f'+{10 + i * 5}%'
                }
                analysis['competitors'].append(competitor_data)
            
            analysis['insights'] = [
                '竞品平均每周发布5-9篇文章',
                '科技类话题互动率较高',
                '工作日发布频率更高',
                '图文并茂的内容更受欢迎'
            ]
            
            return analysis
            
        except Exception as e:
            logger.error(f"竞品分析失败: {str(e)}")
            return {}
    
    def predict_article_performance(self, article_data: Dict) -> Dict:
        """预测文章表现"""
        try:
            # 基于历史数据预测文章表现
            # 这里使用简化的预测模型
            
            title_length = len(article_data.get('title', ''))
            content_length = len(article_data.get('content', ''))
            has_images = bool(article_data.get('images'))
            tags = article_data.get('tags', [])
            
            # 简化的评分算法
            score = 50  # 基础分
            
            # 标题长度影响
            if 10 <= title_length <= 30:
                score += 10
            elif title_length > 30:
                score -= 5
            
            # 内容长度影响
            if 800 <= content_length <= 2000:
                score += 15
            elif content_length < 500:
                score -= 10
            elif content_length > 3000:
                score -= 5
            
            # 图片影响
            if has_images:
                score += 10
            
            # 标签影响
            if tags:
                score += min(len(tags) * 3, 15)
            
            # 预测具体数值
            predicted_views = max(100, score * 20 + random.randint(-500, 500))
            predicted_likes = max(10, predicted_views // 15 + random.randint(-20, 20))
            predicted_comments = max(2, predicted_likes // 8 + random.randint(-5, 5))
            predicted_shares = max(5, predicted_likes // 5 + random.randint(-10, 10))
            
            engagement_rate = (predicted_likes + predicted_comments + predicted_shares) / predicted_views
            
            return {
                'overall_score': min(100, max(0, score)),
                'predicted_performance': {
                    'views': predicted_views,
                    'likes': predicted_likes,
                    'comments': predicted_comments,
                    'shares': predicted_shares,
                    'engagement_rate': round(engagement_rate, 3)
                },
                'improvement_suggestions': self._get_improvement_suggestions(score, article_data),
                'confidence': 0.7  # 预测置信度
            }
            
        except Exception as e:
            logger.error(f"预测文章表现失败: {str(e)}")
            return {}
    
    def _get_improvement_suggestions(self, score: int, article_data: Dict) -> List[str]:
        """获取改进建议"""
        suggestions = []
        
        title_length = len(article_data.get('title', ''))
        content_length = len(article_data.get('content', ''))
        has_images = bool(article_data.get('images'))
        tags = article_data.get('tags', [])
        
        if title_length < 10:
            suggestions.append("标题过短，建议扩展为10-30字")
        elif title_length > 30:
            suggestions.append("标题过长，建议精简到30字以内")
        
        if content_length < 500:
            suggestions.append("内容过短，建议增加详细说明和案例")
        elif content_length > 3000:
            suggestions.append("内容较长，建议分段或拆分为系列文章")
        
        if not has_images:
            suggestions.append("建议添加相关配图提升阅读体验")
        
        if not tags:
            suggestions.append("建议添加相关标签增加文章曝光度")
        
        if score < 60:
            suggestions.append("整体评分偏低，建议优化标题和内容结构")
        
        return suggestions[:5]  # 最多返回5条建议
