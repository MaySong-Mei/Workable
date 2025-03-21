"""
Workable核心模块 - 定义统一的Workable类，通过内部状态区分简单和复杂工作单元
实现基于索引的工作单元管理，分离对象引用和内容存储
"""

import uuid
import logging
from typing import Dict, List, Optional, Union, Any, Set

from workable.core.models import WorkableFrame, Relation
from workable.core.content import Content
from workable.core.message import MessageManager
from workable.core.relation import RelationManager
from workable.core.exceptions import WorkableError, ConversionError

class Workable:
    """
    统一的Workable类，通过内部状态区分简单(原子/γ-workable)和复杂(复合/α-workable)模式
    通过索引机制管理子Workable和本地Workable，实现解耦存储
    """
    
    def __init__(self, name: str, logic_description: str, is_atom: bool = True,
                 content_str: str = None, content_type: str = "code",
                 manager = None):
        """
        初始化Workable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            is_atom: 是否为原子Workable (简单模式)
            content_str: 内容字符串 (仅在简单模式下使用)
            content_type: 内容类型 (仅在简单模式下使用)
            manager: 可选的WorkableManager实例，用于索引查找
        """
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.logic_description = logic_description
        self.is_atom_flag = is_atom  # 内部状态标识
        self.message_manager = MessageManager()
        self.relation_manager = RelationManager()
        self.logger = logging.getLogger('workable')
        self.manager = manager  # 用于索引查找
        
        # 内容管理（所有Workable都有Content）
        if is_atom and content_str:
            # 简单模式: 直接内容
            self.content = Content(content_type=content_type, content=content_str)
        else:
            # 复杂模式或无内容: 空内容容器
            self.content = Content()
        
        # 缓存引用 (为保持向后兼容)
        self._child_references: Dict[str, 'Workable'] = {} if not is_atom else None
        self._local_references: Dict[str, 'Workable'] = {}
        
    def to_frame(self, frame_type: str = "reference") -> WorkableFrame:
        """
        将当前Workable转换为Frame
        
        Args:
            frame_type: 帧类型
        
        Returns:
            包含当前Workable信息的Frame
        """
        return WorkableFrame(
            name=self.name,
            logic_description=self.logic_description,
            seq=0,  # 临时序列号，实际添加时会被修改
            frame_type=frame_type,
            exref=self.uuid,
        )
    
    def update(self, name: str = None, logic_description: str = None) -> None:
        """
        更新Workable基本信息
        
        Args:
            name: 新的名称，如果为None则不更新
            logic_description: 新的逻辑描述，如果为None则不更新
        """
        if name:
            self.name = name
        if logic_description:
            self.logic_description = logic_description
        
        # 同步更新所有Frame
        if hasattr(self, "content") and self.content:
            if self.uuid in self.content._frames_by_uuid:
                for seq in self.content._frames_by_uuid[self.uuid]:
                    frame = self.content._frames_by_seq[seq]
                    if name:
                        frame.name = name
                    if logic_description:
                        frame.logic_description = logic_description
        
        self.logger.debug(f"更新Workable基本信息: {self.uuid}")
    
    # 状态相关方法
    
    def is_atom(self) -> bool:
        """
        检查是否为原子Workable
        
        Returns:
            是否为原子Workable
        """
        return self.is_atom_flag
    
    def is_simple(self) -> bool:
        """
        检查是否为简单Workable (别名方法)
        
        Returns:
            是否为简单Workable
        """
        return self.is_atom()
    
    def is_complex(self) -> bool:
        """
        检查是否为复杂Workable
        
        Returns:
            是否为复杂Workable
        """
        return not self.is_atom()
    
    # 状态转换方法
    
    def make_complex(self) -> 'Workable':
        """
        将简单Workable转换为复杂Workable
        
        Returns:
            转换后的Workable (self)
            
        Raises:
            ConversionError: 如果转换失败
        """
        if not self.is_atom():
            self.logger.warning(f"Workable {self.uuid} 已经是复杂类型")
            return self
        
        self.logger.info(f"开始将Workable {self.uuid} 从简单类型转换为复杂类型")
        
        # 将原始内容保存为本地Workable
        original_content = self.content.content
        original_content_type = self.content.content_type
        
        if original_content:
            # 创建本地Workable保存原内容
            local_workable = Workable(
                name=f"{self.name}_content",
                logic_description=self.logic_description,
                is_atom=True,
                content_str=original_content,
                content_type=original_content_type,
                manager=self.manager
            )
            
            # 标记为转换后的本地内容
            local_workable.is_converted_content = True
            
            # 初始化新的内容容器
            self.content = Content()
            
            # 添加为本地引用 - 使用新的索引机制
            self.add_local(local_workable)
        
        # 状态转换
        self.is_atom_flag = False
        
        # 初始化子引用字典
        self._child_references = {}
        
        self.logger.info(f"Workable {self.uuid} 已成功转换为复杂类型")
        
        return self
    
    def make_simple(self) -> 'Workable':
        """
        将复杂Workable转换为简单Workable
        
        Returns:
            转换后的Workable (self)
            
        Raises:
            ConversionError: 如果转换失败
        """
        if self.is_atom():
            self.logger.warning(f"Workable {self.uuid} 已经是简单类型")
            return self
        
        # 检查是否可以转换: 必须没有子Workable
        child_frames = self.content.get_frames_by_type("child")
        if child_frames and len(child_frames) > 0:
            raise ConversionError(f"无法转换含有子Workable的复杂Workable: {self.uuid}")
        
        # 检查是否有原始内容的本地Workable
        content_workable = None
        for local_uuid, local in self._local_references.items():
            if hasattr(local, "is_converted_content") and local.is_converted_content:
                content_workable = local
                break
                
        if not content_workable:
            # 需要有且仅有一个本地Workable作为内容
            local_frames = self.content.get_frames_by_type("local")
            if len(local_frames) != 1:
                raise ConversionError(
                    f"复杂Workable {self.uuid} 包含 {len(local_frames)} 个本地Workable，"
                    f"无法转换为简单Workable（需要恰好1个）"
                )
            
            # 获取唯一的本地Workable
            local_uuid = local_frames[0].get_reference_uuid()
            content_workable = self._local_references.get(local_uuid)
            
            if not content_workable:
                raise ConversionError(f"找不到本地Workable: {local_uuid}")
        
        self.logger.info(f"开始将Workable {self.uuid} 从复杂类型转换为简单类型")
        
        # 从本地Workable提取内容
        self.content = Content(
            content_type=content_workable.content.content_type,
            content=content_workable.content.content
        )
        
        # 状态转换
        self.is_atom_flag = True
        self._local_references = {}  # 清空本地引用
        self._child_references = None  # 清空子引用
        
        self.logger.info(f"Workable {self.uuid} 已成功转换为简单类型")
        
        return self
    
    # 简单模式方法
    
    @property
    def content_str(self) -> str:
        """
        获取内容字符串 (仅简单模式)
        
        Returns:
            内容字符串
            
        Raises:
            AttributeError: 如果在复杂模式下调用
        """
        if not self.is_atom():
            raise AttributeError("复杂Workable没有直接内容，请使用frames或本地Workable")
        return self.content.content
    
    @content_str.setter
    def content_str(self, value: str) -> None:
        """
        设置内容字符串 (仅简单模式)
        
        Args:
            value: 新的内容字符串
            
        Raises:
            AttributeError: 如果在复杂模式下调用
        """
        if not self.is_atom():
            raise AttributeError("复杂Workable没有直接内容，请使用frames或本地Workable")
        self.content.content = value
    
    @property
    def content_type(self) -> str:
        """
        获取内容类型 (仅简单模式)
        
        Returns:
            内容类型
            
        Raises:
            AttributeError: 如果在复杂模式下调用
        """
        if not self.is_atom():
            raise AttributeError("复杂Workable没有直接内容类型，请使用frames或本地Workable")
        return self.content.content_type
    
    @content_type.setter
    def content_type(self, value: str) -> None:
        """
        设置内容类型 (仅简单模式)
        
        Args:
            value: 新的内容类型
            
        Raises:
            AttributeError: 如果在复杂模式下调用
        """
        if not self.is_atom():
            raise AttributeError("复杂Workable没有直接内容类型，请使用frames或本地Workable")
        self.content.content_type = value
    
    def update_content(self, content_str: str) -> None:
        """
        更新内容 (仅简单模式)
        
        Args:
            content_str: 新的内容字符串
            
        Raises:
            AttributeError: 如果在复杂模式下调用
        """
        if not self.is_atom():
            raise AttributeError("复杂Workable没有直接内容，请使用frames或本地Workable")
        self.content.content = content_str
        self.logger.debug(f"更新Workable内容: {self.uuid}")
    
    # 复杂模式方法 - 子Workable管理
    
    def add_child(self, child: 'Workable') -> None:
        """
        添加子Workable (仅复杂模式)
        
        Args:
            child: 要添加的子Workable
            
        Raises:
            AttributeError: 如果在简单模式下调用
        """
        if self.is_atom():
            raise AttributeError("简单Workable不能添加子Workable，请先调用make_complex()")
        
        if not isinstance(child, Workable):
            raise WorkableError(f"无效的Workable对象: {child}")
        
        # 缓存引用 (向后兼容)
        if child.uuid in self._child_references:
            self.logger.warning(f"覆盖已存在的子Workable引用: {child.uuid}")
        self._child_references[child.uuid] = child
        
        # 添加索引
        self.content.add_frame(
            name=child.name,
            logic_description=child.logic_description,
            frame_type="child",
            uuid=child.uuid,
            is_local=False
        )
        
        self.logger.debug(f"添加子Workable: {child.uuid}")
    
    def remove_child(self, uuid: str) -> bool:
        """
        删除子Workable (仅复杂模式)
        
        Args:
            uuid: 要删除的子Workable的UUID
            
        Returns:
            是否成功删除
            
        Raises:
            AttributeError: 如果在简单模式下调用
        """
        if self.is_atom():
            raise AttributeError("简单Workable不能删除子Workable")
        
        # 从缓存中删除
        if uuid in self._child_references:
            del self._child_references[uuid]
        else:
            self.logger.warning(f"尝试删除不存在的子Workable引用: {uuid}")
        
        # 删除所有相关Frame
        frames = self.content.get_frame_by_uuid(uuid, frame_type="child")
        for frame in frames:
            self.content.remove_frame(frame.seq)
        
        self.logger.debug(f"删除子Workable: {uuid}")
        return bool(frames)
    
    def get_children(self) -> List['Workable']:
        """
        获取所有子Workable (仅复杂模式)
        
        Returns:
            子Workable列表
            
        Raises:
            AttributeError: 如果在简单模式下调用
        """
        if self.is_atom():
            raise AttributeError("简单Workable没有子Workable")
        
        result = []
        child_frames = self.content.get_frames_by_type("child")
        
        for frame in child_frames:
            uuid = frame.get_reference_uuid()
            
            # 首先检查缓存
            if uuid in self._child_references:
                result.append(self._child_references[uuid])
                continue
                
            # 然后尝试从管理器获取
            if self.manager:
                child = self.manager.get_workable(uuid)
                if child:
                    # 更新缓存
                    self._child_references[uuid] = child
                    result.append(child)
        
        return result
    
    @property
    def child_workables(self) -> Dict[str, 'Workable']:
        """
        获取所有子Workable的字典 (向后兼容属性)
        
        Returns:
            子Workable字典
        """
        if self.is_atom():
            return {}
        
        result = {}
        for child in self.get_children():
            result[child.uuid] = child
        
        return result
    
    @child_workables.setter
    def child_workables(self, value: Dict[str, 'Workable']) -> None:
        """
        设置子Workable字典 (向后兼容，仅更新缓存)
        
        Args:
            value: 子Workable字典
        """
        if self.is_atom():
            return
            
        self._child_references = value or {}
    
    # 本地Workable方法
    
    def add_local(self, local: 'Workable') -> None:
        """
        添加本地Workable
        
        Args:
            local: 要添加的本地Workable
        """
        if not local.is_atom():
            raise WorkableError(f"本地Workable必须是简单类型: {local}")
        
        # 标记为本地
        local.is_local = True
        
        # 缓存引用 (向后兼容)
        self._local_references[local.uuid] = local
        
        # 添加索引
        self.content.add_frame(
            name=local.name,
            logic_description=local.logic_description,
            frame_type="local",
            uuid=local.uuid,
            is_local=True
        )
        
        self.logger.debug(f"添加本地Workable: {local.uuid}")
    
    def remove_local(self, uuid: str) -> bool:
        """
        删除本地Workable
        
        Args:
            uuid: 要删除的本地Workable的UUID
            
        Returns:
            是否成功删除
        """
        # 从缓存中删除
        if uuid in self._local_references:
            del self._local_references[uuid]
        else:
            self.logger.warning(f"尝试删除不存在的本地Workable引用: {uuid}")
        
        # 删除所有相关Frame
        frames = self.content.get_frame_by_uuid(uuid, frame_type="local")
        for frame in frames:
            self.content.remove_frame(frame.seq)
        
        self.logger.debug(f"删除本地Workable: {uuid}")
        return bool(frames)
    
    def get_locals(self) -> List['Workable']:
        """
        获取所有本地Workable
        
        Returns:
            本地Workable列表
        """
        result = []
        local_frames = self.content.get_frames_by_type("local")
        
        for frame in local_frames:
            uuid = frame.get_reference_uuid()
            
            # 首先检查缓存
            if uuid in self._local_references:
                result.append(self._local_references[uuid])
                continue
                
            # 这里不从管理器获取，因为本地Workable应该始终在缓存中
            
        return result
    
    @property
    def local_workables(self) -> Dict[str, 'Workable']:
        """
        获取所有本地Workable的字典 (向后兼容属性)
        
        Returns:
            本地Workable字典
        """
        result = {}
        for local in self.get_locals():
            result[local.uuid] = local
        
        return result
    
    @local_workables.setter
    def local_workables(self, value: Dict[str, 'Workable']) -> None:
        """
        设置本地Workable字典 (向后兼容，仅更新缓存)
        
        Args:
            value: 本地Workable字典
        """
        self._local_references = value or {}
    
    # 序列化与反序列化
        
    def to_dict(self, include_content: bool = True) -> Dict[str, Any]:
        """
        将Workable转换为字典表示
        
        Args:
            include_content: 是否包含内容
            
        Returns:
            Workable的字典表示
        """
        result = {
            "uuid": self.uuid,
            "name": self.name,
            "logic_description": self.logic_description,
            "is_atom": self.is_atom(),
        }
        
        if self.is_atom() and include_content:
            result["content"] = self.content.content
            result["content_type"] = self.content.content_type
        
        # 不包含子Workable和本地Workable，它们通过索引引用
        
        return result
    
    def __repr__(self) -> str:
        type_str = "SimpleWorkable" if self.is_atom() else "ComplexWorkable"
        return f"<{type_str} uuid={self.uuid[:6]} name={self.name}>"


# 兼容性转换函数

def convert_simple_to_complex(workable: Workable) -> Workable:
    """
    将简单Workable转换为复杂Workable
    
    Args:
        workable: 要转换的简单Workable
        
    Returns:
        转换后的复杂Workable
        
    Raises:
        ConversionError: 如果转换失败
    """
    if not workable.is_atom():
        raise ConversionError(f"只能转换简单类型的Workable: {workable}")
    
    # 使用内部状态转换
    return workable.make_complex()


def convert_complex_to_simple(workable: Workable) -> Optional[Workable]:
    """
    将复杂Workable转换为简单Workable
    
    Args:
        workable: 要转换的复杂Workable
        
    Returns:
        转换后的简单Workable，如果无法转换则返回None
    
    Raises:
        ConversionError: 如果转换失败
    """
    if workable.is_atom():
        raise ConversionError(f"只能转换复杂类型的Workable: {workable}")
    
    try:
        # 使用内部状态转换
        return workable.make_simple()
    except ConversionError:
        # 如果无法转换，返回None
        return None 