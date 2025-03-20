"""
基础数据模型 - 定义Workable系统中使用的数据结构
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import uuid

@dataclass
class WorkableFrame:
    """
    Workable的轻量引用，记录快照和引用信息
    用于解耦工作单元的实际实现
    """
    name: str
    logic_description: str
    snapshot: str = ""
    exref: Optional[str] = None  # 外部β-workable引用UUID
    lnref: Optional[str] = None  # 本地γ-workable引用UUID
    
    def is_external(self) -> bool:
        """判断当前Frame是否引用外部Workable"""
        return self.exref is not None

@dataclass
class Message:
    """
    消息对象，用于在Workable之间传递任务或信息
    """
    content: str
    sender: str
    receiver: str
    status: str = "inbox"  # inbox, processing, archive
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """验证消息状态是否有效"""
        valid_statuses = ["inbox", "processing", "archive"]
        if self.status not in valid_statuses:
            self.status = "inbox"

@dataclass
class Relation:
    """
    关系对象，描述当前Workable对外部Workable的影响和依赖关系
    """
    target_uuid: str
    meta: Dict = None
    
    def __post_init__(self):
        """初始化元数据字典"""
        if self.meta is None:
            self.meta = {} 