"""
Workable管理模块 - 负责工作单元的创建、注册和查找
支持索引式Workable管理，分离存储和引用
"""

import uuid
import logging
from typing import Dict, List, Optional, Set, Any

from workable.core.workable import Workable
from workable.core.exceptions import WorkableError, ManagerError


class WorkableManager:
    """
    Workable管理器，负责工作单元的创建和索引
    支持基于索引的工作单元管理，实现解耦存储
    """
    
    def __init__(self):
        """初始化WorkableManager"""
        self._workables: Dict[str, Workable] = {}  # UUID -> Workable
        self._workable_by_name: Dict[str, Set[str]] = {}  # name -> set(UUID)
        
        self.logger = logging.getLogger('workable_manager')
    
    def register(self, workable: Workable) -> None:
        """
        注册工作单元到管理器
        
        Args:
            workable: 要注册的工作单元
            
        Raises:
            ManagerError: 如果工作单元已经存在
        """
        if not isinstance(workable, Workable):
            raise ManagerError("只能注册Workable对象")
            
        if workable.uuid in self._workables:
            raise ManagerError(f"UUID重复: {workable.uuid}")
            
        # 注册到主索引
        self._workables[workable.uuid] = workable
        
        # 注册到名称索引
        if workable.name not in self._workable_by_name:
            self._workable_by_name[workable.name] = set()
        self._workable_by_name[workable.name].add(workable.uuid)
        
        # 设置管理器引用
        workable.manager = self
        
        self.logger.debug(f"注册Workable: {workable.uuid} ({workable.name})")
        
    def create_workable(self, name: str, logic_description: str, is_atom: bool = True,
                      content: str = None, content_type: str = "code") -> Workable:
        """
        创建并注册工作单元
        
        Args:
            name: 工作单元名称
            logic_description: 逻辑描述
            is_atom: 是否为原子工作单元（简单模式）
            content: 内容字符串（仅简单模式适用）
            content_type: 内容类型（仅简单模式适用）
            
        Returns:
            创建的工作单元
            
        Raises:
            ManagerError: 如果创建失败
        """
        workable = Workable(
            name=name,
            logic_description=logic_description,
            is_atom=is_atom,
            content_str=content,
            content_type=content_type,
            manager=self
        )
        
        try:
            self.register(workable)
        except ManagerError as e:
            # 尝试处理UUID冲突
            if "UUID重复" in str(e):
                self.logger.warning(f"UUID冲突，重新生成: {workable.uuid}")
                workable.uuid = str(uuid.uuid4())
                self.register(workable)
            else:
                raise
        
        self.logger.info(f"创建{'原子' if is_atom else '复合'}工作单元: {workable.uuid} ({workable.name})")
        return workable
    
    def create_simple(self, name: str, logic_description: str, 
                     content: str = None, content_type: str = "code") -> Workable:
        """
        创建简单工作单元 (向后兼容方法)
        
        Args:
            name: 工作单元名称
            logic_description: 逻辑描述
            content: 内容字符串
            content_type: 内容类型
            
        Returns:
            创建的简单工作单元
        """
        return self.create_workable(
            name=name,
            logic_description=logic_description,
            is_atom=True,
            content=content,
            content_type=content_type
        )
    
    def create_complex(self, name: str, logic_description: str) -> Workable:
        """
        创建复杂工作单元 (向后兼容方法)
        
        Args:
            name: 工作单元名称
            logic_description: 逻辑描述
            
        Returns:
            创建的复杂工作单元
        """
        return self.create_workable(
            name=name,
            logic_description=logic_description,
            is_atom=False
        )
    
    def get_workable(self, uuid: str) -> Optional[Workable]:
        """
        通过UUID获取工作单元
        
        Args:
            uuid: 工作单元UUID
            
        Returns:
            工作单元，如果不存在则返回None
        """
        return self._workables.get(uuid)
    
    def get_by_name(self, name: str) -> List[Workable]:
        """
        通过名称获取工作单元
        
        Args:
            name: 工作单元名称
            
        Returns:
            工作单元列表
        """
        if name not in self._workable_by_name:
            return []
            
        return [self._workables[uuid] for uuid in self._workable_by_name[name] 
                if uuid in self._workables]
    
    def get_all(self) -> List[Workable]:
        """
        获取所有工作单元
        
        Returns:
            工作单元列表
        """
        return list(self._workables.values())
    
    def get_simple_workables(self) -> List[Workable]:
        """
        获取所有简单工作单元
        
        Returns:
            简单工作单元列表
        """
        return [w for w in self._workables.values() if w.is_atom()]
    
    def get_complex_workables(self) -> List[Workable]:
        """
        获取所有复杂工作单元
        
        Returns:
            复杂工作单元列表
        """
        return [w for w in self._workables.values() if not w.is_atom()]
    
    def delete(self, uuid: str) -> bool:
        """
        删除工作单元
        
        Args:
            uuid: 工作单元UUID
            
        Returns:
            是否成功删除
        """
        if uuid not in self._workables:
            self.logger.warning(f"尝试删除不存在的工作单元: {uuid}")
            return False
            
        workable = self._workables[uuid]
        
        # 从名称索引中删除
        if workable.name in self._workable_by_name:
            self._workable_by_name[workable.name].discard(uuid)
            if not self._workable_by_name[workable.name]:
                del self._workable_by_name[workable.name]
        
        # 从主索引中删除
        del self._workables[uuid]
        
        self.logger.info(f"删除工作单元: {uuid}")
        return True
    
    def clear(self) -> None:
        """
        清空所有工作单元
        """
        self._workables.clear()
        self._workable_by_name.clear()
        
        self.logger.info("清空所有工作单元")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将管理器转换为字典表示
        
        Returns:
            管理器的字典表示
        """
        return {
            "workable_count": len(self._workables),
            "simple_count": len(self.get_simple_workables()),
            "complex_count": len(self.get_complex_workables()),
        }
    
    def __repr__(self) -> str:
        return f"<WorkableManager workables={len(self._workables)}>" 