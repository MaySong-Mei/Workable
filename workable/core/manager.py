"""
Workable管理器 - 集中管理Workable实例的CRUD操作
"""

import logging
from typing import Dict, List, Optional, Tuple, Type

from workable.core.workable import (
    Workable, SimpleWorkable, ComplexWorkable,
    convert_simple_to_complex, convert_complex_to_simple
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
    
    def get_workables_by_type(self, workable_type: Type[Workable]) -> Dict[str, Workable]:
        """
        获取指定类型的Workable
        
        Args:
            workable_type: Workable类型
        
        Returns:
            指定类型的Workable字典
        """
        return {
            uuid: workable 
            for uuid, workable in self.workables.items() 
            if isinstance(workable, workable_type)
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
        if workable and isinstance(workable, SimpleWorkable):
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
    
    def create_simple(self, name: str, logic_description: str, content: str,
                      content_type: str = "code") -> SimpleWorkable:
        """
        创建SimpleWorkable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            content: 内容字符串
            content_type: 内容类型，默认为"code"
            
        Returns:
            创建的SimpleWorkable
            
        Raises:
            WorkableError: 如果创建失败
        """
        try:
            if not name or not isinstance(name, str):
                raise WorkableError("无效的name参数")
            
            workable = SimpleWorkable(name, logic_description, content, content_type)
            
            if workable.uuid in self.workables:
                raise WorkableError(f"UUID冲突: {workable.uuid}")
                
            self.workables[workable.uuid] = workable
            self.logger.info(f"创建SimpleWorkable: {workable.uuid}")
            return workable
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"创建SimpleWorkable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def create_complex(self, name: str, logic_description: str) -> ComplexWorkable:
        """
        创建ComplexWorkable
        
        Args:
            name: Workable名称
            logic_description: 逻辑描述
            
        Returns:
            创建的ComplexWorkable
            
        Raises:
            WorkableError: 如果创建失败
        """
        try:
            if not name or not isinstance(name, str):
                raise WorkableError("无效的name参数")
            
            workable = ComplexWorkable(name, logic_description)
            
            if workable.uuid in self.workables:
                raise WorkableError(f"UUID冲突: {workable.uuid}")
                
            self.workables[workable.uuid] = workable
            self.logger.info(f"创建ComplexWorkable: {workable.uuid}")
            return workable
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"创建ComplexWorkable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
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
        更新SimpleWorkable
        
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
            
            if not isinstance(workable, SimpleWorkable):
                raise WorkableError(f"Workable {uuid} 不是SimpleWorkable")
            
            if content:
                workable.update_content(content)
            
            if name or logic_description:
                workable.update(name, logic_description)
            
            self.logger.info(f"更新SimpleWorkable: {uuid}")
            return True
        except Exception as e:
            if not isinstance(e, WorkableError):
                e = WorkableError(f"更新SimpleWorkable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def update_complex_structure(self, uuid: str, add_child: str = None, 
                               remove_child: str = None) -> bool:
        """
        更新ComplexWorkable结构
        
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
            
            if not isinstance(workable, ComplexWorkable):
                raise WorkableError(f"Workable {uuid} 不是ComplexWorkable")
            
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
                e = WorkableError(f"更新ComplexWorkable结构失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def add_local_to_complex(self, complex_uuid: str, name: str, 
                            logic_description: str, content: str, 
                            content_type: str = "code") -> Optional[str]:
        """
        向ComplexWorkable添加本地Workable
        
        Args:
            complex_uuid: ComplexWorkable的UUID
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
                raise WorkableError(f"未找到ComplexWorkable: {complex_uuid}")
            
            if not isinstance(complex_work, ComplexWorkable):
                raise WorkableError(f"Workable {complex_uuid} 不是ComplexWorkable")
            
            # 创建本地Workable
            local_work = SimpleWorkable(name, logic_description, content, content_type)
            
            # 添加到ComplexWorkable
            complex_work.add_local(local_work)
            
            # 不需要添加到管理器，因为它是本地的
            self.logger.info(f"向ComplexWorkable添加本地Workable: {complex_uuid} -> {local_work.uuid}")
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
            
            # 从所有ComplexWorkable中删除对该Workable的引用
            for w_uuid, workable in self.workables.items():
                if isinstance(workable, ComplexWorkable) and uuid in workable.child_workables:
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
        将SimpleWorkable转换为ComplexWorkable
        
        Args:
            uuid: SimpleWorkable的UUID
            
        Returns:
            转换后的ComplexWorkable的UUID，如果转换失败则返回None
            
        Raises:
            ConversionError: 如果转换失败
        """
        try:
            workable = self.read(uuid)
            if not workable:
                raise ConversionError(f"未找到Workable: {uuid}")
            
            if not isinstance(workable, SimpleWorkable):
                raise ConversionError(f"Workable {uuid} 不是SimpleWorkable")
            
            # 执行转换
            complex_work = convert_simple_to_complex(workable)
            
            # 更新管理器
            del self.workables[uuid]
            self.workables[complex_work.uuid] = complex_work
            
            # 更新引用该Workable的ComplexWorkable
            for w_uuid, w in self.workables.items():
                if isinstance(w, ComplexWorkable) and uuid in w.child_workables:
                    w.remove_child(uuid)
                    w.add_child(complex_work)
            
            self.logger.info(f"转换SimpleWorkable为ComplexWorkable: {uuid} -> {complex_work.uuid}")
            return complex_work.uuid
        except Exception as e:
            if not isinstance(e, ConversionError):
                e = ConversionError(f"转换为ComplexWorkable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def convert_to_simple(self, uuid: str) -> Optional[str]:
        """
        将ComplexWorkable转换为SimpleWorkable
        
        Args:
            uuid: ComplexWorkable的UUID
            
        Returns:
            转换后的SimpleWorkable的UUID，如果转换失败则返回None
            
        Raises:
            ConversionError: 如果转换失败
        """
        try:
            workable = self.read(uuid)
            if not workable:
                raise ConversionError(f"未找到Workable: {uuid}")
            
            if not isinstance(workable, ComplexWorkable):
                raise ConversionError(f"Workable {uuid} 不是ComplexWorkable")
            
            # 检查是否有子Workable
            if workable.child_workables:
                raise ConversionError(f"无法转换含有子Workable的ComplexWorkable: {uuid}")
            
            # 检查是否有本地Workable
            if workable.content.workables:
                raise ConversionError(f"无法转换含有本地Workable的ComplexWorkable: {uuid}")
            
            # 执行转换
            simple_work = convert_complex_to_simple(workable)
            
            # 更新管理器
            del self.workables[uuid]
            self.workables[simple_work.uuid] = simple_work
            
            # 更新引用该Workable的ComplexWorkable
            for w_uuid, w in self.workables.items():
                if isinstance(w, ComplexWorkable) and uuid in w.child_workables:
                    w.remove_child(uuid)
                    w.add_child(simple_work)
            
            self.logger.info(f"转换ComplexWorkable为SimpleWorkable: {uuid} -> {simple_work.uuid}")
            return simple_work.uuid
        except Exception as e:
            if not isinstance(e, ConversionError):
                e = ConversionError(f"转换为SimpleWorkable失败: {str(e)}")
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
            if isinstance(workable, ComplexWorkable):
                # 添加β-workables的父引用
                for child_uuid in workable.child_workables.keys():
                    parent_map[child_uuid] = parent_uuid
                
                # 添加γ-workables的父引用
                for local_uuid in workable.content.workables.keys():
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
        simple_count = sum(1 for w in self.workables.values() if isinstance(w, SimpleWorkable))
        complex_count = sum(1 for w in self.workables.values() if isinstance(w, ComplexWorkable))
        
        # 获取总共的本地Workable数量
        local_count = 0
        for w in self.workables.values():
            if isinstance(w, ComplexWorkable):
                local_count += len(w.content.workables)
        
        # 获取根节点数量
        roots = self.get_all_roots()
        
        return {
            "total_workables": total,
            "simple_workables": simple_count,
            "complex_workables": complex_count,
            "local_workables": local_count,
            "root_workables": len(roots)
        } 