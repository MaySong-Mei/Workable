"""
Workable核心模块 - 定义Workable基类和SimpleWorkable、ComplexWorkable子类
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
    Workable基类，包含基本的元数据和内容管理
    """
    
    def __init__(self, name: str, logic_description: str):
        """
        初始化Workable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
        """
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.logic_description = logic_description
        self.content = Content()
        self.message_manager = MessageManager()
        self.relation_manager = RelationManager()
        self.logger = logging.getLogger('workable')
    
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
    
    def is_atom(self) -> bool:
        """
        检查是否为原子Workable
        
        Returns:
            是否为原子Workable
        """
        raise NotImplementedError("子类必须实现is_atom方法")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} uuid={self.uuid[:6]} name={self.name}>"


class SimpleWorkable(Workable):
    """
    简单Workable (γ-workable)，存储原子内容
    """
    
    def __init__(self, name: str, logic_description: str, content_str: str, content_type: str = "code"):
        """
        初始化SimpleWorkable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            content_str: 内容字符串
            content_type: 内容类型，默认为"code"
        """
        super().__init__(name, logic_description)
        self.content_str = content_str
        self.content_type = content_type
        self.logger.debug(f"创建SimpleWorkable: {self.uuid}, type={content_type}")
    
    def update_content(self, content_str: str) -> None:
        """
        更新内容
        
        Args:
            content_str: 新的内容字符串
        """
        self.content_str = content_str
        self.logger.debug(f"更新SimpleWorkable内容: {self.uuid}")
    
    def is_atom(self) -> bool:
        """
        SimpleWorkable始终是原子的
        
        Returns:
            True
        """
        return True


class ComplexWorkable(Workable):
    """
    复杂Workable (α-workable)，可以包含β-workable和γ-workable
    """
    
    def __init__(self, name: str, logic_description: str):
        """
        初始化ComplexWorkable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
        """
        super().__init__(name, logic_description)
        self.child_workables: Dict[str, Workable] = {}  # β-workables
        self.logger.debug(f"创建ComplexWorkable: {self.uuid}")
    
    def add_child(self, child: Workable) -> None:
        """
        添加子Workable (β-workable)
        
        Args:
            child: 要添加的子Workable
        """
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
    
    def add_local(self, simple: SimpleWorkable) -> None:
        """
        添加本地Workable (γ-workable)
        
        Args:
            simple: 要添加的本地SimpleWorkable
        """
        if not isinstance(simple, SimpleWorkable):
            raise WorkableError(f"本地Workable必须是SimpleWorkable: {simple}")
        
        self.content.add_local_workable(simple)
        self.logger.debug(f"添加本地Workable: {simple.uuid}")
    
    def remove_child(self, uuid: str) -> bool:
        """
        删除子Workable (β-workable)
        
        Args:
            uuid: 要删除的子Workable的UUID
            
        Returns:
            是否成功删除
        """
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
    
    def remove_local(self, uuid: str) -> bool:
        """
        删除本地Workable (γ-workable)
        
        Args:
            uuid: 要删除的本地Workable的UUID
            
        Returns:
            是否成功删除
        """
        return self.content.remove_local_workable(uuid)
    
    def is_atom(self) -> bool:
        """
        ComplexWorkable不是原子的
        
        Returns:
            False
        """
        return False
    
    def get_all_children(self) -> Dict[str, Workable]:
        """
        获取所有子Workable
        
        Returns:
            所有子Workable的字典
        """
        return self.child_workables.copy()
    
    def get_all_locals(self) -> Dict[str, SimpleWorkable]:
        """
        获取所有本地Workable
        
        Returns:
            所有本地Workable的字典
        """
        return self.content.workables


