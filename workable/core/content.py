"""
内容管理模块 - 负责管理Workable的内容结构
实现索引式存储机制，分离内容和引用
"""

import logging
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING, Any, Set

from workable.core.models import WorkableFrame
from workable.core.exceptions import ContentError

# 避免循环导入
if TYPE_CHECKING:
    from workable.core.workable import Workable

class Content:
    """
    内容管理类，实现索引式存储
    负责管理WorkableFrame序列和引用关系
    采用封装与代理访问模式确保数据一致性
    """
    
    def __init__(self, content_type: str = "text", content: str = ""):
        """初始化内容管理器"""
        # 基本内容属性
        self.content_type = content_type
        self.content = content
        
        # 序列化的框架索引存储
        self._frames_by_seq: Dict[int, WorkableFrame] = {}  # 按序列号索引
        self._frames_by_uuid: Dict[str, Set[int]] = {}  # UUID到序列号映射
        self._frames_by_type: Dict[str, Set[int]] = {}  # 类型到序列号映射
        self._next_seq: int = 1  # 下一个可用序列号
        
        # 缓存本地工作单元引用 (仅缓存，不存储)
        self._local_workables_cache: Dict[str, 'Workable'] = {}
        
        self.logger = logging.getLogger('content')
    
    @property
    def frames(self) -> List[WorkableFrame]:
        """按序列号顺序获取所有frames"""
        return [self._frames_by_seq[seq] for seq in sorted(self._frames_by_seq.keys())]
    
    @property
    def frame_count(self) -> int:
        """获取frames数量"""
        return len(self._frames_by_seq)
    
    @property
    def workables(self) -> Dict[str, 'Workable']:
        """获取本地workables缓存（只读）"""
        return self._local_workables_cache.copy()
    
    def get_frame(self, seq: int) -> Optional[WorkableFrame]:
        """
        获取指定序列号的Frame
        
        Args:
            seq: Frame序列号
            
        Returns:
            指定的Frame，如果序列号无效则返回None
        """
        return self._frames_by_seq.get(seq)
    
    def get_frame_by_uuid(self, uuid: str, frame_type: Optional[str] = None) -> List[WorkableFrame]:
        """
        获取指定UUID引用的所有Frame
        
        Args:
            uuid: 工作单元UUID
            frame_type: 可选的帧类型筛选
            
        Returns:
            所有引用此UUID的Frame列表
        """
        if uuid not in self._frames_by_uuid:
            return []
        
        frames = [self._frames_by_seq[seq] for seq in self._frames_by_uuid[uuid]]
        
        if frame_type:
            frames = [f for f in frames if f.frame_type == frame_type]
            
        return frames
    
    def get_main_frame(self) -> Optional[WorkableFrame]:
        """
        获取主Frame（序列号最小的Frame）
        
        Returns:
            主Frame，如果没有Frame则返回None
        """
        if not self._frames_by_seq:
            return None
        min_seq = min(self._frames_by_seq.keys())
        return self._frames_by_seq[min_seq]
    
    def get_workable(self, uuid: str) -> Optional['Workable']:
        """
        获取指定UUID的本地Workable（从缓存）
        
        Args:
            uuid: Workable的UUID
            
        Returns:
            指定的Workable，如果不存在则返回None
        """
        return self._local_workables_cache.get(uuid)
    
    def add_frame(self, name: str, logic_description: str, 
                frame_type: str = "reference", uuid: Optional[str] = None, 
                is_local: bool = False, metadata: Dict[str, Any] = None) -> int:
        """
        添加Frame到索引系统
        
        Args:
            name: Frame名称
            logic_description: 逻辑描述
            frame_type: 帧类型 (reference, child, local)
            uuid: 引用的工作单元UUID
            is_local: 是否为本地引用
            metadata: 元数据字典
            
        Returns:
            添加的Frame的序列号
        """
        if not name or not logic_description:
            raise ContentError("框架名称和逻辑描述不能为空")
            
        if uuid is None and frame_type != "empty":
            raise ContentError("引用框架必须指定UUID")
            
        # 创建新框架
        seq = self._next_seq
        self._next_seq += 1
        
        # 如果是本地引用，确保frame_type是local
        if is_local:
            frame_type = "local"
            
        frame = WorkableFrame(
            name=name,
            logic_description=logic_description,
            seq=seq,
            frame_type=frame_type,
            exref=uuid,
            metadata=metadata
        )
        
        # 添加到索引
        self._frames_by_seq[seq] = frame
        
        if uuid:
            if uuid not in self._frames_by_uuid:
                self._frames_by_uuid[uuid] = set()
            self._frames_by_uuid[uuid].add(seq)
        
        if frame_type not in self._frames_by_type:
            self._frames_by_type[frame_type] = set()
        self._frames_by_type[frame_type].add(seq)
        
        self.logger.debug(f"添加Frame: seq={seq}, type={frame_type}, uuid={uuid}")
        return seq
    
    def add_local_workable(self, workable: 'Workable') -> int:
        """
        添加本地Workable并创建对应的Frame
        
        Args:
            workable: 要添加的本地Workable
            
        Returns:
            添加的Frame的序列号
        """
        try:
            if not workable or not hasattr(workable, 'uuid'):
                raise ContentError("无效的Workable对象")
                
            if workable.uuid in self._local_workables_cache:
                raise ContentError(f"Workable {workable.uuid} 已存在")
            
            # 添加到缓存
            self._local_workables_cache[workable.uuid] = workable
            
            # 创建并添加对应的Frame
            seq = self.add_frame(
                name=workable.name,
                logic_description=workable.logic_description,
                frame_type="local",
                uuid=workable.uuid,
                is_local=True
            )
            
            self.logger.debug(f"添加本地Workable: {workable.uuid}, seq={seq}")
            return seq
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"添加本地Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def update_frame(self, seq: int, name: Optional[str] = None, 
                   logic_description: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        更新指定序列号的Frame
        
        Args:
            seq: Frame序列号
            name: 新的名称
            logic_description: 新的逻辑描述
            metadata: 要更新的元数据
            
        Returns:
            是否成功更新
        """
        if seq not in self._frames_by_seq:
            self.logger.warning(f"尝试更新不存在的Frame: seq={seq}")
            return False
            
        frame = self._frames_by_seq[seq]
        
        if name:
            frame.name = name
        if logic_description:
            frame.logic_description = logic_description
        if metadata:
            for key, value in metadata.items():
                frame.update_metadata(key, value)
                
        self.logger.debug(f"更新Frame: seq={seq}")
        return True
    
    def update_workable(self, uuid: str, name: Optional[str] = None, 
                      logic_description: Optional[str] = None) -> bool:
        """
        更新Workable和对应的所有Frame
        
        Args:
            uuid: Workable的UUID
            name: 新的名称
            logic_description: 新的逻辑描述
            
        Returns:
            是否成功更新
        """
        try:
            if uuid not in self._local_workables_cache:
                raise ContentError(f"Workable {uuid} 不存在")
            
            # 更新Workable
            workable = self._local_workables_cache[uuid]
            if name:
                workable.name = name
            if logic_description:
                workable.logic_description = logic_description
            
            # 同步更新所有引用此Workable的Frame
            if uuid in self._frames_by_uuid:
                for seq in self._frames_by_uuid[uuid]:
                    frame = self._frames_by_seq[seq]
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
    
    def remove_frame(self, seq: int) -> Optional[WorkableFrame]:
        """
        移除指定序列号的Frame
        
        Args:
            seq: Frame序列号
            
        Returns:
            被移除的Frame，如果序列号无效则返回None
        """
        try:
            if seq not in self._frames_by_seq:
                raise ContentError(f"序列号 {seq} 不存在")
            
            frame = self._frames_by_seq[seq]
            
            # 从序列号索引中移除
            del self._frames_by_seq[seq]
            
            # 更新UUID索引
            ref_uuid = frame.get_reference_uuid()
            if ref_uuid and ref_uuid in self._frames_by_uuid:
                self._frames_by_uuid[ref_uuid].discard(seq)
                if not self._frames_by_uuid[ref_uuid]:
                    del self._frames_by_uuid[ref_uuid]
            
            # 更新类型索引
            if frame.frame_type in self._frames_by_type:
                self._frames_by_type[frame.frame_type].discard(seq)
                if not self._frames_by_type[frame.frame_type]:
                    del self._frames_by_type[frame.frame_type]
            
            self.logger.debug(f"移除Frame: seq={seq}")
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
            if uuid not in self._local_workables_cache:
                raise ContentError(f"Workable {uuid} 不存在")
            
            # 记录要删除的序列号
            seqs_to_remove = []
            if uuid in self._frames_by_uuid:
                seqs_to_remove = list(self._frames_by_uuid[uuid])
            
            # 从缓存中删除
            del self._local_workables_cache[uuid]
            
            # 删除所有相关Frame
            for seq in sorted(seqs_to_remove, reverse=True):
                self.remove_frame(seq)
            
            self.logger.debug(f"删除本地Workable: {uuid}, 影响Frame数量: {len(seqs_to_remove)}")
            return True
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"删除Workable失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def move_frame(self, from_seq: int, to_seq: int) -> bool:
        """
        调整Frame序列号（重新排序）
        
        Args:
            from_seq: 源序列号
            to_seq: 目标序列号
            
        Returns:
            是否成功移动
        """
        try:
            if from_seq not in self._frames_by_seq:
                raise ContentError(f"源序列号 {from_seq} 不存在")
            
            if to_seq < 0:
                raise ContentError(f"目标序列号 {to_seq} 无效")
                
            if from_seq == to_seq:
                return True  # 无需移动
            
            # 获取要移动的Frame
            frame = self._frames_by_seq[from_seq]
            
            # 生成新的序列号空间
            new_frames_by_seq = {}
            
            # 重建序列号索引
            for seq, f in sorted(self._frames_by_seq.items()):
                if seq == from_seq:
                    continue  # 跳过要移动的
                    
                new_seq = seq
                if (from_seq < to_seq and seq > from_seq and seq <= to_seq):
                    new_seq = seq - 1  # 向前移动
                elif (from_seq > to_seq and seq >= to_seq and seq < from_seq):
                    new_seq = seq + 1  # 向后移动
                    
                f.seq = new_seq
                new_frames_by_seq[new_seq] = f
                
                # 更新UUID索引
                ref_uuid = f.get_reference_uuid()
                if ref_uuid in self._frames_by_uuid:
                    if seq in self._frames_by_uuid[ref_uuid]:
                        self._frames_by_uuid[ref_uuid].discard(seq)
                        self._frames_by_uuid[ref_uuid].add(new_seq)
            
            # 添加移动的Frame到新位置
            frame.seq = to_seq
            new_frames_by_seq[to_seq] = frame
            
            # 更新UUID索引
            ref_uuid = frame.get_reference_uuid()
            if ref_uuid in self._frames_by_uuid:
                if from_seq in self._frames_by_uuid[ref_uuid]:
                    self._frames_by_uuid[ref_uuid].discard(from_seq)
                    self._frames_by_uuid[ref_uuid].add(to_seq)
            
            # 使用新索引替换旧索引
            self._frames_by_seq = new_frames_by_seq
            
            # 更新下一个序列号
            self._next_seq = max(self._frames_by_seq.keys()) + 1 if self._frames_by_seq else 0
            
            self.logger.debug(f"移动Frame: {from_seq} -> {to_seq}")
            return True
        except Exception as e:
            if not isinstance(e, ContentError):
                e = ContentError(f"移动Frame失败: {str(e)}")
            self.logger.error(str(e))
            raise e
    
    def get_frames_by_type(self, frame_type: str) -> List[WorkableFrame]:
        """
        获取指定类型的所有Frame
        
        Args:
            frame_type: 帧类型
            
        Returns:
            所有该类型的Frame列表
        """
        if frame_type not in self._frames_by_type:
            return []
            
        result = []
        for seq in self._frames_by_type[frame_type]:
            frame = self._frames_by_seq[seq]
            result.append(frame)
                
        return result
    
    def clear_cache(self) -> None:
        """
        清除本地工作单元缓存
        注意：这只会清除缓存，不会删除实际的Frame
        """
        self._local_workables_cache = {}
        self.logger.debug("清除本地Workable缓存")
    
    def validate(self) -> Tuple[bool, List[int], List[str]]:
        """
        验证内部一致性
        
        Returns:
            元组 (是否有效, 孤立Frame序列号列表, 幽灵Workable UUID列表)
        """
        # 检查孤立Frame
        orphan_frames = []
        for seq, frame in self._frames_by_seq.items():
            ref_uuid = frame.get_reference_uuid()
            if ref_uuid and frame.is_local() and ref_uuid not in self._local_workables_cache:
                orphan_frames.append(seq)
        
        # 检查幽灵Workable
        ghost_workables = []
        for uuid in self._local_workables_cache:
            if uuid not in self._frames_by_uuid:
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
            for seq in sorted(orphan_frames, reverse=True):
                self.remove_frame(seq)
            
            # 修复幽灵Workable
            for uuid in ghost_workables:
                workable = self._local_workables_cache[uuid]
                self.add_frame(
                    name=workable.name,
                    logic_description=workable.logic_description,
                    frame_type="local",
                    uuid=workable.uuid,
                    is_local=True
                )
            
            self.logger.info(f"修复了 {len(orphan_frames)} 个孤立Frames和 {len(ghost_workables)} 个幽灵Workables")
            return True
        except Exception as e:
            self.logger.error(f"修复失败: {str(e)}")
            raise ContentError(f"修复一致性问题失败: {str(e)}")
    
    def clear_frames(self) -> None:
        """
        清空所有框架
        """
        self._frames_by_seq.clear()
        self._frames_by_uuid.clear()
        self._frames_by_type.clear()
        self._next_seq = 1
        
        self.logger.debug("清空所有框架") 