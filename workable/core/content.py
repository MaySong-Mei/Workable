"""
内容管理模块 - 负责管理Workable的内容结构
"""

import logging
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from workable.core.models import WorkableFrame
from workable.core.exceptions import ContentError

# 避免循环导入
if TYPE_CHECKING:
    from workable.core.workable import SimpleWorkable

class Content:
    """
    内容管理类，负责管理WorkableFrame序列和本地Workable
    采用封装与代理访问模式确保数据一致性
    """
    
    def __init__(self):
        """初始化内容管理器"""
        self._sequence: List[WorkableFrame] = []
        self._local_workables: Dict[str, 'SimpleWorkable'] = {}
        self.logger = logging.getLogger('content')
    
    @property
    def frames(self) -> List[WorkableFrame]:
        """只读访问frames"""
        return self._sequence.copy()
    
    @property
    def frame_count(self) -> int:
        """获取frames数量，兼容旧API"""
        return len(self._sequence)
    
    @property
    def workables(self) -> Dict[str, 'SimpleWorkable']:
        """只读访问workables"""
        return self._local_workables.copy()
    
    def get_frame(self, index: int) -> Optional[WorkableFrame]:
        """
        获取指定索引的Frame
        
        Args:
            index: Frame索引
            
        Returns:
            指定的Frame，如果索引无效则返回None
        """
        if 0 <= index < len(self._sequence):
            return self._sequence[index]
        return None
    
    def get_main_frame(self) -> Optional[WorkableFrame]:
        """
        获取主Frame（第一个Frame）
        
        Returns:
            主Frame，如果没有Frame则返回None
        """
        if self._sequence:
            return self._sequence[0]
        return None
    
    def get_workable(self, uuid: str) -> Optional['SimpleWorkable']:
        """
        获取指定UUID的本地Workable
        
        Args:
            uuid: Workable的UUID
            
        Returns:
            指定的Workable，如果不存在则返回None
        """
        return self._local_workables.get(uuid)
    
    def add_frame(self, frame: WorkableFrame) -> int:
        """
        添加Frame到序列
        
        Args:
            frame: 要添加的Frame
            
        Returns:
            添加的Frame的索引
        """
        if not isinstance(frame, WorkableFrame):
            raise ContentError(f"无效的Frame对象: {frame}")
        
        self._sequence.append(frame)
        self.logger.debug(f"添加Frame: {frame.name}")
        return len(self._sequence) - 1
    
    def add_local_workable(self, workable: 'SimpleWorkable') -> int:
        """
        添加本地Workable并创建对应的Frame
        
        Args:
            workable: 要添加的本地Workable
            
        Returns:
            添加的Frame的索引
        """
        try:
            if not workable or not hasattr(workable, 'uuid'):
                raise ContentError("无效的Workable对象")
                
            if workable.uuid in self._local_workables:
                raise ContentError(f"Workable {workable.uuid} 已存在")
            
            self._local_workables[workable.uuid] = workable
            
            # 创建并添加对应的Frame
            frame = WorkableFrame(
                name=workable.name,
                logic_description=workable.logic_description,
                lnref=workable.uuid
            )
            self._sequence.append(frame)
            
            self.logger.debug(f"添加本地Workable: {workable.uuid}")
            return len(self._sequence) - 1
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"添加本地Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def update_workable(self, uuid: str, name: str = None, 
                      logic_description: str = None) -> bool:
        """
        更新Workable和对应的所有Frame
        
        Args:
            uuid: Workable的UUID
            name: 新的名称，如果为None则不更新
            logic_description: 新的逻辑描述，如果为None则不更新
            
        Returns:
            是否成功更新
        """
        try:
            if uuid not in self._local_workables:
                raise ContentError(f"Workable {uuid} 不存在")
            
            # 更新Workable
            workable = self._local_workables[uuid]
            if name:
                workable.name = name
            if logic_description:
                workable.logic_description = logic_description
            
            # 同步更新所有引用此Workable的Frame
            for frame in self._sequence:
                if frame.lnref == uuid:
                    if name:
                        frame.name = name
                    if logic_description:
                        frame.logic_description = logic_description
            
            self.logger.debug(f"更新Workable: {uuid}")
            return True
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"更新Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def remove_frame(self, index: int) -> Optional[WorkableFrame]:
        """
        移除指定索引的Frame
        
        Args:
            index: Frame索引
            
        Returns:
            被移除的Frame，如果索引无效则返回None
        """
        try:
            if not (0 <= index < len(self._sequence)):
                raise ContentError(f"索引 {index} 超出范围")
            
            frame = self._sequence.pop(index)
            self.logger.debug(f"移除Frame: 索引 {index}")
            return frame
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"移除Frame失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def remove_local_workable(self, uuid: str) -> bool:
        """
        删除本地Workable及其所有Frame
        
        Args:
            uuid: Workable的UUID
            
        Returns:
            是否成功删除
        """
        try:
            if uuid not in self._local_workables:
                raise ContentError(f"Workable {uuid} 不存在")
            
            # 先保存序列中有这个lnref的索引位置
            indices = [i for i, f in enumerate(self._sequence) if f.lnref == uuid]
            
            # 删除Workable
            del self._local_workables[uuid]
            
            # 删除所有引用
            self._sequence = [f for f in self._sequence if f.lnref != uuid]
            
            self.logger.debug(f"删除本地Workable: {uuid}, 影响Frame位置: {indices}")
            return True
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"删除Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def move_frame(self, from_index: int, to_index: int) -> bool:
        """
        移动Frame位置
        
        Args:
            from_index: 源索引
            to_index: 目标索引
            
        Returns:
            是否成功移动
        """
        try:
            if not (0 <= from_index < len(self._sequence)):
                raise ContentError(f"源索引 {from_index} 超出范围")
            
            if not (0 <= to_index < len(self._sequence)):
                raise ContentError(f"目标索引 {to_index} 超出范围")
            
            # 记录要移动的Frame
            frame = self._sequence.pop(from_index)
            # 插入到新位置
            self._sequence.insert(to_index, frame)
            
            self.logger.debug(f"移动Frame: {from_index} -> {to_index}")
            return True
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"移动Frame失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def validate(self) -> Tuple[bool, List[int], List[str]]:
        """
        验证内部一致性
        
        Returns:
            元组 (是否有效, 孤立Frame索引列表, 幽灵Workable UUID列表)
        """
        orphan_frames = []
        for i, frame in enumerate(self._sequence):
            if frame.lnref and frame.lnref not in self._local_workables:
                orphan_frames.append(i)
        
        ghost_workables = []
        for uuid in self._local_workables:
            if not any(f.lnref == uuid for f in self._sequence):
                ghost_workables.append(uuid)
        
        is_valid = not orphan_frames and not ghost_workables
        if not is_valid:
            self.logger.warning(f"验证失败: 孤立Frames={orphan_frames}, 幽灵Workables={ghost_workables}")
        
        return is_valid, orphan_frames, ghost_workables
    
    def repair(self) -> bool:
        """
        修复一致性问题
        
        Returns:
            是否成功修复
        """
        try:
            is_valid, orphan_frames, ghost_workables = self.validate()
            if is_valid:
                return True
            
            # 修复孤立Frame
            for idx in sorted(orphan_frames, reverse=True):
                del self._sequence[idx]
            
            # 修复幽灵Workable
            for uuid in ghost_workables:
                workable = self._local_workables[uuid]
                frame = WorkableFrame(
                    name=workable.name,
                    logic_description=workable.logic_description,
                    lnref=workable.uuid
                )
                self._sequence.append(frame)
            
            self.logger.info(f"修复了 {len(orphan_frames)} 个孤立Frames和 {len(ghost_workables)} 个幽灵Workables")
            return True
        except Exception as e:
            self.logger.error(f"修复失败: {str(e)}")
            raise ContentError(f"修复一致性问题失败: {str(e)}") 