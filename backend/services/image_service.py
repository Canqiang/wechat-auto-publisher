# backend/services/image_service.py

import requests
from openai import OpenAI
from PIL import Image
import io
import base64
import time
import os
from typing import Optional, List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

class ImageService:
    """图片生成和处理服务"""
    
    def __init__(self):
        self.dalle_api_key = Config.DALLE_API_KEY
        self.stable_diffusion_api = Config.STABLE_DIFFUSION_API
        if self.dalle_api_key:
            self.openai_client = OpenAI(api_key=self.dalle_api_key)
    
    def generate_cover_image(self, article_title: str, style: str = "modern") -> Optional[str]:
        """为文章生成封面图"""
        try:
            # 生成提示词
            prompt = self._create_image_prompt(article_title, style)
            
            # 使用DALL-E生成图片
            if self.dalle_api_key:
                return self._generate_with_dalle(prompt)
            
            # 使用Stable Diffusion
            elif self.stable_diffusion_api:
                return self._generate_with_stable_diffusion(prompt)
            
            # 使用默认图片库
            else:
                return self._get_stock_image(article_title)
                
        except Exception as e:
            logger.error(f"生成封面图失败: {str(e)}")
            return None
    
    def _create_image_prompt(self, title: str, style: str) -> str:
        """创建图片生成提示词"""
        style_prompts = {
            "modern": "modern, minimalist, clean design, professional",
            "tech": "futuristic, technology, digital art, cyber",
            "nature": "natural, organic, environmental, peaceful",
            "business": "corporate, professional, elegant, sophisticated"
        }
        
        base_prompt = f"Create a cover image for article titled '{title}'"
        style_addon = style_prompts.get(style, "professional, high quality")
        
        return f"{base_prompt}, {style_addon}, high resolution, 16:9 aspect ratio"
    
    def _generate_with_dalle(self, prompt: str) -> str:
        """使用DALL-E 3生成图片"""
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # 下载并保存图片
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                # 确保目录存在
                os.makedirs("data/images", exist_ok=True)
                filename = f"data/images/cover_{int(time.time())}.png"
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                return filename
                
        except Exception as e:
            logger.error(f"DALL-E生成失败: {str(e)}")
            return None
    
    def _generate_with_stable_diffusion(self, prompt: str) -> str:
        """使用Stable Diffusion生成图片"""
        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": "low quality, blurry, distorted",
                "width": 1024,
                "height": 576,
                "num_inference_steps": 50,
                "guidance_scale": 7.5
            }
            
            response = requests.post(
                self.stable_diffusion_api,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # 假设API返回base64编码的图片
                img_data = base64.b64decode(data['image'])
                
                # 确保目录存在
                os.makedirs("data/images", exist_ok=True)
                filename = f"data/images/cover_{int(time.time())}.png"
                with open(filename, 'wb') as f:
                    f.write(img_data)
                return filename
                
        except Exception as e:
            logger.error(f"Stable Diffusion生成失败: {str(e)}")
            return None
    
    def _get_stock_image(self, title: str) -> Optional[str]:
        """获取默认图片"""
        try:
            # 使用免费图片API如Unsplash
            query = title[:50]  # 限制查询长度
            api_url = f"https://api.unsplash.com/photos/random"
            params = {
                'query': query,
                'orientation': 'landscape',
                'client_id': 'your_unsplash_client_id'  # 需要配置
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                image_url = data['urls']['regular']
                
                # 下载图片
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    os.makedirs("data/images", exist_ok=True)
                    filename = f"data/images/stock_{int(time.time())}.jpg"
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    return filename
            
            # 如果API失败，创建一个简单的默认图片
            return self._create_default_image(title)
            
        except Exception as e:
            logger.error(f"获取图片失败: {str(e)}")
            return self._create_default_image(title)
    
    def _create_default_image(self, title: str) -> str:
        """创建默认图片"""
        try:
            # 创建一个简单的文字图片
            img = Image.new('RGB', (1200, 675), color='#f0f0f0')
            
            # 这里可以添加文字，但需要PIL的字体支持
            # 简化版本直接返回纯色图片
            
            os.makedirs("data/images", exist_ok=True)
            filename = f"data/images/default_{int(time.time())}.png"
            img.save(filename)
            return filename
            
        except Exception as e:
            logger.error(f"创建默认图片失败: {str(e)}")
            return None
    
    def extract_images_from_article(self, html_content: str) -> List[str]:
        """从文章HTML中提取图片"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                images.append(src)
        
        return images
    
    def optimize_image(self, image_path: str, max_width: int = 1080) -> str:
        """优化图片大小和质量"""
        try:
            img = Image.open(image_path)
            
            # 调整大小
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为RGB（如果需要）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # 保存优化后的图片
            output_path = image_path.replace('.', '_optimized.')
            img.save(output_path, 'JPEG', quality=85, optimize=True)
            
            return output_path
            
        except Exception as e:
            logger.error(f"图片优化失败: {str(e)}")
            return image_path
    
    def create_image_collage(self, images: List[str], layout: str = "grid") -> str:
        """创建图片拼贴"""
        try:
            if layout == "grid":
                return self._create_grid_collage(images)
            elif layout == "horizontal":
                return self._create_horizontal_collage(images)
            else:
                return self._create_vertical_collage(images)
                
        except Exception as e:
            logger.error(f"创建拼贴失败: {str(e)}")
            return None
    
    def _create_grid_collage(self, images: List[str]) -> str:
        """创建网格拼贴"""
        try:
            if not images:
                return None
            
            # 打开所有图片
            pil_images = []
            for img_path in images[:4]:  # 最多4张图片
                try:
                    if img_path.startswith('http'):
                        response = requests.get(img_path)
                        img = Image.open(io.BytesIO(response.content))
                    else:
                        img = Image.open(img_path)
                    pil_images.append(img)
                except Exception as e:
                    logger.warning(f"无法打开图片 {img_path}: {str(e)}")
            
            if not pil_images:
                return None
            
            # 计算网格大小
            img_count = len(pil_images)
            if img_count == 1:
                cols, rows = 1, 1
            elif img_count <= 2:
                cols, rows = 2, 1
            elif img_count <= 4:
                cols, rows = 2, 2
            else:
                cols, rows = 3, 2
            
            # 调整所有图片到相同大小
            cell_width, cell_height = 400, 300
            for i, img in enumerate(pil_images):
                resized = img.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
                pil_images[i] = resized
            
            # 创建拼贴画布
            canvas_width = cols * cell_width
            canvas_height = rows * cell_height
            collage = Image.new('RGB', (canvas_width, canvas_height), 'white')
            
            # 放置图片
            for i, img in enumerate(pil_images):
                row = i // cols
                col = i % cols
                x = col * cell_width
                y = row * cell_height
                collage.paste(img, (x, y))
            
            # 保存拼贴
            os.makedirs("data/images", exist_ok=True)
            filename = f"data/images/collage_{int(time.time())}.jpg"
            collage.save(filename, 'JPEG', quality=90)
            
            return filename
            
        except Exception as e:
            logger.error(f"创建网格拼贴失败: {str(e)}")
            return None
    
    def _create_horizontal_collage(self, images: List[str]) -> str:
        """创建水平拼贴"""
        try:
            if not images:
                return None
            
            # 打开图片
            pil_images = []
            for img_path in images[:5]:  # 最多5张图片
                try:
                    if img_path.startswith('http'):
                        response = requests.get(img_path)
                        img = Image.open(io.BytesIO(response.content))
                    else:
                        img = Image.open(img_path)
                    pil_images.append(img)
                except Exception as e:
                    logger.warning(f"无法打开图片 {img_path}: {str(e)}")
            
            if not pil_images:
                return None
            
            # 统一高度
            target_height = 300
            total_width = 0
            
            for i, img in enumerate(pil_images):
                ratio = target_height / img.height
                new_width = int(img.width * ratio)
                resized = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                pil_images[i] = resized
                total_width += new_width
            
            # 创建水平拼贴
            collage = Image.new('RGB', (total_width, target_height), 'white')
            
            x_offset = 0
            for img in pil_images:
                collage.paste(img, (x_offset, 0))
                x_offset += img.width
            
            # 保存
            os.makedirs("data/images", exist_ok=True)
            filename = f"data/images/horizontal_collage_{int(time.time())}.jpg"
            collage.save(filename, 'JPEG', quality=90)
            
            return filename
            
        except Exception as e:
            logger.error(f"创建水平拼贴失败: {str(e)}")
            return None
    
    def _create_vertical_collage(self, images: List[str]) -> str:
        """创建垂直拼贴"""
        try:
            if not images:
                return None
            
            # 打开图片
            pil_images = []
            for img_path in images[:5]:  # 最多5张图片
                try:
                    if img_path.startswith('http'):
                        response = requests.get(img_path)
                        img = Image.open(io.BytesIO(response.content))
                    else:
                        img = Image.open(img_path)
                    pil_images.append(img)
                except Exception as e:
                    logger.warning(f"无法打开图片 {img_path}: {str(e)}")
            
            if not pil_images:
                return None
            
            # 统一宽度
            target_width = 600
            total_height = 0
            
            for i, img in enumerate(pil_images):
                ratio = target_width / img.width
                new_height = int(img.height * ratio)
                resized = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                pil_images[i] = resized
                total_height += new_height
            
            # 创建垂直拼贴
            collage = Image.new('RGB', (target_width, total_height), 'white')
            
            y_offset = 0
            for img in pil_images:
                collage.paste(img, (0, y_offset))
                y_offset += img.height
            
            # 保存
            os.makedirs("data/images", exist_ok=True)
            filename = f"data/images/vertical_collage_{int(time.time())}.jpg"
            collage.save(filename, 'JPEG', quality=90)
            
            return filename
            
        except Exception as e:
            logger.error(f"创建垂直拼贴失败: {str(e)}")
            return None
