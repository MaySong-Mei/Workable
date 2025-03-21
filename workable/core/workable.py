"""
Workable核心模块 - 定义统一的Workable类，通过内部状态区分简单和复杂工作单元
"""

import uuid
import logging
from typing import Dict, List, Optional, Union

from workable.core.models import WorkableFrame, Relation
from workable.core.content import Content
from workable.core.message import MessageManager
from workable.core.relation import RelationManager
from workable.core.exceptions import WorkableError, ConversionError

class Workable:
    """
    统一的Workable类，通过内部状态区分简单(原子/γ-workable)和复杂(复合/α-workable)模式
    """
    
    def __init__(self, name: str, logic_description: str, is_atom: bool = True,
                 content_str: str = None, content_type: str = "code"):
        """
        初始化Workable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            is_atom: 是否为原子Workable (简单模式)
            content_str: 内容字符串 (仅在简单模式下使用)
            content_type: 内容类型 (仅在简单模式下使用)
        """
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.logic_description = logic_description
        self.is_atom_flag = is_atom  # 内部状态标识
        self.content = Content()
        self.message_manager = MessageManager()
        self.relation_manager = RelationManager()
        self.logger = logging.getLogger('workable')
        
        # 简单模式特有属性
        self._content_str = content_str if is_atom else None
        self._content_type = content_type if is_atom else None
        
        # 复杂模式特有属性
        self.child_workables = {} if not is_atom else None
        
        # 所有Workable都可以包含本地Workable
        self.local_workables = {}
        
    def to_frame(self) -> WorkableFrame:
        """
        将当前Workable转换为Frame
        
        Returns:
            包含当前Workable信息的Frame
        """
        return WorkableFrame(
            name=self.name,
            logic_description=self.logic_description,
            lnref=self.uuid
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
        
        # 如果有内容，创建本地Workable来保存它
        if self._content_str is not None:
            local_workable = Workable(
                name=f"{self.name}_content",
                logic_description=self.logic_description,
                is_atom=True,
                content_str=self._content_str,
                content_type=self._content_type
            )
            local_workable.is_local = True  # 标记为本地
            self.add_local(local_workable)
        
        # 状态转换
        self.is_atom_flag = False
        self._content_str = None
        self._content_type = None
        self.child_workables = {}
        
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
        
        # 检查是否可以转换
        if self.child_workables and len(self.child_workables) > 0:
            raise ConversionError(f"无法转换含有子Workable的复杂Workable: {self.uuid}")
        
        # 需要有且仅有一个本地Workable
        if len(self.local_workables) != 1:
            raise ConversionError(
                f"复杂Workable {self.uuid} 包含 {len(self.local_workables)} 个本地Workable，"
                f"无法转换为简单Workable（需要恰好1个）"
            )
        
        self.logger.info(f"开始将Workable {self.uuid} 从复杂类型转换为简单类型")
        
        # 获取唯一的本地Workable
        local_uuid = next(iter(self.local_workables.keys()))
        local_workable = self.local_workables[local_uuid]
        
        # 提取内容
        self._content_str = local_workable._content_str
        self._content_type = local_workable._content_type
        
        # 状态转换
        self.is_atom_flag = True
        self.local_workables = {}  # 清空本地Workable
        self.child_workables = None
        
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
        return self._content_str
    
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
        self._content_str = value
    
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
        return self._content_type
    
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
        self._content_type = value
    
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
        self._content_str = content_str
        self.logger.debug(f"更新Workable内容: {self.uuid}")
    
    # 复杂模式方法
    
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
        
        if child.uuid in self.child_workables:
            self.logger.warning(f"覆盖已存在的子Workable: {child.uuid}")
        
        self.child_workables[child.uuid] = child
        
        # 添加外部引用Frame
        frame = WorkableFrame(
            name=child.name,
            logic_description=child.logic_description,
            exref=child.uuid
        )
        self.content.add_frame(frame)
        
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
            raise AttributeError("简单Workable不能删除子Workable，请先调用make_complex()")
        
        if uuid not in self.child_workables:
            self.logger.warning(f"尝试删除不存在的子Workable: {uuid}")
            return False
        
        # 移除子Workable
        del self.child_workables[uuid]
        
        # 删除对应Frame
        frames_to_remove = []
        for i, frame in enumerate(self.content.frames):
            if frame.exref == uuid:
                frames_to_remove.append(i)
        
        for i in sorted(frames_to_remove, reverse=True):
            self.content.remove_frame(i)
        
        self.logger.debug(f"删除子Workable: {uuid}")
        return True
    
    def get_all_children(self) -> Dict[str, 'Workable']:
        """
        获取所有子Workable (仅复杂模式)
        
        Returns:
            所有子Workable的字典
            
        Raises:
            AttributeError: 如果在简单模式下调用
        """
        if self.is_atom():
            raise AttributeError("简单Workable没有子Workable")
        return self.child_workables.copy()
    
    # 本地Workable方法 (所有模式通用)
    
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
        
        # 添加到本地字典
        self.local_workables[local.uuid] = local
        
        # 如果是复杂模式，还要添加到Content
        if not self.is_atom():
            self.content.add_local_workable(local)
        
        self.logger.debug(f"添加本地Workable: {local.uuid}")
    
    def remove_local(self, uuid: str) -> bool:
        """
        删除本地Workable
        
        Args:
            uuid: 要删除的本地Workable的UUID
            
        Returns:
            是否成功删除
        """
        if uuid not in self.local_workables:
            self.logger.warning(f"尝试删除不存在的本地Workable: {uuid}")
            return False
        
        # 从本地字典中删除
        del self.local_workables[uuid]
        
        # 如果是复杂模式，还要从Content中删除
        if not self.is_atom():
            self.content.remove_local_workable(uuid)
        
        self.logger.debug(f"删除本地Workable: {uuid}")
        return True
    
    def get_all_locals(self) -> Dict[str, 'Workable']:
        """
        获取所有本地Workable
        
        Returns:
            所有本地Workable的字典
        """
        return self.local_workables.copy()
    
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