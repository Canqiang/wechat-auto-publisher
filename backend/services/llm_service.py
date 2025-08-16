from openai import OpenAI
from anthropic import Anthropic
import json
import logging
import time
from typing import Dict, Optional, List
from config import Config

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.claude_client = None
        self.timeout = 30  # 设置超时时间
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化LLM客户端"""
        if Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_BASE_URL,
                timeout=self.timeout
            )
        
        if Config.CLAUDE_API_KEY:
            self.claude_client = Anthropic(
                api_key=Config.CLAUDE_API_KEY,
                base_url=Config.CLAUDE_BASE_URL,
                timeout=self.timeout
            )
    
    def rewrite_article(self, content: str, style: str = "professional") -> str:
        """使用LLM改写文章"""
        prompt = f"""
        请将以下文章改写成{style}风格，要求：
        1. 保持原文的核心信息和观点
        2. 调整语言风格和表达方式
        3. 确保内容原创性，避免抄袭
        4. 保持文章结构清晰，段落分明
        5. 字数控制在原文的80%-120%之间
        
        原文：
        {content}
        
        改写后的文章：
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "你是一个专业的内容创作者"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                return response.content[0].text
            
        except Exception as e:
            logger.error(f"LLM改写失败: {str(e)}")
            return content
    
    def generate_article(self, params: Dict) -> Dict:
        """生成新文章"""
        topic = params.get('topic', '')
        keywords = params.get('keywords', [])
        style = params.get('style', 'professional')
        length = params.get('length', 1000)
        
        prompt = f"""
        请创作一篇关于"{topic}"的文章，要求：
        1. 文章风格：{style}
        2. 包含关键词：{', '.join(keywords)}
        3. 字数要求：约{length}字
        4. 结构清晰，包含引言、主体和结论
        5. 内容要有深度，提供有价值的信息
        6. 适合微信公众号发布
        
        请生成文章：
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "你是一个优秀的自媒体内容创作者"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=2000
                )
                content = response.choices[0].message.content
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                content = response.content[0].text
            else:
                content = "生成失败：未配置LLM服务"
            
            # 生成标题
            title = self._generate_title(content)
            
            return {
                'title': title,
                'content': content,
                'keywords': keywords,
                'topic': topic
            }
            
        except Exception as e:
            logger.error(f"文章生成失败: {str(e)}")
            return None
    
    def _generate_title(self, content: str) -> str:
        """为文章生成标题"""
        prompt = f"请为以下文章生成一个吸引人的标题（15字以内）：\n{content[:500]}"
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                    max_tokens=50
                )
                return response.choices[0].message.content.strip()
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-haiku-20240307",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50
                )
                return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"生成标题失败: {str(e)}")
            return "精彩文章标题"
    
    def generate_content(self, prompt: str) -> str:
        """生成内容 - 为API兼容性添加的方法"""
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "你是一个专业的内容创作者，擅长创作高质量的文章。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content.strip()
            elif self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                return response.content[0].text.strip()
            else:
                return "错误：未配置LLM服务"
        except Exception as e:
            logger.error(f"生成内容失败: {str(e)}")
            return f"生成失败：{str(e)}"
    
    def generate_title(self, content: str) -> str:
        """生成标题 - 为API兼容性添加的方法"""
        return self._generate_title(content)
    
    def rewrite_for_wechat(self, original_content: str, source_info: dict = None) -> dict:
        """将内容改写为适合微信公众号的文章"""
        
        # 如果原内容太长，进行截取以避免超时
        max_content_length = 3000
        if len(original_content) > max_content_length:
            original_content = original_content[:max_content_length] + "..."
            logger.info(f"内容过长，已截取至{max_content_length}字符")
        
        try:
            source_type = source_info.get('source_type', '网络') if source_info else '网络'
            original_title = source_info.get('title', '') if source_info else ''
            
            # 简化的改写提示词以减少API调用时间
            system_prompt = """你是微信公众号编辑。请将内容改写为公众号文章风格，要求：
1. 保持核心信息
2. 语言生动有趣
3. 适当使用emoji
4. 段落清晰
5. 控制在1000字内

格式：标题 + 正文"""

            user_prompt = f"""改写以下{source_type}内容：

标题：{original_title}
内容：{original_content[:2000]}

