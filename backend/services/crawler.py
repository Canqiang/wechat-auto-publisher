import requests
from bs4 import BeautifulSoup
import re
import time
import json
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import feedparser
from datetime import datetime, timedelta

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
    
    def crawl_website(self, website_url: str, max_articles: int = 5) -> List[Dict]:
        """爬取指定网站的最新文章"""
        try:
            # 首先尝试RSS/Atom feeds
            rss_articles = self._crawl_rss_feed(website_url, max_articles)
            if rss_articles:
                return rss_articles
            
            # 如果没有RSS，尝试解析网站内容
            return self._crawl_website_content(website_url, max_articles)
            
        except Exception as e:
            logger.error(f"爬取网站失败: {str(e)}")
            return []
    
    def _crawl_rss_feed(self, website_url: str, max_articles: int) -> List[Dict]:
        """尝试从RSS/Atom feed爬取"""
        # 常见的RSS路径
        rss_paths = ['/rss', '/feed', '/rss.xml', '/feed.xml', '/atom.xml', '/index.xml']
        
        for path in rss_paths:
            try:
                rss_url = urljoin(website_url, path)
                feed = feedparser.parse(rss_url)
                
                if feed.entries:
                    articles = []
                    for entry in feed.entries[:max_articles]:
                        article = self._parse_rss_entry(entry)
                        if article:
                            articles.append(article)
                    return articles
            except Exception as e:
                logger.debug(f"RSS路径 {path} 失败: {str(e)}")
                continue
        
        return []
    
    def _parse_rss_entry(self, entry) -> Optional[Dict]:
        """解析RSS条目"""
        try:
            title = getattr(entry, 'title', '')
            content = ''
            
            # 尝试获取内容
            if hasattr(entry, 'content'):
                content = entry.content[0].value if entry.content else ''
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            
            # 清理HTML标签
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text().strip()
            
            return {
                'title': title,
                'content': content,
                'source_url': getattr(entry, 'link', ''),
                'source_type': 'rss',
                'published_time': getattr(entry, 'published', ''),
                'meta': {
                    'author': getattr(entry, 'author', ''),
                    'published': getattr(entry, 'published', '')
                }
            }
        except Exception as e:
            logger.error(f"解析RSS条目失败: {str(e)}")
            return None
    
    def _crawl_website_content(self, website_url: str, max_articles: int) -> List[Dict]:
        """爬取网站内容页面"""
        try:
            response = self.session.get(website_url, timeout=30)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章链接 - 常见的文章链接模式
            article_links = self._find_article_links(soup, website_url)
            
            articles = []
            for link in article_links[:max_articles]:
                article = self._crawl_single_page(link)
                if article:
                    articles.append(article)
                time.sleep(1)  # 避免频率过高
            
            return articles
            
        except Exception as e:
            logger.error(f"爬取网站内容失败: {str(e)}")
            return []
    
    def _find_article_links(self, soup, base_url: str) -> List[str]:
        """查找文章链接"""
        links = []
        
        # 常见的文章链接选择器
        selectors = [
            'article a[href]',
            '.post a[href]',
            '.entry a[href]',
            '.article a[href]',
            'h1 a[href]',
            'h2 a[href]',
            'h3 a[href]',
            'a[href*="article"]',
            'a[href*="post"]',
            'a[href*="/p/"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    href = elem.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if self._is_valid_article_url(full_url):
                            links.append(full_url)
                
                if links:  # 如果找到链接就返回
                    break
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {str(e)}")
                continue
        
        return list(set(links))  # 去重
    
    def _is_valid_article_url(self, url: str) -> bool:
        """判断是否是有效的文章URL"""
        # 排除一些明显不是文章的URL
        exclude_patterns = [
            r'\.jpg$', r'\.png$', r'\.gif$', r'\.pdf$',
            r'/tag/', r'/category/', r'/author/',
            r'#', r'javascript:', r'mailto:'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _crawl_single_page(self, url: str) -> Optional[Dict]:
        """爬取单个页面内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取正文内容
            content = self._extract_article_content(soup)
            
            if not title or not content or len(content) < 100:
                return None
            
            return {
                'title': title,
                'content': content,
                'source_url': url,
                'source_type': 'website',
                'meta': {
                    'crawled_time': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"爬取页面 {url} 失败: {str(e)}")
            return None
    
    def _extract_title(self, soup) -> str:
        """提取文章标题"""
        # 尝试多种标题提取方式
        title_selectors = [
            'h1',
            '.title',
            '.post-title',
            '.entry-title',
            '.article-title',
            'title'
        ]
        
        for selector in title_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text().strip()
                    if title and len(title) > 5:  # 过滤太短的标题
                        return title
            except Exception:
                continue
        
        return ""
    
    def _extract_article_content(self, soup) -> str:
        """提取文章正文内容"""
        # 移除不需要的元素
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', '.ad', '.advertisement']):
            element.decompose()
        
        # 尝试多种内容提取方式
        content_selectors = [
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.main-content',
            '.post-body',
            '.entry'
        ]
        
        for selector in content_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    content = self._extract_text(elem)
                    if content and len(content) > 100:  # 过滤太短的内容
                        return content
            except Exception:
                continue
        
        # 如果以上都失败，尝试提取body内容
        body = soup.find('body')
        if body:
            return self._extract_text(body)
        
        return ""
    
    def crawl_zhihu_author(self, author_url: str, max_articles: int = 5) -> List[Dict]:
        """爬取知乎答主的最新内容"""
        try:
            # 知乎需要特殊的User-Agent和header
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # 从用户主页获取文章和回答
            response = self.session.get(author_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"知乎请求失败，状态码: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取用户名
            author_name = self._extract_zhihu_author_name(soup)
            
            # 查找文章和回答链接
            content_links = self._find_zhihu_content_links(soup, author_url)
            
            articles = []
            for link in content_links[:max_articles]:
                article = self._crawl_zhihu_content(link, author_name)
                if article:
                    articles.append(article)
                time.sleep(2)  # 知乎限制较严格，间隔久一点
            
            return articles
            
        except Exception as e:
            logger.error(f"爬取知乎答主内容失败: {str(e)}")
            return []
    
    def _extract_zhihu_author_name(self, soup) -> str:
        """提取知乎用户名"""
        try:
            # 尝试多种方式提取用户名
            name_selectors = [
                '.ProfileHeader-name',
                '.AuthorInfo-name',
                'h1.UserHeader-name',
                '.Profile-name'
            ]
            
            for selector in name_selectors:
                elem = soup.select_one(selector)
                if elem:
                    return elem.get_text().strip()
            
            return "知乎用户"
        except Exception:
            return "知乎用户"
    
    def _find_zhihu_content_links(self, soup, base_url: str) -> List[str]:
        """查找知乎内容链接（文章和回答）"""
        links = []
        
        # 查找文章和回答链接
        link_selectors = [
            'a[href*="/answer/"]',
            'a[href*="/p/"]',
            'a[href*="zhuanlan.zhihu.com/p/"]'
        ]
        
        for selector in link_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    href = elem.get('href')
                    if href:
                        if not href.startswith('http'):
                            href = urljoin('https://www.zhihu.com', href)
                        links.append(href)
            except Exception as e:
                logger.debug(f"知乎链接选择器 {selector} 失败: {str(e)}")
                continue
        
        return list(set(links))[:10]  # 去重并限制数量
    
    def _crawl_zhihu_content(self, url: str, author_name: str) -> Optional[Dict]:
        """爬取知乎单个内容（文章或回答）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = self._extract_zhihu_title(soup, url)
            
            # 提取内容
            content = self._extract_zhihu_content_text(soup, url)
            
            if not title or not content or len(content) < 50:
                return None
            
            content_type = "文章" if "/p/" in url else "回答"
            
            return {
                'title': title,
                'content': content,
                'source_url': url,
                'source_type': 'zhihu',
                'meta': {
                    'author': author_name,
                    'content_type': content_type,
                    'crawled_time': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"爬取知乎内容 {url} 失败: {str(e)}")
            return None
    
    def _extract_zhihu_title(self, soup, url: str) -> str:
        """提取知乎标题"""
        try:
            if "/p/" in url:  # 文章
                title_elem = soup.select_one('.Post-Title') or soup.select_one('h1')
            else:  # 回答
                title_elem = soup.select_one('.QuestionHeader-title') or soup.select_one('h1')
            
            if title_elem:
                return title_elem.get_text().strip()
            
            return "知乎内容"
        except Exception:
            return "知乎内容"
    
    def _extract_zhihu_content_text(self, soup, url: str) -> str:
        """提取知乎内容文本"""
        try:
            if "/p/" in url:  # 文章
                content_elem = soup.select_one('.Post-RichText') or soup.select_one('.RichText')
            else:  # 回答
                content_elem = soup.select_one('.RichContent-inner') or soup.select_one('.RichText')
            
            if content_elem:
                return self._extract_text(content_elem)
            
            return ""
        except Exception:
            return ""
    
    def crawl(self, source_url: str, source_type: str = 'auto', max_count: int = 5) -> List[Dict]:
        """统一爬取接口"""
        try:
            if source_type == 'auto':
                source_type = self._detect_source_type(source_url)
            
            if source_type == 'wechat':
                article = self.crawl_wechat_article(source_url)
                return [article] if article else []
            elif source_type == 'zhihu':
                return self.crawl_zhihu_author(source_url, max_count)
            elif source_type == 'website':
                return self.crawl_website(source_url, max_count)
            else:
                logger.error(f"不支持的源类型: {source_type}")
                return []
                
        except Exception as e:
            logger.error(f"爬取失败: {str(e)}")
            return []
    
    def _detect_source_type(self, url: str) -> str:
        """自动检测源类型"""
        if 'mp.weixin.qq.com' in url:
            return 'wechat'
        elif 'zhihu.com' in url:
            return 'zhihu'
        else:
            return 'website'