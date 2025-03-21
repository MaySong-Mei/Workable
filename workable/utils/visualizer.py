"""
可视化工具 - 生成Workable结构的可视化表示
"""

import logging
import json
from typing import Dict, List, Optional, Union, Any, Type, TYPE_CHECKING, Set

from workable.core.exceptions import VisualizationError

# 避免循环导入
if TYPE_CHECKING:
    from workable.core.manager import WorkableManager
    from workable.core.workable import Workable

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

    def generate_tree(self, workable: 'Workable', max_depth: int = 10, 
                     depth: int = 0, visited: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        生成Workable的树状结构
        
        Args:
            workable: 要可视化的Workable
            max_depth: 最大深度
            depth: 当前深度
            visited: 已访问的Workable UUID集合
            
        Returns:
            树状结构的字典
        """
        if visited is None:
            visited = set()
            
        if workable.uuid in visited:
            return {"name": f"{workable.name} (循环引用)", "uuid": workable.uuid}
            
        visited.add(workable.uuid)
        
        if depth >= max_depth:
            return {"name": f"{workable.name} (达到最大深度)", "uuid": workable.uuid}
        
        result = {
            "name": workable.name,
            "uuid": workable.uuid,
            "description": workable.logic_description,
            "is_atom": workable.is_atom()
        }
        
        # 如果是简单Workable，添加内容信息
        if workable.is_atom():
            result["content_type"] = workable.content_type
            # 截断可能很长的内容
            content = workable.content_str or ""
            if len(content) > 100:
                content = content[:97] + "..."
            result["content"] = content
        else:
            # 添加子Workable
            children = []
            for child in workable.get_children():
                children.append(self.generate_tree(
                    child, max_depth, depth + 1, visited.copy()
                ))
            result["children"] = children
            
            # 添加本地Workable
            locals = []
            for local in workable.get_locals():
                local_info = {
                    "name": local.name,
                    "uuid": local.uuid,
                    "description": local.logic_description,
                    "content_type": local.content_type
                }
                # 截断可能很长的内容
                content = local.content_str or ""
                if len(content) > 100:
                    content = content[:97] + "..."
                local_info["content"] = content
                locals.append(local_info)
            result["locals"] = locals
            
        return result
    
    def export_tree_to_json(self, workable: 'Workable', max_depth: int = 10) -> Dict[str, Any]:
        """
        将Workable树导出为JSON对象
        
        Args:
            workable: 根Workable
            max_depth: 最大深度
            
        Returns:
            JSON对象
            
        Raises:
            VisualizationError: 如果导出失败
        """
        try:
            tree = self.generate_tree(workable, max_depth)
            return tree
        except Exception as e:
            error_msg = f"导出树到JSON失败: {str(e)}"
            self.logger.error(error_msg)
            raise VisualizationError(error_msg)
    
    def generate_ascii_tree(self, workable: 'Workable') -> str:
        """
        生成ASCII格式的树
        
        Args:
            workable: 根Workable
            
        Returns:
            ASCII树字符串
            
        Raises:
            VisualizationError: 如果生成失败
        """
        try:
            lines = []
            self._generate_ascii_tree_recursive(workable, "", True, lines)
            return "\n".join(lines)
        except Exception as e:
            error_msg = f"生成ASCII树失败: {str(e)}"
            self.logger.error(error_msg)
            raise VisualizationError(error_msg)
    
    def _generate_ascii_tree_recursive(self, workable: 'Workable', prefix: str, 
                                     is_last: bool, lines: List[str]) -> None:
        """
        递归生成ASCII树
        
        Args:
            workable: 当前Workable
            prefix: 当前行的前缀
            is_last: 是否是当前级别的最后一个节点
            lines: 输出行列表
        """
        # 添加当前节点
        type_str = "Simple" if workable.is_atom() else "Complex"
        node = f"{workable.name} [{type_str}] ({workable.uuid[:6]})"
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{node}")
        
        # 为子节点准备前缀
        new_prefix = f"{prefix}{'    ' if is_last else '│   '}"
        
        # 如果是复杂Workable，添加子节点和本地节点
        if not workable.is_atom():
            # 获取本地Workable
            locals = workable.get_locals()
            
            # 处理本地Workable
            if locals:
                local_prefix = f"{new_prefix}├── Locals:"
                lines.append(local_prefix)
                
                for i, local in enumerate(locals):
                    is_last_local = i == len(locals) - 1
                    local_node = f"{local.name} [Local] ({local.uuid[:6]})"
                    lines.append(f"{new_prefix}│   {'└── ' if is_last_local else '├── '}{local_node}")
            
            # 获取子Workable
            children = workable.get_children()
            
            # 处理子Workable
            if children:
                if locals:
                    lines.append(f"{new_prefix}└── Children:")
                    new_prefix = f"{new_prefix}    "
                else:
                    lines.append(f"{new_prefix}├── Children:")
                
                for i, child in enumerate(children):
                    is_last_child = i == len(children) - 1
                    self._generate_ascii_tree_recursive(child, new_prefix, is_last_child, lines)
    
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
        
        # 添加子Workable (仅复杂工作单元)
        if workable.is_complex():
            children.extend(list(workable.child_workables.keys()))
        
        # 添加本地Workable
        locals_list = list(workable.local_workables.keys())
        
        # 处理本地节点
        for i, local_uuid in enumerate(locals_list):
            local = workable.local_workables[local_uuid]
            local_info = self._format_node_info(local, show_details)
            
            is_last = (i == len(locals_list) - 1) and len(children) == 0
            
            if compact:
                new_prefix = prefix + (branch_styles["space"] if is_last else branch_styles["pipe"])
                new_branch = branch_styles["branch"]
            else:
                new_prefix = prefix + (branch_styles["space"] if is_last else branch_styles["pipe"])
                new_branch = branch_styles["last_branch"] if is_last else branch_styles["branch"]
                
            lines.append(f"{new_prefix}{new_branch}[LOCAL] {local_info}")
        
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
        
        # 处理本地Workable
        for local_uuid, local in workable.local_workables.items():
            local_info = self._format_node_info(local, show_details)
            lines.append(f"{indent_str}  [LOCAL] {local_info}")
        
        # 处理子Workable (仅复杂工作单元)
        if workable.is_complex():
            for child_uuid in workable.child_workables.keys():
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
        workable_type = "SimpleWorkable" if workable.is_atom() else "ComplexWorkable"
        
        if show_details:
            return f"{workable.name} ({workable_type}) [{workable.uuid[:6]}]"
        else:
            return f"{workable.name} [{workable.uuid[:6]}]" 