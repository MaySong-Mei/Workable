"""
Workable管理器 - 集中管理Workable实例的CRUD操作
"""

import logging
from typing import Dict, List, Optional, Tuple, Type

from workable.core.workable import (
    Workable, convert_simple_to_complex, convert_complex_to_simple
)
from workable.core.exceptions import WorkableError, ConversionError, ManagerError

class WorkableManager:
    """
    管理Workable的创建、读取、更新和删除
    """
    
    def __init__(self):
        """初始化Workable管理器"""
        self.workables: Dict[str, Workable] = {}
        self.logger = logging.getLogger('workable_manager')
    
    # 主要API方法
    
    def create_workable(self, name: str, logic_description: str, is_atom: bool = True,
                       content: str = None, content_type: str = "code") -> Workable:
        """
        创建Workable（统一接口）
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            is_atom: 是否为原子Workable (简单模式)
            content: 内容字符串 (仅在简单模式下使用)
            content_type: 内容类型 (仅在简单模式下使用)
            
        Returns:
            创建的Workable
            
        Raises:
            WorkableError: 如果创建失败
        """
        try:
            if not name or not isinstance(name, str):
                raise WorkableError("无效的name参数")
            
            # 创建Workable
            workable = Workable(
                name=name,
                logic_description=logic_description,
                is_atom=is_atom,
                content_str=content,
                content_type=content_type
            )
            
            if workable.uuid in self.workables:
                raise WorkableError(f"UUID冲突: {workable.uuid}")
                
            self.workables[workable.uuid] = workable
            
            # 根据类型记录日志
            type_str = "SimpleWorkable" if is_atom else "ComplexWorkable"
            self.logger.info(f"创建{type_str}: {workable.uuid}")
            
            return workable
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"创建Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    # 兼容性方法
    
    def create_simple(self, name: str, logic_description: str, content: str,
                      content_type: str = "code") -> Workable:
        """
        创建简单Workable (兼容性方法)
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            content: 内容字符串
            content_type: 内容类型，默认为"code"
            
        Returns:
            创建的简单Workable
            
        Raises:
            WorkableError: 如果创建失败
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
        创建复杂Workable (兼容性方法)
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            
        Returns:
            创建的复杂Workable
            
        Raises:
            WorkableError: 如果创建失败
        """
        return self.create_workable(
            name=name, 
            logic_description=logic_description, 
            is_atom=False
        )
    
    # 兼容测试API的方法
    
    def register_workable(self, workable: Workable) -> None:
        """
        注册Workable到管理器
        
        Args:
            workable: 要注册的Workable实例
        
        Raises:
            ManagerError: 如果Workable已存在或无效
        """
        if not isinstance(workable, Workable):
            raise WorkableError(f"无效的Workable对象: {workable}")
        
        if workable.uuid in self.workables:
            raise ManagerError(f"Workable已经存在: {workable.uuid}")
        
        self.workables[workable.uuid] = workable
        self.logger.info(f"注册Workable: {workable.uuid}")
    
    def unregister_workable(self, uuid: str) -> bool:
        """
        注销Workable
        
        Args:
            uuid: Workable的UUID
        
        Returns:
            是否成功注销
        """
        if uuid in self.workables:
            del self.workables[uuid]
            self.logger.info(f"注销Workable: {uuid}")
            return True
        else:
            self.logger.warning(f"尝试注销不存在的Workable: {uuid}")
            return False
    
    def get_workable(self, uuid: str) -> Optional[Workable]:
        """
        获取Workable
        
        Args:
            uuid: Workable的UUID
        
        Returns:
            Workable实例，如果不存在则返回None
        """
        return self.read(uuid)
    
    def get_all_workables(self) -> Dict[str, Workable]:
        """
        获取所有Workable
        
        Returns:
            所有Workable的字典副本
        """
        return self.workables.copy()
    
    def get_workables_by_type(self, is_atom: bool) -> Dict[str, Workable]:
        """
        获取指定类型的Workable
        
        Args:
            is_atom: 是否为原子Workable (简单模式)
        
        Returns:
            指定类型的Workable字典
        """
        return {
            uuid: workable 
            for uuid, workable in self.workables.items() 
            if workable.is_atom() == is_atom
        }
    
    def create_simple_workable(self, name: str, logic_description: str, 
                            content_str: str, content_type: str = "code") -> str:
        """
        创建SimpleWorkable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            content_str: 内容字符串
            content_type: 内容类型
        
        Returns:
            创建的SimpleWorkable的UUID
        """
        workable = self.create_simple(name, logic_description, content_str, content_type)
        return workable.uuid
    
    def create_complex_workable(self, name: str, logic_description: str) -> str:
        """
        创建ComplexWorkable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
        
        Returns:
            创建的ComplexWorkable的UUID
        """
        workable = self.create_complex(name, logic_description)
        return workable.uuid
    
    def update_workable(self, uuid: str, name: str = None, logic_description: str = None) -> bool:
        """
        更新Workable基本信息
        
        Args:
            uuid: Workable的UUID
            name: 新的名称
            logic_description: 新的逻辑描述
        
        Returns:
            是否成功更新
        """
        workable = self.read(uuid)
        if workable:
            workable.update(name, logic_description)
            self.logger.info(f"更新Workable: {uuid}")
            return True
        return False
    
    def update_simple_workable_content(self, uuid: str, content_str: str) -> bool:
        """
        更新SimpleWorkable内容
        
        Args:
            uuid: SimpleWorkable的UUID
            content_str: 新的内容
        
        Returns:
            是否成功更新
        """
        workable = self.read(uuid)
        if workable and workable.is_atom():
            workable.update_content(content_str)
            self.logger.info(f"更新SimpleWorkable内容: {uuid}")
            return True
        return False
    
    def delete_workable(self, uuid: str) -> bool:
        """
        删除Workable
        
        Args:
            uuid: Workable的UUID
        
        Returns:
            是否成功删除
        """
        try:
            return self.delete(uuid)
        except WorkableError:
            return False
    
    # 实际实现的方法
    
    def read(self, uuid: str) -> Optional[Workable]:
        """
        读取Workable
        
        Args:
            uuid: Workable的UUID
            
        Returns:
            指定的Workable，如果不存在则返回None
        """
        if not uuid or not isinstance(uuid, str):
            self.logger.warning(f"无效的uuid参数: {uuid}")
            return None
            
        result = self.workables.get(uuid)
        if not result:
            self.logger.warning(f"未找到Workable: {uuid}")
        return result
    
    def update_simple(self, uuid: str, content: str = None, 
                     name: str = None, logic_description: str = None) -> bool:
        """
        更新简单Workable
        
        Args:
            uuid: Workable的UUID
            content: 新的内容字符串，如果为None则不更新
            name: 新的名称，如果为None则不更新
            logic_description: 新的逻辑描述，如果为None则不更新
            
        Returns:
            是否成功更新
            
        Raises:
            WorkableError: 如果更新失败
        """
        try:
            workable = self.read(uuid)
            if not workable:
                raise WorkableError(f"未找到Workable: {uuid}")
            
            if not workable.is_atom():
                raise WorkableError(f"Workable {uuid} 不是简单类型")
            
            if content:
                workable.update_content(content)
            
            if name or logic_description:
                workable.update(name, logic_description)
            
            self.logger.info(f"更新简单Workable: {uuid}")
            return True
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"更新简单Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def update_complex_structure(self, uuid: str, add_child: str = None, 
                               remove_child: str = None) -> bool:
        """
        更新复杂Workable结构
        
        Args:
            uuid: Workable的UUID
            add_child: 要添加的子Workable的UUID，如果为None则不添加
            remove_child: 要删除的子Workable的UUID，如果为None则不删除
            
        Returns:
            是否成功更新
            
        Raises:
            WorkableError: 如果更新失败
        """
        try:
            workable = self.read(uuid)
            if not workable:
                raise WorkableError(f"未找到Workable: {uuid}")
            
            if not workable.is_complex():
                raise WorkableError(f"Workable {uuid} 不是复杂类型")
            
            if add_child:
                child = self.read(add_child)
                if not child:
                    raise WorkableError(f"未找到子Workable: {add_child}")
                workable.add_child(child)
                self.logger.info(f"添加子Workable: {uuid} -> {add_child}")
            
            if remove_child:
                if workable.remove_child(remove_child):
                    self.logger.info(f"删除子Workable: {uuid} -> {remove_child}")
            
            return True
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"更新复杂Workable结构失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def add_local_to_complex(self, complex_uuid: str, name: str, 
                            logic_description: str, content: str, 
                            content_type: str = "code") -> Optional[str]:
        """
        向复杂Workable添加本地Workable
        
        Args:
            complex_uuid: 复杂Workable的UUID
            name: 本地Workable的名称
            logic_description: 本地Workable的逻辑描述
            content: 本地Workable的内容
            content_type: 本地Workable的内容类型，默认为"code"
            
        Returns:
            添加的本地Workable的UUID，如果添加失败则返回None
            
        Raises:
            WorkableError: 如果添加失败
        """
        try:
            complex_work = self.read(complex_uuid)
            if not complex_work:
                raise WorkableError(f"未找到复杂Workable: {complex_uuid}")
            
            if not complex_work.is_complex():
                raise WorkableError(f"Workable {complex_uuid} 不是复杂类型")
            
            # 创建本地Workable
            local_work = Workable(
                name=name, 
                logic_description=logic_description,
                is_atom=True,
                content_str=content,
                content_type=content_type
            )
            
            # 添加到复杂Workable
            complex_work.add_local(local_work)
            
            # 不需要添加到管理器，因为它是本地的
            self.logger.info(f"向复杂Workable添加本地Workable: {complex_uuid} -> {local_work.uuid}")
            return local_work.uuid
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"添加本地Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def delete(self, uuid: str) -> bool:
        """
        删除Workable
        
        Args:
            uuid: Workable的UUID
            
        Returns:
            是否成功删除
            
        Raises:
            WorkableError: 如果删除失败
        """
        try:
            if not uuid or uuid not in self.workables:
                raise WorkableError(f"Workable不存在: {uuid}")
            
            # 从所有复杂Workable中删除对该Workable的引用
            for w_uuid, workable in self.workables.items():
                if workable.is_complex() and uuid in workable.child_workables:
                    workable.remove_child(uuid)
            
            # 删除Workable
            del self.workables[uuid]
            self.logger.info(f"删除Workable: {uuid}")
            return True
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"删除Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def convert_to_complex(self, uuid: str) -> Optional[str]:
        """
        将简单Workable转换为复杂Workable
        
        Args:
            uuid: 简单Workable的UUID
            
        Returns:
            转换后的Workable的UUID
            
        Raises:
            ConversionError: 如果转换失败
        """
        try:
            workable = self.read(uuid)
            if not workable:
                raise ConversionError(f"未找到Workable: {uuid}")
            
            if not workable.is_atom():
                raise ConversionError(f"Workable {uuid} 不是简单类型")
            
            # 执行转换
            workable.make_complex()
            
            self.logger.info(f"转换简单Workable为复杂Workable: {uuid}")
            return uuid  # 返回同一个UUID，因为是原地转换
        except Exception as e:
            if not isinstance(e, ConversionError):
                e = ConversionError(f"转换为复杂Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def convert_to_simple(self, uuid: str) -> Optional[str]:
        """
        将复杂Workable转换为简单Workable
        
        Args:
            uuid: 复杂Workable的UUID
            
        Returns:
            转换后的Workable的UUID
            
        Raises:
            ConversionError: 如果转换失败
        """
        try:
            workable = self.read(uuid)
            if not workable:
                raise ConversionError(f"未找到Workable: {uuid}")
            
            if workable.is_atom():
                raise ConversionError(f"Workable {uuid} 不是复杂类型")
            
            # 执行转换
            workable.make_simple()
            
            self.logger.info(f"转换复杂Workable为简单Workable: {uuid}")
            return uuid  # 返回同一个UUID，因为是原地转换
        except Exception as e:
            if not isinstance(e, ConversionError):
                e = ConversionError(f"转换为简单Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def get_all_roots(self) -> List[str]:
        """
        获取所有根Workable的UUID
        
        Returns:
            所有根Workable的UUID列表
        """
        parent_map = self.build_parent_map()
        all_uuids = set(self.workables.keys())
        children = set(parent_map.keys())
        return list(all_uuids - children)
    
    def build_parent_map(self) -> Dict[str, str]:
        """
        构建子Workable到父Workable的映射
        
        Returns:
            子UUID到父UUID的映射字典
        """
        parent_map = {}
        
        for parent_uuid, workable in self.workables.items():
            if workable.is_complex():
                # 添加子Workable的父引用
                for child_uuid in workable.child_workables.keys():
                    parent_map[child_uuid] = parent_uuid
                
                # 添加本地Workable的父引用
                for local_uuid in workable.local_workables.keys():
                    parent_map[local_uuid] = parent_uuid
        
        return parent_map
    
    def get_parent(self, uuid: str) -> Optional[str]:
        """
        获取Workable的父Workable UUID
        
        Args:
            uuid: Workable的UUID
            
        Returns:
            父Workable的UUID，如果不存在则返回None
        """
        parent_map = self.build_parent_map()
        return parent_map.get(uuid)
    
    def get_statistics(self) -> Dict:
        """
        获取Workable统计信息
        
        Returns:
            包含统计信息的字典
        """
        total = len(self.workables)
        simple_count = sum(1 for w in self.workables.values() if w.is_atom())
        complex_count = sum(1 for w in self.workables.values() if w.is_complex())
        
        # 获取总共的本地Workable数量
        local_count = 0
        for w in self.workables.values():
            local_count += len(w.local_workables)
        
        # 获取根节点数量
        roots = self.get_all_roots()
        
        return {
            "total_workables": total,
            "simple_workables": simple_count,
            "complex_workables": complex_count,
            "local_workables": local_count,
            "root_workables": len(roots)
        } 