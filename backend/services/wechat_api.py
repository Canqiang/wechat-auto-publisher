import requests
import json
import hashlib
import time
from typing import Dict, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class WeChatAPI:
    def __init__(self):
        self.app_id = Config.WECHAT_APP_ID
        self.app_secret = Config.WECHAT_APP_SECRET
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
    
    def get_access_token(self) -> str:
        """获取access_token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "access_token" in data:
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
        except Exception as e:
            logger.error(f"请求access_token异常: {str(e)}")
            return None
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片获取media_id"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/media/upload"
        params = {
            "access_token": access_token,
            "type": "image"
        }
        
        try:
            with open(image_path, 'rb') as f:
                files = {"media": f}
                response = requests.post(url, params=params, files=files)
                data = response.json()
                
                if "media_id" in data:
                    return data["media_id"]
                else:
                    logger.error(f"上传图片失败: {data}")
                    return None
        except Exception as e:
            logger.error(f"上传图片异常: {str(e)}")
            return None
    
    def upload_news(self, articles: list) -> Optional[str]:
        """上传图文消息"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/material/add_news"
        params = {"access_token": access_token}
        
        data = {"articles": articles}
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            result = response.json()
            
            if "media_id" in result:
                return result["media_id"]
            else:
                logger.error(f"上传图文消息失败: {result}")
                return None
        except Exception as e:
            logger.error(f"上传图文消息异常: {str(e)}")
            return None
    
    def publish(self, article: Dict) -> Dict:
        """发布文章到公众号"""
        # 上传封面图
        cover_media_id = None
        if article.get('cover_image'):
            cover_media_id = self.upload_image(article['cover_image'])
        
        # 构建图文消息
        news_article = {
            "title": article['title'],
            "author": article.get('author', ''),
            "digest": article.get('digest', ''),
            "content": article['html_content'],
            "content_source_url": article.get('source_url', ''),
            "thumb_media_id": cover_media_id or '',
            "show_cover_pic": 1,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
        
        # 上传图文消息
        media_id = self.upload_news([news_article])
        if not media_id:
            return {"success": False, "message": "上传图文消息失败"}
        
        # 群发消息
        result = self.send_all(media_id)
        
        return result
    
    def send_all(self, media_id: str) -> Dict:
        """群发消息"""
        access_token = self.get_access_token()
        if not access_token:
            return {"success": False, "message": "获取access_token失败"}
        
        url = f"{self.base_url}/message/mass/sendall"
        params = {"access_token": access_token}
        
        data = {
            "filter": {
                "is_to_all": True
            },
            "mpnews": {
                "media_id": media_id
            },
            "msgtype": "mpnews",
            "send_ignore_reprint": 0
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            if result.get("errcode") == 0:
                return {
                    "success": True,
                    "message": "发布成功",
                    "msg_id": result.get("msg_id"),
                    "msg_data_id": result.get("msg_data_id")
                }
            else:
                return {
                    "success": False,
                    "message": f"发布失败: {result.get('errmsg', '未知错误')}"
                }
        except Exception as e:
            logger.error(f"群发消息异常: {str(e)}")
            return {"success": False, "message": f"发布异常: {str(e)}"}