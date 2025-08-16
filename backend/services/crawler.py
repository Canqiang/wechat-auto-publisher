import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ArticleCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def crawl_wechat_article(self, url: str) -> Dict:
        """爬取微信公众号文章"""
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文章标题
            title = soup.find('h1', class_='rich_media_title')
            title = title.text.strip() if title else ''
            
            # 提取文章内容
            content_div = soup.find('div', class_='rich_media_content')
            if not content_div:
                return None
            
            # 提取文本内容
            content = self._extract_text(content_div)
            
            # 提取图片
            images = self._extract_images(content_div)
            
            # 提取作者和时间
            meta_info = self._extract_meta(soup)
            
            return {
                'title': title,
                'content': content,
                'images': images,
                'source_url': url,
                'meta': meta_info
            }
            
        except Exception as e:
            logger.error(f"爬取文章失败: {str(e)}")
            return None
    
    def _extract_text(self, content_div) -> str:
        """提取纯文本内容"""
        # 移除script和style标签
        for script in content_div(['script', 'style']):
            script.decompose()
        
        # 获取文本
        text = content_div.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_images(self, content_div) -> List[str]:
        """提取图片URL"""
        images = []
        for img in content_div.find_all('img'):
            src = img.get('data-src') or img.get('src')
            if src:
                images.append(src)
        return images
    
    def _extract_meta(self, soup) -> Dict:
        """提取元信息"""
        meta = {}
        
        # 作者
        author = soup.find('span', class_='rich_media_meta_text')
        if author:
            meta['author'] = author.text.strip()
        
        # 发布时间
        publish_time = soup.find('em', id='publish_time')
        if publish_time:
            meta['publish_time'] = publish_time.text.strip()
        
        return meta
    
    def crawl_multiple(self, urls: List[str]) -> List[Dict]:
        """批量爬取文章"""
        articles = []
        for url in urls:
            article = self.crawl_wechat_article(url)
            if article:
                articles.append(article)
            time.sleep(2)  # 避免频率过高
        return articles