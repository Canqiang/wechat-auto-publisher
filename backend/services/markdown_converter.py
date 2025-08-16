import markdown
from markdown.extensions import tables, fenced_code, nl2br
import re
from typing import Dict

class MarkdownToWeChatHTML:
    def __init__(self):
        self.md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'nl2br',
            'attr_list',
            'def_list',
            'footnotes',
            'md_in_html',
            'sane_lists'
        ])
        
        # 微信公众号样式模板
        self.styles = {
            'h1': 'font-size: 24px; font-weight: bold; margin: 30px 0 20px; text-align: center; color: #333;',
            'h2': 'font-size: 20px; font-weight: bold; margin: 25px 0 15px; color: #333; border-left: 4px solid #1890ff; padding-left: 10px;',
            'h3': 'font-size: 18px; font-weight: bold; margin: 20px 0 10px; color: #333;',
            'p': 'font-size: 16px; line-height: 1.8; margin: 15px 0; color: #444; text-align: justify;',
            'blockquote': 'border-left: 4px solid #ddd; padding: 10px 20px; margin: 20px 0; background: #f9f9f9; color: #666;',
            'code': 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; color: #c7254e;',
            'pre': 'background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 20px 0;',
            'ul': 'margin: 15px 0; padding-left: 30px;',
            'ol': 'margin: 15px 0; padding-left: 30px;',
            'li': 'font-size: 16px; line-height: 1.8; margin: 8px 0; color: #444;',
            'img': 'max-width: 100%; height: auto; display: block; margin: 20px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
            'table': 'width: 100%; border-collapse: collapse; margin: 20px 0;',
            'th': 'background: #f0f0f0; padding: 10px; border: 1px solid #ddd; font-weight: bold;',
            'td': 'padding: 10px; border: 1px solid #ddd;',
            'hr': 'margin: 30px 0; border: none; border-top: 1px solid #eee;',
            'strong': 'font-weight: bold; color: #333;',
            'em': 'font-style: italic; color: #666;',
            'a': 'color: #1890ff; text-decoration: none;'
        }
    
    def convert(self, markdown_text: str, custom_styles: Dict = None) -> str:
        """将Markdown转换为微信公众号HTML"""
        if custom_styles:
            self.styles.update(custom_styles)
        
        # 转换Markdown为HTML
        html = self.md.convert(markdown_text)
        
        # 应用微信公众号样式
        html = self._apply_styles(html)
        
        # 添加容器
        html = self._wrap_container(html)
        
        # 处理特殊元素
        html = self._process_special_elements(html)
        
        return html
    
    def _apply_styles(self, html: str) -> str:
        """应用样式到HTML元素"""
        for tag, style in self.styles.items():
            # 处理开标签
            pattern = f'<{tag}>'
            replacement = f'<{tag} style="{style}">'
            html = re.sub(pattern, replacement, html)
            
            # 处理带属性的标签
            pattern = f'<{tag} ([^>]+)>'
            replacement = f'<{tag} style="{style}" \\1>'
            html = re.sub(pattern, replacement, html)
        
        return html
    
    def _wrap_container(self, html: str) -> str:
        """添加容器包装"""
        container_style = """
        <section style="max-width: 677px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        """
        
        return f'{container_style}{html}</section>'
    
    def _process_special_elements(self, html: str) -> str:
        """处理特殊元素"""
        # 添加阅读原文按钮
        read_more = """
        <section style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center;">
            <p style="font-size: 14px; color: #999;">- END -</p>
        </section>
        """
        
        # 处理代码高亮
        html = self._highlight_code(html)
        
        # 添加图片说明
        html = self._add_image_captions(html)
        
        return html + read_more
    
    def _highlight_code(self, html: str) -> str:
        """代码高亮处理"""
        # 这里可以集成pygments或其他代码高亮库
        return html
    
    def _add_image_captions(self, html: str) -> str:
        """为图片添加说明文字"""
        # 查找所有图片并添加figure包装
        pattern = r'<img ([^>]+) alt="([^"]*)"([^>]*)>'
        def replace_img(match):
            attrs = match.group(1)
            alt = match.group(2)
            other = match.group(3)
            if alt:
                return f'''
                <figure style="margin: 20px 0; text-align: center;">
                    <img {attrs} alt="{alt}"{other}>
                    <figcaption style="margin-top: 10px; font-size: 14px; color: #999;">{alt}</figcaption>
                </figure>
                '''
            return match.group(0)
        
        return re.sub(pattern, replace_img, html)
    
    def add_signature(self, html: str, author: str = "", official_account: str = "") -> str:
        """添加文章签名"""
        signature = f"""
        <section style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <p style="font-size: 14px; color: #666; margin: 5px 0;">
                作者：{author or '佚名'}
            </p>
            <p style="font-size: 14px; color: #666; margin: 5px 0;">
                公众号：{official_account or '精彩内容'}
            </p>
            <p style="font-size: 12px; color: #999; margin-top: 10px;">
                欢迎关注，获取更多精彩内容
            </p>
        </section>
        """
        
        return html + signature