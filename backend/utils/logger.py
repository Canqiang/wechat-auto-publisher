import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import traceback
import json


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器（JSON格式）"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        
        return json.dumps(log_entry, ensure_ascii=False)


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self._loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """设置根日志记录器"""
        # 创建日志目录
        log_dir = "data/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 清除默认处理器
        root_logger.handlers = []
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 控制台格式化器（带颜色）
        console_formatter = ColorFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器（应用日志）
        app_file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'app.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        app_file_handler.setLevel(logging.DEBUG)
        
        # 文件格式化器
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
            '[%(filename)s:%(lineno)d]'
        )
        app_file_handler.setFormatter(file_formatter)
        
        # 错误日志文件处理器
        error_file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'error.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        
        # 结构化日志处理器
        structured_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'structured.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        structured_handler.setLevel(logging.INFO)
        structured_handler.setFormatter(StructuredFormatter())
        
        # 添加处理器
        root_logger.addHandler(console_handler)
        root_logger.addHandler(app_file_handler)
        root_logger.addHandler(error_file_handler)
        root_logger.addHandler(structured_handler)
        
        # 设置第三方库日志级别
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def log_request(self, logger: logging.Logger, request, response=None, 
                   user_id: Optional[str] = None):
        """记录HTTP请求日志"""
        extra = {
            'request_id': getattr(request, 'request_id', None),
            'ip_address': request.remote_addr,
            'user_id': user_id
        }
        
        message = f"{request.method} {request.path}"
        if response:
            message += f" - {response.status_code}"
        
        logger.info(message, extra=extra)
    
    def log_task_start(self, logger: logging.Logger, task_name: str, 
                      task_id: Optional[str] = None, **kwargs):
        """记录任务开始日志"""
        extra = {'task_id': task_id} if task_id else {}
        message = f"Task started: {task_name}"
        if kwargs:
            message += f" - {kwargs}"
        logger.info(message, extra=extra)
    
    def log_task_end(self, logger: logging.Logger, task_name: str, 
                    duration: float, success: bool = True, 
                    task_id: Optional[str] = None, **kwargs):
        """记录任务结束日志"""
        extra = {'task_id': task_id} if task_id else {}
        status = "completed" if success else "failed"
        message = f"Task {status}: {task_name} - Duration: {duration:.2f}s"
        if kwargs:
            message += f" - {kwargs}"
        
        if success:
            logger.info(message, extra=extra)
        else:
            logger.error(message, extra=extra)
    
    def log_api_call(self, logger: logging.Logger, api_name: str, 
                    method: str, url: str, status_code: int, 
                    duration: float, **kwargs):
        """记录API调用日志"""
        message = f"API Call: {api_name} - {method} {url} - {status_code} - {duration:.2f}s"
        if kwargs:
            message += f" - {kwargs}"
        
        if status_code >= 400:
            logger.error(message)
        else:
            logger.info(message)


# 全局日志管理器实例
logger_manager = LoggerManager()

# 便捷函数
def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    if name is None:
        # 获取调用者的模块名
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return logger_manager.get_logger(name)


def log_exception(logger: logging.Logger, message: str = "An error occurred", 
                 exc_info=True, **kwargs):
    """记录异常日志"""
    extra = kwargs
    logger.error(message, exc_info=exc_info, extra=extra)


def log_performance(func):
    """性能监控装饰器"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Function {func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    
    return wrapper


def log_user_action(action: str, user_id: Optional[str] = None, 
                   details: Optional[dict] = None):
    """记录用户操作日志"""
    logger = get_logger('user_actions')
    
    extra = {}
    if user_id:
        extra['user_id'] = user_id
    
    message = f"User action: {action}"
    if details:
        message += f" - {details}"
    
    logger.info(message, extra=extra)


# 配置日志级别
def set_log_level(level: str):
    """设置日志级别"""
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    if level.upper() in level_map:
        logging.getLogger().setLevel(level_map[level.upper()])
    else:
        raise ValueError(f"Invalid log level: {level}")


# 示例使用
if __name__ == "__main__":
    # 获取日志记录器
    logger = get_logger(__name__)
    
    # 测试不同级别的日志
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    # 测试异常日志
    try:
        1 / 0
    except Exception:
        log_exception(logger, "除零错误测试")
    
    # 测试用户操作日志
    log_user_action("login", user_id="123", details={"ip": "192.168.1.1"})
    
    print("日志测试完成，请查看 data/logs/ 目录下的日志文件")
