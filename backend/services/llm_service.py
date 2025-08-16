from openai import OpenAI
from anthropic import Anthropic
import json
import logging
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.claude_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化LLM客户端"""
        if Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_BASE_URL
            )
        
        if Config.CLAUDE_API_KEY:
            self.claude_client = Anthropic(
                api_key=Config.CLAUDE_API_KEY,
                base_url=Config.CLAUDE_BASE_URL
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