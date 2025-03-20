"""
消息管理模块 - 负责处理Workable间的消息传递
"""

import logging
from typing import List, Optional, Dict

from workable.core.models import Message
from workable.core.exceptions import MessageError

class MessageManager:
    """
    消息管理器 - 管理与Workable相关的消息
    """
    
    def __init__(self):
        """初始化消息管理器"""
        self.inbox = []  # type: List[Message]
        self.archived = []  # type: List[Message]
        self.logger = logging.getLogger(__name__)
        
        # 兼容旧版API的属性
        self._processing = []  # 旧版API使用的处理中列表
    
    @property
    def processing(self):
        """兼容旧版API的处理中消息列表"""
        return [msg for msg in self.archived if msg.status == "processing"]
    
    @property
    def archive(self):
        """兼容旧版API的归档消息列表"""
        return [msg for msg in self.archived if msg.status == "archive"]
    
    def append(self, message: Message) -> None:
        """
        添加消息到收件箱
        
        Args:
            message: 要添加的消息
            
        Raises:
            MessageError: 如果消息对象无效
        """
        self.append_message(message)
    
    def append_message(self, message: Message) -> None:
        """
        添加消息到收件箱
        
        Args:
            message: 要添加的消息
            
        Raises:
            MessageError: 如果消息对象无效
        """
        if not isinstance(message, Message):
            raise MessageError(f"无效的消息对象: {message}")
        
        # 设置消息状态为inbox（如果未指定）
        if not message.status or message.status not in ["inbox", "processing", "archive", "archived"]:
            message.status = "inbox"
            
        # 添加消息到收件箱或已归档列表
        if message.status in ["archived", "archive", "processing"]:
            self.archived.append(message)
        else:
            self.inbox.append(message)
            
        self.logger.info(f"添加消息: {message.content[:20]}...")
    
    def process_next(self) -> Optional[Message]:
        """
        处理下一条消息
        
        Returns:
            处理的消息，如果没有消息则返回None
        """
        if not self.inbox:
            self.logger.warning("尝试处理空收件箱")
            return None
        
        message = self.inbox.pop(0)
        message.status = "processing"  # 兼容旧版状态
        self.archived.append(message)
        
        self.logger.info(f"处理消息: {message.content[:20]}...")
        return message
    
    def archive_message(self, message_id: str) -> bool:
        """
        将消息归档
        
        Args:
            message_id: 消息ID
            
        Returns:
            是否成功归档
        """
        # 从收件箱中查找消息
        for i, message in enumerate(self.inbox):
            if message.id == message_id:
                message.status = "archive"  # 兼容旧版状态
                self.archived.append(self.inbox.pop(i))
                self.logger.info(f"归档收件箱消息: {message.content[:20]}...")
                return True
        
        # 从处理中状态查找消息
        for message in self.archived:
            if message.id == message_id and message.status == "processing":
                message.status = "archive"
                self.logger.info(f"归档处理中消息: {message.content[:20]}...")
                return True
                
        self.logger.warning(f"尝试归档不存在的消息: {message_id}")
        return False
    
    def get_inbox(self) -> List[Message]:
        """
        获取收件箱中的所有消息
        
        Returns:
            收件箱消息列表
        """
        return self.inbox.copy()
    
    def get_archived(self) -> List[Message]:
        """
        获取已归档的所有消息
        
        Returns:
            已归档消息列表
        """
        return [msg for msg in self.archived if msg.status in ["archive", "archived"]]
    
    def get_all_messages(self) -> List[Message]:
        """
        获取所有消息(收件箱和已归档)
        
        Returns:
            所有消息列表
        """
        return self.inbox.copy() + self.archived.copy()
    
    def get_messages_by_status(self, status: str) -> List[Message]:
        """
        获取指定状态的消息
        
        Args:
            status: 消息状态，可选值为inbox、processing或archive
        
        Returns:
            指定状态的消息列表
        
        Raises:
            ValueError: 如果状态值无效
        """
        if status not in ["inbox", "processing", "archive"]:
            raise ValueError(f"无效的消息状态: {status}")
            
        if status == "inbox":
            return self.inbox.copy()
        elif status == "processing":
            return [msg for msg in self.archived if msg.status == "processing"]
        else:  # archive
            return [msg for msg in self.archived if msg.status in ["archive", "archived"]]
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """
        通过ID获取消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            消息对象，如果不存在则返回None
        """
        for message in self.inbox + self.archived:
            if message.id == message_id:
                return message
        return None
    
    def clear_inbox(self) -> None:
        """清空收件箱"""
        self.inbox.clear()
        self.logger.info("清空收件箱")
    
    def clear_processing(self) -> None:
        """清空处理中队列（兼容旧版API）"""
        self.archived = [msg for msg in self.archived if msg.status != "processing"]
        self.logger.info("清空处理中队列")
    
    def clear_archive(self) -> None:
        """清空归档队列（兼容旧版API）"""
        self.archived = [msg for msg in self.archived if msg.status not in ["archive", "archived"]]
        self.logger.info("清空归档队列")
    
    def clear_all(self) -> None:
        """清空所有消息(收件箱和已归档)"""
        self.inbox.clear()
        self.archived.clear()
        self.logger.info("清空所有消息")
    
    # 兼容旧版API
    clear_messages = clear_all 