import traceback
import logging
from typing import Any, Callable, Optional

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DebateError(Exception):
    """辩论系统专用异常"""
    def __init__(self, agent_name: str, error_type: str, message: str, original_error: Exception = None):
        self.agent_name = agent_name
        self.error_type = error_type
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{agent_name}] {error_type}: {message}")

def handle_agent_error(agent_name: str, error: Exception, ui_callback: Optional[Callable] = None) -> str:
    """处理agent层面的错误
    
    Args:
        agent_name: agent名称
        error: 捕获的异常
        ui_callback: UI回调函数
    
    Returns:
        str: 错误处理后的回复内容
    """
    error_type = type(error).__name__
    error_message = str(error)
    traceback_info = traceback.format_exc()
    
    # 记录详细错误信息
    logger.error(f"Agent {agent_name} 发生错误: {error_type}: {error_message}")
    logger.error(f"错误堆栈: {traceback_info}")
    
    # 根据错误类型进行分类处理
    if ui_callback:
        if "rate limit" in error_message.lower() or "quota" in error_message.lower():
            ui_callback("系统", f"[{agent_name}] 遇到API调用频率限制，请稍后再试")
        elif "connection" in error_message.lower() or "timeout" in error_message.lower():
            ui_callback("系统", f"[{agent_name}] 网络连接问题，请检查网络连接")
        elif "authentication" in error_message.lower() or "api key" in error_message.lower():
            ui_callback("系统", f"[{agent_name}] API认证失败，请检查API密钥")
        elif "model" in error_message.lower():
            ui_callback("系统", f"[{agent_name}] 模型调用错误: {error_message}")
        else:
            ui_callback("系统", f"[{agent_name}] 发生未知错误: {error_message}")
    
    # 返回错误后的默认回复
    return f"[{agent_name}] 当前无法正常回复，请稍后再试"

def safe_generate_reply(agent_name: str, safe_function: Callable, ui_callback: Optional[Callable] = None) -> str:
    """安全调用函数的包装器
    
    Args:
        agent_name: agent名称
        safe_function: 安全的函数调用（已经处理了所有参数）
        ui_callback: UI回调函数
    
    Returns:
        str: 回复内容
    """
    try:
        return safe_function()
    except Exception as e:
        return handle_agent_error(agent_name, e, ui_callback)

def log_debate_error(agent_name: str, error: Exception, context: str = ""):
    """记录辩论错误到日志文件
    
    Args:
        agent_name: agent名称
        error: 异常对象
        context: 错误上下文信息
    """
    error_info = {
        'agent': agent_name,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'traceback': traceback.format_exc()
    }
    
    logger.error(f"辩论错误详情: {error_info}")
    
    # 可以扩展为保存到文件或发送到监控系统
    # 例如: save_error_to_file(error_info)
    
def handle_debate_error(error: Exception, ui_callback: Optional[Callable] = None) -> bool:
    """处理辩论过程中的全局错误
    
    Args:
        error: 全局异常
        ui_callback: UI回调函数
    
    Returns:
        bool: 是否成功处理了错误
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    logger.error(f"辩论系统全局错误: {error_type}: {error_message}")
    logger.error(f"全局错误堆栈: {traceback.format_exc()}")
    
    if ui_callback:
        ui_callback("主持人", f"辩论过程中出现错误：{error_message}")
    
    return True