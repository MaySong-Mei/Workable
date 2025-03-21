import json
import logging
from typing import Dict, List, Optional, Type, Any

from workable.core.workable import Workable
from workable.core.exceptions import VisualizationError

class WorkableVisualizer:
    """
    Workable可视化工具
    提供树形结构和列表形式的可视化
    """
    
    def __init__(self, manager=None):
        """
        初始化可视化器
        
        Args:
            manager: 可选的WorkableManager实例，如果未提供则使用内部空管理器
        """
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        self.logger.debug("初始化WorkableVisualizer")
    
    def generate_tree(self, workable: Workable) -> Dict[str, Any]:
        """
        将Workable对象转换为树形结构的字典
        
        Args:
            workable: Workable对象
            
        Returns:
            树形结构的字典
        """
        try:
            result = {
                "name": workable.name,
                "uuid": workable.uuid,
                "type": "SimpleWorkable" if workable.is_atom() else "ComplexWorkable",
                "logic_description": workable.logic_description,
                "children": [],
                "locals": []
            }
            
            # 添加简单工作单元特有属性
            if workable.is_atom():
                result["content_type"] = workable.content_type
                
            # 处理复杂工作单元
            elif workable.is_complex():
                # 添加子Workable
                for child_uuid, child in workable.child_workables.items():
                    child_tree = self.generate_tree(child)
                    result["children"].append(child_tree)
            
            # 添加本地Workable (对所有类型)
            for local_uuid, local in workable.local_workables.items():
                local_tree = self.generate_tree(local)
                local_tree["is_local"] = True
                result["locals"].append(local_tree)
                    
            return result
        except Exception as e:
            self.logger.error(f"生成树形结构失败: {str(e)}")
            raise VisualizationError(f"生成树形结构失败: {str(e)}")
    
    def generate_workable_list(self, filter_type: Optional[Type[Workable]] = None) -> List[Dict]:
        """
        生成Workable列表
        
        Args:
            filter_type: 可选的Workable类型过滤器
            
        Returns:
            Workable信息列表
        """
        if not self.manager:
            raise VisualizationError("未设置WorkableManager")
        
        result = []
        
        if filter_type:
            workables = self.manager.get_workables_by_type(filter_type)
        else:
            workables = self.manager.get_all_workables()
        
        for uuid, workable in workables.items():
            item = {
                "uuid": uuid,
                "name": workable.name,
                "type": workable.__class__.__name__,
                "relations_count": len(workable.relation_manager.get_all())
            }
            result.append(item)
        
        return result
    
    def export_tree_to_json(self, workable: Workable, filepath: str) -> None:
        """
        将树结构导出为JSON文件
        
        Args:
            workable: Workable对象
            filepath: 输出文件路径
        """
        try:
            tree = self.generate_tree(workable)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tree, f, ensure_ascii=False, indent=2)
            self.logger.info(f"树形结构已导出到文件: {filepath}")
        except Exception as e:
            self.logger.error(f"导出树形结构失败: {str(e)}")
            raise VisualizationError(f"导出树形结构失败: {str(e)}")
    
    def export_workable_list_to_json(self, filter_type: Optional[Type[Workable]] = None) -> str:
        """
        将Workable列表导出为JSON
        
        Args:
            filter_type: 可选的Workable类型过滤器
            
        Returns:
            JSON字符串
            
        Raises:
            VisualizationError: 如果导出失败
        """
        workable_list = self.generate_workable_list(filter_type)
        try:
            return json.dumps(workable_list, indent=2)
        except Exception as e:
            raise VisualizationError(f"导出列表JSON失败: {e}")
    
    def generate_ascii_tree(self, workable: Workable) -> str:
        """
        生成ASCII格式的树
        
        Args:
            workable: Workable对象
            
        Returns:
            ASCII树字符串
        """
        try:
            lines = []
            self._generate_ascii_tree_recursive(workable, "", "", lines)
            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"生成ASCII树形图失败: {str(e)}")
            raise VisualizationError(f"生成ASCII树形图失败: {str(e)}")
    
    def _generate_ascii_tree_recursive(self, workable: Workable, prefix: str, 
                                     branch: str, lines: list) -> None:
        """
        递归生成ASCII树形图
        
        Args:
            workable: Workable对象
            prefix: 前缀
            branch: 分支字符
            lines: 结果行列表
        """
        # 确定工作单元类型
        workable_type = "SimpleWorkable" if workable.is_atom() else "ComplexWorkable"
        
        # 检查是否为本地工作单元
        is_local = hasattr(workable, 'is_local') and workable.is_local
        local_mark = " [LOCAL]" if is_local else ""
        
        # 添加当前节点
        lines.append(f"{prefix}{branch}{workable.name} ({workable_type}){local_mark}")
        
        # 计算子节点的前缀
        next_prefix = prefix + ("    " if branch == "└── " else "│   ")
        
        # 先处理本地工作单元
        if workable.local_workables:
            local_items = list(workable.local_workables.items())
            for i, (local_uuid, local) in enumerate(local_items):
                is_last_local = (i == len(local_items) - 1) and (not workable.is_complex() or not workable.child_workables)
                local_branch = "└── " if is_last_local else "├── "
                self._generate_ascii_tree_recursive(local, next_prefix, local_branch, lines)
        
        # 再处理子工作单元 (仅复杂工作单元)
        if workable.is_complex() and workable.child_workables:
            child_items = list(workable.child_workables.items())
            for i, (child_uuid, child) in enumerate(child_items):
                is_last_child = (i == len(child_items) - 1)
                child_branch = "└── " if is_last_child else "├── "
                self._generate_ascii_tree_recursive(child, next_prefix, child_branch, lines)
    
    def set_manager(self, manager) -> None:
        """
        设置WorkableManager
        
        Args:
            manager: WorkableManager实例
        """
        self.manager = manager
        self.logger.info("设置WorkableManager") 