def convert_simple_to_complex(simple_workable: SimpleWorkable) -> ComplexWorkable:
    """
    将SimpleWorkable转换为ComplexWorkable
    
    Args:
        simple_workable: 要转换的SimpleWorkable
        
    Returns:
        转换后的ComplexWorkable
        
    Raises:
        ConversionError: 如果转换失败
    """
    logger = logging.getLogger(__name__)
    
    if not isinstance(simple_workable, SimpleWorkable):
        raise ConversionError(f"无效的SimpleWorkable对象: {type(simple_workable)}")
    
    logger.info(f"开始将SimpleWorkable {simple_workable.uuid} 转换为ComplexWorkable")
    
    # 创建一个新的ComplexWorkable，复制基本属性
    complex_workable = ComplexWorkable(
        name=simple_workable.name,
        logic_description=simple_workable.logic_description
    )
    
    # 复制SimpleWorkable中的消息到ComplexWorkable
    for message in simple_workable.message_manager.get_all_messages():
        complex_workable.message_manager.append_message(message)
    
    # 复制SimpleWorkable中的关系到ComplexWorkable
    for relation in simple_workable.relation_manager.get_all():
        # 创建新的Relation对象而不是直接添加原始对象
        new_relation = Relation(relation.target_uuid, meta=relation.meta)
        complex_workable.relation_manager.add(new_relation)
    
    # 创建一个新的本地SimpleWorkable并添加到ComplexWorkable中
    local_simple = SimpleWorkable(
        name=f"{simple_workable.name}_content",
        logic_description=simple_workable.logic_description,
        content_str=simple_workable.content_str,
        content_type=simple_workable.content_type
    )
    complex_workable.add_local(local_simple)
    
    logger.info(f"SimpleWorkable {simple_workable.uuid} 已成功转换为ComplexWorkable {complex_workable.uuid}")
    
    return complex_workable


def convert_complex_to_simple(complex_workable: ComplexWorkable) -> Optional[SimpleWorkable]:
    """
    将ComplexWorkable转换为SimpleWorkable
    
    Args:
        complex_workable: 要转换的ComplexWorkable
        
    Returns:
        转换后的SimpleWorkable，如果无法转换则返回None
    
    Raises:
        ConversionError: 如果转换失败
    """
    logger = logging.getLogger(__name__)
    
    if not isinstance(complex_workable, ComplexWorkable):
        raise ConversionError(f"无效的ComplexWorkable对象: {type(complex_workable)}")
    
    # 检查是否可以转换：
    # 1. 无子Workable 
    # 2. 只有一个本地Workable
    if complex_workable.child_workables:
        logger.warning(f"ComplexWorkable {complex_workable.uuid} 包含子Workable，无法转换为SimpleWorkable")
        return None
    
    if len(complex_workable.content.workables) != 1:
        logger.warning(
            f"ComplexWorkable {complex_workable.uuid} 包含 {len(complex_workable.content.workables)} 个本地Workable，"
            f"无法转换为SimpleWorkable（需要恰好1个）"
        )
        return None
    
    logger.info(f"开始将ComplexWorkable {complex_workable.uuid} 转换为SimpleWorkable")
    
    # 获取唯一的本地Workable
    local_uuid = next(iter(complex_workable.content.workables.keys()))
    local_workable = complex_workable.content.workables[local_uuid]
    
    # 创建一个新的SimpleWorkable，使用本地Workable的内容
    simple_workable = SimpleWorkable(
        name=complex_workable.name,
        logic_description=complex_workable.logic_description,
        content_str=local_workable.content_str,
        content_type=local_workable.content_type
    )
    
    # 复制ComplexWorkable中的消息到SimpleWorkable
    for message in complex_workable.message_manager.get_all_messages():
        simple_workable.message_manager.append_message(message)
    
    # 复制ComplexWorkable中的关系到SimpleWorkable
    for relation in complex_workable.relation_manager.get_all():
        # 创建新的Relation对象而不是直接添加原始对象
        new_relation = Relation(relation.target_uuid, meta=relation.meta)
        simple_workable.relation_manager.add(new_relation)
    
    logger.info(f"ComplexWorkable {complex_workable.uuid} 已成功转换为SimpleWorkable {simple_workable.uuid}")
    
    return simple_workable 