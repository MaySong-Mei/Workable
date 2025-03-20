"""
可视化工具 - 生成Workable结构的可视化表示
"""

import logging
import json
from typing import Dict, List, Optional, Union, Any, Type, TYPE_CHECKING

from workable.core.exceptions import VisualizationError

# 避免循环导入
if TYPE_CHECKING:
    from workable.core.manager import WorkableManager
    from workable.core.workable import Workable, SimpleWorkable, ComplexWorkable

class WorkableVisualizer:
    """负责生成各种Workable可视化格式的工具类"""
    
    def __init__(self, manager: Optional['WorkableManager'] = None):
        """
        初始化可视化工具
        
        Args:
            manager: Workable管理器实例，可选
        """
        self.manager = manager
        self.logger = logging.getLogger("workable_visualizer")
    
    def as_tree(self, root_uuid: str = None, show_details: bool = False,
              max_depth: int = -1, compact: bool = False) -> str:
        """
        以树状格式展示Workable结构，需要manager
        
        Args:
            root_uuid: 根节点UUID，如果为None则选择第一个根节点
            show_details: 是否显示详细信息
            max_depth: 最大深度，-1表示不限制
            compact: 是否使用紧凑格式
            
        Returns:
            树状图字符串
        """
        if not self.manager:
            raise VisualizationError("需要管理器实例才能使用as_tree方法")
            
        try:
            parent_map = self._build_parent_map()
            
            # 获取根节点
            if not root_uuid:
                roots = self.manager.get_all_roots()
                if not roots:
                    return "空的Workable树"
                root_uuid = roots[0]
            
            # 检查根节点存在
            if root_uuid not in self.manager.workables:
                return f"根节点 {root_uuid} 不存在"
            
            # 生成树状图
            lines = []
            self._visualize_node(root_uuid, "", "", lines, show_details, 
                                parent_map, max_depth, 0, compact)
            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"生成树状图失败: {str(e)}")
            raise VisualizationError(f"生成树状图失败: {str(e)}")
    
    def as_ascii_tree(self, root_uuid: str = None, show_details: bool = False,
                     max_depth: int = -1) -> str:
        """
        生成紧凑的ASCII树形图，需要manager
        
        Args:
            root_uuid: 根节点UUID，如果为None则选择第一个根节点
            show_details: 是否显示详细信息
            max_depth: 最大深度，-1表示不限制
            
        Returns:
            ASCII树形图字符串
        """
        return self.as_tree(root_uuid, show_details, max_depth, compact=True)
    
    def as_list(self, root_uuid: str = None, indent: bool = True,
               show_details: bool = False) -> str:
        """
        以缩进列表形式显示Workable结构，需要manager
        
        Args:
            root_uuid: 根节点UUID，如果为None则选择第一个根节点
            indent: 是否缩进
            show_details: 是否显示详细信息
            
        Returns:
            缩进列表字符串
        """
        if not self.manager:
            raise VisualizationError("需要管理器实例才能使用as_list方法")
            
        try:
            parent_map = self._build_parent_map()
            
            # 获取根节点
            if not root_uuid:
                roots = self.manager.get_all_roots()
                if not roots:
                    return "空的Workable列表"
                root_uuid = roots[0]
            
            # 检查根节点存在
            if root_uuid not in self.manager.workables:
                return f"根节点 {root_uuid} 不存在"
            
            # 生成列表
            lines = []
            self._list_node(root_uuid, 0, lines, show_details, parent_map, indent)
            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"生成列表失败: {str(e)}")
            raise VisualizationError(f"生成列表失败: {str(e)}")
    
    def log_visualization(self, format_type: str = "tree", root_uuid: str = None,
                         show_details: bool = True, log_level: str = "INFO") -> None:
        """
        生成可视化并记录到日志，需要manager
        
        Args:
            format_type: 可视化格式类型（"tree", "ascii", "list"）
            root_uuid: 根节点UUID，如果为None则选择第一个根节点
            show_details: 是否显示详细信息
            log_level: 日志级别
        """
        if not self.manager:
            raise VisualizationError("需要管理器实例才能使用log_visualization方法")
            
        format_map = {
            "tree": self.as_tree,
            "ascii": self.as_ascii_tree,
            "list": self.as_list
        }
        
        if format_type not in format_map:
            self.logger.warning(f"未知的可视化格式: {format_type}")
            format_type = "tree"
        
        viz_str = format_map[format_type](root_uuid=root_uuid, show_details=show_details)
        
        log_method = getattr(self.logger, log_level.lower())
        
        # 获取根节点信息
        root_info = "Root"
        if root_uuid and root_uuid in self.manager.workables:
            root = self.manager.workables[root_uuid]
            root_info = f"{root.name} ({root_uuid[:6]})"
        
        log_method(f"Workable结构 - {root_info} - 格式: {format_type}\n{viz_str}")
    
    # 新方法：直接使用Workable对象

    def generate_tree(self, workable: 'Workable') -> Dict[str, Any]:
        """
        将Workable对象转换为树形结构的字典
        
        Args:
            workable: Workable对象
            
        Returns:
            树形结构的字典
        """
        try:
            from workable.core.workable import SimpleWorkable, ComplexWorkable
            
            result = {
                "name": workable.name,
                "uuid": workable.uuid,
                "type": workable.__class__.__name__,
                "logic_description": workable.logic_description,
                "children": [],
                "locals": []
            }
            
            # 处理SimpleWorkable特有属性
            if isinstance(workable, SimpleWorkable):
                result["content_type"] = workable.content_type
                
            # 处理ComplexWorkable
            elif isinstance(workable, ComplexWorkable):
                # 添加子Workable
                for child_uuid, child in workable.child_workables.items():
                    child_tree = self.generate_tree(child)
                    result["children"].append(child_tree)
                
                # 添加本地Workable
                for local_uuid, local in workable.content.workables.items():
                    local_tree = self.generate_tree(local)
                    result["locals"].append(local_tree)
                    
            return result
        except Exception as e:
            self.logger.error(f"生成树形结构失败: {str(e)}")
            raise VisualizationError(f"生成树形结构失败: {str(e)}")
    
    def export_tree_to_json(self, workable: 'Workable', filepath: str) -> None:
        """
        将Workable树结构导出为JSON文件
        
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
    
    def generate_ascii_tree(self, workable: 'Workable') -> str:
        """
        生成Workable的ASCII树形图
        
        Args:
            workable: Workable对象
            
        Returns:
            ASCII树形图字符串
        """
        try:
            lines = []
            self._generate_ascii_tree_recursive(workable, "", "", lines)
            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"生成ASCII树形图失败: {str(e)}")
            raise VisualizationError(f"生成ASCII树形图失败: {str(e)}")
    
    def _generate_ascii_tree_recursive(self, workable: 'Workable', prefix: str, 
                                     branch: str, lines: list) -> None:
        """
        递归生成ASCII树形图
        
        Args:
            workable: Workable对象
            prefix: 前缀
            branch: 分支字符
            lines: 结果行列表
        """
        from workable.core.workable import SimpleWorkable, ComplexWorkable
        
        # 节点信息
        node_info = workable.name
        
        # 显示节点类型
        type_info = workable.__class__.__name__
        lines.append(f"{prefix}{branch}{node_info} ({type_info})")
        
        if isinstance(workable, ComplexWorkable):
            # 显示本地Workable
            local_count = len(workable.content.workables)
            for i, (local_uuid, local) in enumerate(workable.content.workables.items()):
                is_last = (i == local_count - 1) and (len(workable.child_workables) == 0)
                new_prefix = prefix + ("    " if is_last else "│   ")
                new_branch = "└── " if is_last else "├── "
                local_info = f"{local.name} ({local.__class__.__name__}) [LOCAL]"
                lines.append(f"{prefix}{new_branch}{local_info}")
            
            # 显示子Workable
            child_count = len(workable.child_workables)
            for i, (child_uuid, child) in enumerate(workable.child_workables.items()):
                is_last = i == child_count - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                new_branch = "└── " if is_last else "├── "
                self._generate_ascii_tree_recursive(child, new_prefix, new_branch, lines)
    
    def export_ascii_tree_to_file(self, workable: 'Workable', filepath: str) -> None:
        """
        将ASCII树形图导出到文件
        
        Args:
            workable: Workable对象
            filepath: 输出文件路径
        """
        try:
            ascii_tree = self.generate_ascii_tree(workable)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(ascii_tree)
            self.logger.info(f"ASCII树形图已导出到文件: {filepath}")
        except Exception as e:
            self.logger.error(f"导出ASCII树形图失败: {str(e)}")
            raise VisualizationError(f"导出ASCII树形图失败: {str(e)}")
    
    def generate_workable_list(self, workable: 'Workable') -> List[Dict[str, Any]]:
        """
        生成Workable的扁平列表
        
        Args:
            workable: Workable对象
            
        Returns:
            Workable信息的扁平列表
        """
        try:
            from workable.core.workable import ComplexWorkable
            
            result = []
            self._collect_workables_recursive(workable, result)
            return result
        except Exception as e:
            self.logger.error(f"生成Workable列表失败: {str(e)}")
            raise VisualizationError(f"生成Workable列表失败: {str(e)}")
    
    def _collect_workables_recursive(self, workable: 'Workable', 
                                   result: List[Dict[str, Any]]) -> None:
        """
        递归收集所有Workable
        
        Args:
            workable: Workable对象
            result: 结果列表
        """
        from workable.core.workable import ComplexWorkable
        
        # 添加当前Workable
        result.append({
            "name": workable.name,
            "uuid": workable.uuid,
            "type": workable.__class__.__name__,
            "logic_description": workable.logic_description
        })
        
        # 处理复杂Workable
        if isinstance(workable, ComplexWorkable):
            # 添加本地Workable
            for local_uuid, local in workable.content.workables.items():
                result.append({
                    "name": local.name,
                    "uuid": local.uuid,
                    "type": local.__class__.__name__,
                    "logic_description": local.logic_description,
                    "is_local": True,
                    "parent_uuid": workable.uuid
                })
            
            # 递归处理子Workable
            for child_uuid, child in workable.child_workables.items():
                self._collect_workables_recursive(child, result)
    
    def export_workable_list_to_json(self, workable: 'Workable', filepath: str) -> None:
        """
        将Workable列表导出为JSON文件
        
        Args:
            workable: Workable对象
            filepath: 输出文件路径
        """
        try:
            workable_list = self.generate_workable_list(workable)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workable_list, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Workable列表已导出到文件: {filepath}")
        except Exception as e:
            self.logger.error(f"导出Workable列表失败: {str(e)}")
            raise VisualizationError(f"导出Workable列表失败: {str(e)}")
    
    def _build_parent_map(self) -> Dict[str, str]:
        """
        构建子节点到父节点的映射
        
        Returns:
            子节点UUID到父节点UUID的映射字典
        """
        if not self.manager:
            return {}
        return self.manager.build_parent_map()
    
    def _visualize_node(self, node_uuid: str, prefix: str, branch: str, 
                       lines: list, show_details: bool, parent_map: Dict[str, str],
                       max_depth: int, current_depth: int, compact: bool) -> None:
        """
        递归生成节点的树形可视化
        
        Args:
            node_uuid: 节点UUID
            prefix: 前缀字符串
            branch: 分支字符串
            lines: 结果行列表
            show_details: 是否显示详细信息
            parent_map: 子节点到父节点的映射
            max_depth: 最大深度
            current_depth: 当前深度
            compact: 是否使用紧凑格式
        """
        # 检查深度限制
        if max_depth >= 0 and current_depth > max_depth:
            if lines and lines[-1].endswith("..."):
                return
            lines.append(f"{prefix}{branch}...")
            return
        
        workable = self.manager.workables.get(node_uuid)
        if not workable:
            return
        
        # 获取节点信息
        node_info = self._format_node_info(workable, show_details)
        
        # 使用不同风格的分支符号
        if compact:
            branch_styles = {
                "branch": "+--", 
                "pipe": "|  ", 
                "space": "   "
            }
        else:
            branch_styles = {
                "branch": "├── ", 
                "pipe": "│   ", 
                "last_branch": "└── ", 
                "space": "    "
            }
        
        lines.append(f"{prefix}{branch}[{node_info}]")
        
        # 处理子节点
        children = []
        
        # 添加β-workables (外部引用)
        if hasattr(workable, 'child_workables'):
            children.extend(list(workable.child_workables.keys()))
        
        # 添加γ-workables (本地workable)
        if hasattr(workable, 'content') and hasattr(workable.content, 'workables'):
            children.extend(list(workable.content.workables.keys()))
        
        # 显示子节点
        child_count = len(children)
        for i, child_uuid in enumerate(children):
            is_last = i == child_count - 1
            
            if compact:
                new_prefix = prefix + (branch_styles["space"] if is_last else branch_styles["pipe"])
                new_branch = branch_styles["branch"]
            else:
                new_prefix = prefix + (branch_styles["space"] if is_last else branch_styles["pipe"])
                new_branch = branch_styles["last_branch"] if is_last else branch_styles["branch"]
            
            self._visualize_node(
                child_uuid, new_prefix, new_branch, lines, show_details, 
                parent_map, max_depth, current_depth + 1, compact
            )
    
    def _list_node(self, node_uuid: str, level: int, lines: list, 
                  show_details: bool, parent_map: Dict[str, str], indent: bool) -> None:
        """
        递归生成节点的列表可视化
        
        Args:
            node_uuid: 节点UUID
            level: 层级
            lines: 结果行列表
            show_details: 是否显示详细信息
            parent_map: 子节点到父节点的映射
            indent: 是否缩进
        """
        workable = self.manager.workables.get(node_uuid)
        if not workable:
            return
        
        # 获取节点信息
        node_info = self._format_node_info(workable, show_details)
        
        # 添加缩进
        indent_str = "  " * level if indent else ""
        lines.append(f"{indent_str}[{node_info}]")
        
        # 处理子节点
        children = []
        
        # 添加β-workables (外部引用)
        if hasattr(workable, 'child_workables'):
            children.extend(list(workable.child_workables.keys()))
        
        # 添加γ-workables (本地workable)
        if hasattr(workable, 'content') and hasattr(workable.content, 'workables'):
            local_ids = list(workable.content.workables.keys())
            for local_id in local_ids:
                local = workable.content.workables[local_id]
                # 显示是本地workable
                local_info = self._format_node_info(local, show_details)
                lines.append(f"{indent_str}  [LOCAL] {local_info}")
        
        # 显示子节点
        for child_uuid in children:
            self._list_node(child_uuid, level + 1, lines, show_details, parent_map, indent)
    
    def _format_node_info(self, workable: 'Workable', show_details: bool) -> str:
        """
        格式化节点信息
        
        Args:
            workable: Workable对象
            show_details: 是否显示详细信息
            
        Returns:
            格式化的节点信息字符串
        """
        if show_details:
            return f"{workable.name} ({workable.__class__.__name__}) [{workable.uuid[:6]}]"
        else:
            return f"{workable.name} [{workable.uuid[:6]}]" 