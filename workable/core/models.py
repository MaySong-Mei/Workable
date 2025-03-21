"""
Workable基础数据模型 - 定义系统中使用的基础数据模型
增强Frame作为索引实体的功能
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import uuid

class WorkableFrame:
    """
    Workable框架，用于索引和引用Workable
    
    作为workable框架级别设计中的核心索引实体，管理引用和顺序
    """
    
    def __init__(self, name: str, logic_description: str, 
                 seq: int = 0,
                 frame_type: str = "reference", 
                 exref: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        初始化WorkableFrame
        
        Args:
            name: 名称
            logic_description: 逻辑描述
            seq: 序列号，用于顺序索引
            frame_type: 框架类型 (reference, child, local)
            exref: 外部引用UUID
            metadata: 元数据字典
        """
        self.name = name
        self.logic_description = logic_description
        self.seq = seq  # 序列号用于在Content中的有序存储
        self.frame_type = frame_type  # 框架类型
        self.exref = exref  # 外部引用UUID
        self.metadata = metadata or {}  # 元数据字典
        
    def is_external(self) -> bool:
        """
        检查是否为外部引用
        
        Returns:
            是否为外部引用
        """
        return self.exref is not None and self.frame_type != "local"
        
    def is_local(self) -> bool:
        """
        检查是否为本地引用
        
        Returns:
            是否为本地引用
        """
        return self.frame_type == "local"
        
    def get_reference_uuid(self) -> Optional[str]:
        """
        获取引用的UUID
        
        Returns:
            引用的UUID，如果没有则返回None
        """
        return self.exref
        
    def update_metadata(self, key: str, value: Any) -> None:
        """
        更新元数据
        
        Args:
            key: 键
            value: 值
        """
        self.metadata[key] = value
        
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        获取元数据
        
        Args:
            key: 键
            default: 默认值
            
        Returns:
            元数据值
        """
        return self.metadata.get(key, default)
    
    def __repr__(self) -> str:
        return f"<WorkableFrame type={self.frame_type} name={self.name} seq={self.seq}>"

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
    关系模型
    """
    
    def __init__(self, source_uuid: str, target_uuid: str, relation_type: str, description: str = ""):
        """
        初始化关系
        
        Args:
            source_uuid: 源UUID
            target_uuid: 目标UUID
            relation_type: 关系类型
            description: 关系描述
        """
        self.source_uuid = source_uuid
        self.target_uuid = target_uuid
        self.relation_type = relation_type
        self.description = description
    
    def __repr__(self) -> str:
        return f"<Relation {self.source_uuid}-{self.relation_type}->{self.target_uuid}>" 