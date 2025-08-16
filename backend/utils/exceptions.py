
class WeChatAutoPublisherException(Exception):
    """基础异常类"""
    pass

class ConfigurationError(WeChatAutoPublisherException):
    """配置错误"""
    pass

class APIError(WeChatAutoPublisherException):
    """API调用错误"""
    pass

class CrawlerError(WeChatAutoPublisherException):
    """爬虫错误"""
    pass

class PublishError(WeChatAutoPublisherException):
    """发布错误"""
    pass

class LLMError(WeChatAutoPublisherException):
    """LLM服务错误"""
    pass