"""
关系管理模块 - 负责处理Workable间的关系
"""

import logging
from typing import Dict, List, Optional, Any

from workable.core.models import Relation
from workable.core.exceptions import RelationError

class RelationManager:
    """
    关系管理器 - 管理Workable之间的关系
    """
    
    def __init__(self):
        """初始化关系管理器"""
        self.relations = {}  # type: Dict[str, Relation]
        self.logger = logging.getLogger(__name__)
    
    def add(self, relation: Relation) -> None:
        """
        添加关系
        
        Args:
            relation: 关系对象
            
        Raises:
            RelationError: 如果关系对象无效
        """
        if not isinstance(relation, Relation):
            raise RelationError(f"无效的关系对象: {relation}")
        
        # 如果同一目标已有关系，则覆盖
        if relation.target_uuid in self.relations:
            self.logger.info(f"覆盖已存在的关系: {relation.target_uuid}")
        
        self.relations[relation.target_uuid] = relation
        self.logger.info(f"添加关系: {relation.target_uuid}")
    
    def remove(self, target_uuid: str) -> bool:
        """
        移除关系
        
        Args:
            target_uuid: 目标Workable的UUID
            
        Returns:
            是否成功移除
        """
        if target_uuid in self.relations:
            del self.relations[target_uuid]
            self.logger.info(f"移除关系: {target_uuid}")
            return True
        else:
            self.logger.warning(f"尝试移除不存在的关系: {target_uuid}")
            return False
    
    def update_meta(self, target_uuid: str, meta: Dict) -> bool:
        """
        更新关系元数据
        
        Args:
            target_uuid: 目标Workable的UUID
            meta: 新的元数据字典
            
        Returns:
            是否成功更新
        """
        if target_uuid in self.relations:
            self.relations[target_uuid].meta.clear()
            self.relations[target_uuid].meta.update(meta)
            self.logger.info(f"更新关系元数据: {target_uuid}")
            return True
        else:
            self.logger.warning(f"尝试更新不存在的关系元数据: {target_uuid}")
            return False
    
    def has_relation(self, target_uuid: str) -> bool:
        """
        检查是否存在指定关系
        
        Args:
            target_uuid: 目标Workable的UUID
            
        Returns:
            是否存在关系
        """
        return target_uuid in self.relations
    
    def get(self, target_uuid: str) -> Optional[Relation]:
        """
        获取指定目标的关系
        
        Args:
            target_uuid: 目标ID
            
        Returns:
            关系对象，如果不存在则返回None
        """
        return self.relations.get(target_uuid)
    
    def get_all(self) -> List[Relation]:
        """
        获取所有关系的副本
        
        Returns:
            关系列表
        """
        return list(self.relations.values())
    
    def get_related(self) -> List[str]:
        """
        获取所有相关Workable的UUID
        
        Returns:
            相关Workable UUID的列表
        """
        return list(self.relations.keys())
    
    def get_relation(self, target_uuid: str) -> Optional[Relation]:
        """
        获取指定关系（兼容旧API）
        
        Args:
            target_uuid: 目标Workable的UUID
            
        Returns:
            关系对象，如果不存在则返回None
        """
        return self.get(target_uuid)
    
    def get_related_by_meta(self, key: str, value: Any) -> Dict[str, Relation]:
        """
        根据元数据筛选关系
        
        Args:
            key: 元数据键
            value: 元数据值
            
        Returns:
            符合条件的关系字典
        """
        result = {}
        for uuid, relation in self.relations.items():
            if key in relation.meta and relation.meta[key] == value:
                result[uuid] = relation
        return result
    
    def clear(self) -> None:
        """清空所有关系"""
        self.relations.clear()
        self.logger.info("所有关系已清空")
    
    # 兼容旧版API
    clear_all = clear 