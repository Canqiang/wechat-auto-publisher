
import re
from typing import Dict, List

def validate_article(article: Dict) -> List[str]:
    """验证文章内容"""
    errors = []
    
    # 检查标题
    if not article.get('title'):
        errors.append('文章标题不能为空')
    elif len(article['title']) > 64:
        errors.append('文章标题不能超过64个字符')
    
    # 检查内容
    if not article.get('content'):
        errors.append('文章内容不能为空')
    elif len(article['content']) < 100:
        errors.append('文章内容至少需要100个字符')
    elif len(article['content']) > 20000:
        errors.append('文章内容不能超过20000个字符')
    
    # 检查封面图
    if article.get('cover_image'):
        if not is_valid_image_url(article['cover_image']):
            errors.append('封面图URL格式不正确')
    
    return errors

def is_valid_image_url(url: str) -> bool:
    """验证图片URL"""
    pattern = r'^https?://.+\.(jpg|jpeg|png|gif|webp)(\?.*)?$'
    return bool(re.match(pattern, url, re.IGNORECASE))

def validate_wechat_config(config: Dict) -> List[str]:
    """验证微信配置"""
    errors = []
    
    if not config.get('app_id'):
        errors.append('App ID不能为空')
    elif not config['app_id'].startswith('wx'):
        errors.append('App ID格式不正确')
    
    if not config.get('app_secret'):
        errors.append('App Secret不能为空')
    elif len(config['app_secret']) != 32:
        errors.append('App Secret长度应为32位')
    
    return errors