输出格式：
标题：[新标题]
正文：[改写内容]"""

            # 尝试使用更快的模型和更短的内容
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",  # 使用更快的模型
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=1500,  # 减少token数量
                        temperature=0.7,
                        timeout=15  # 设置较短的超时时间
                    )
                    result = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"GPT-4o-mini失败，尝试备用方案: {str(e)}")
                    # 备用方案：返回原内容但做简单优化
                    result = self._simple_rewrite_fallback(original_content, original_title)
            elif self.claude_client:
                try:
                    response = self.claude_client.messages.create(
                        model="claude-3-haiku-20240307",  # 使用更快的模型
                        max_tokens=1500,
                        temperature=0.7,
                        timeout=15,
                        messages=[
                            {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                        ]
                    )
                    result = response.content[0].text.strip()
                except Exception as e:
                    logger.warning(f"Claude失败，使用备用方案: {str(e)}")
                    result = self._simple_rewrite_fallback(original_content, original_title)
            else:
                logger.warning("未配置LLM服务，使用简单格式化")
                result = self._simple_rewrite_fallback(original_content, original_title)
            
            # 解析结果，提取标题和内容
            title, content = self._parse_rewrite_result(result)
            
            return {
                'title': title,
                'content': content,
                'original_title': original_title,
                'source_info': source_info,
                'rewrite_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"改写内容失败: {str(e)}")
            return {
                'title': original_title or "改写文章",
                'content': original_content,
                'error': str(e)
            }
    
    def _parse_rewrite_result(self, result: str) -> tuple:
        """解析改写结果，提取标题和内容"""
        try:
            lines = result.strip().split('\n')
            title = ""
            content_lines = []
            
            # 查找标题
            for i, line in enumerate(lines):
                line = line.strip()
                if any(keyword in line for keyword in ['标题', '新标题', '题目']):
                    # 提取标题内容
                    if '：' in line:
                        title = line.split('：', 1)[1].strip()
                    elif ':' in line:
                        title = line.split(':', 1)[1].strip()
                    continue
                
                # 跳过格式化文本
                if line and not any(keyword in line for keyword in ['正文', '内容', '文章']):
                    if not title and len(line) < 100 and i < 5:  # 可能是标题
                        title = line
                    else:
                        content_lines.append(line)
            
            content = '\n'.join(content_lines).strip()
            
            # 如果没有找到标题，使用第一行
            if not title and content_lines:
                first_line = content_lines[0]
                if len(first_line) < 100:
                    title = first_line
                    content = '\n'.join(content_lines[1:]).strip()
            
            return title or "改写文章", content or result
            
        except Exception as e:
            logger.error(f"解析改写结果失败: {str(e)}")
            return "改写文章", result
    
    def rewrite_batch(self, articles: List[dict]) -> List[dict]:
        """批量改写文章"""
        rewritten_articles = []
        
        for article in articles:
            try:
                rewritten = self.rewrite_for_wechat(
                    article.get('content', ''),
                    {
                        'title': article.get('title', ''),
                        'source_type': article.get('source_type', 'unknown'),
                        'source_url': article.get('source_url', ''),
                        'meta': article.get('meta', {})
                    }
                )
                
                # 合并原始信息和改写结果
                final_article = {
                    **article,
                    'title': rewritten['title'],
                    'content': rewritten['content'],
                    'original_title': article.get('title', ''),
                    'original_content': article.get('content', ''),
                    'rewritten': True,
                    'rewrite_time': rewritten.get('rewrite_time')
                }
                
                rewritten_articles.append(final_article)
                
                # 避免API限制
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"批量改写失败: {str(e)}")
                # 如果改写失败，保留原文
                rewritten_articles.append({
                    **article,
                    'rewritten': False,
                    'error': str(e)
                })
        
        return rewritten_articles
    
    def _simple_rewrite_fallback(self, content: str, title: str) -> str:
        """简单的备用改写方案，当LLM失败时使用"""
        try:
            # 简单的文本优化：添加emoji、调整段落
            emojis = ['📝', '✨', '🔥', '💡', '🎯', '🚀', '📊', '💰', '🌟']
            import random
            
            # 优化标题
            if title:
                new_title = f"{random.choice(emojis[:3])} {title}"
                if len(title) > 20:
                    new_title = title[:20] + "..."
            else:
                new_title = f"{random.choice(emojis)} 精彩内容分享"
            
            # 简单的内容格式化
            paragraphs = content.split('\n')
            formatted_paragraphs = []
            
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if para:
                    # 每隔几段添加emoji
                    if i % 3 == 0 and i > 0:
                        para = f"{random.choice(emojis[3:])} {para}"
                    formatted_paragraphs.append(para)
            
            new_content = '\n\n'.join(formatted_paragraphs)
            
            # 添加结尾
            new_content += f"\n\n{random.choice(['✨', '🌟', '💫'])} 以上就是今天的分享内容，希望对大家有帮助！"
            
            return f"标题：{new_title}\n正文：{new_content}"
            
        except Exception as e:
            logger.error(f"备用改写方案失败: {str(e)}")
            return f"标题：{title or '内容分享'}\n正文：{content}"