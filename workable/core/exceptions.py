"""
异常类模块 - 定义Workable系统中使用的异常类
"""

class WorkableError(Exception):
    """Workable系统基础异常类"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class ContentError(WorkableError):
    """内容管理相关异常"""
    pass

class RelationError(WorkableError):
    """关系管理相关异常"""
    pass

class MessageError(WorkableError):
    """消息处理相关异常"""
    pass

class ConversionError(WorkableError):
    """转换操作相关异常"""
    pass

class VisualizationError(WorkableError):
    """可视化相关异常"""
    pass

class ManagerError(WorkableError):
    """Workable管理器相关异常"""
    pass 