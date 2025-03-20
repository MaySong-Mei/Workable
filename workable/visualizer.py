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
    
    def generate_tree(self, root_uuid: str, max_depth: int = 3) -> Dict:
        """
        生成Workable树结构
        
        Args:
            root_uuid: 根Workable的UUID
            max_depth: 最大深度
            
        Returns:
            树形结构的字典
            
        Raises:
            VisualizationError: 如果根Workable不存在
        """
        if not self.manager:
            raise VisualizationError("未设置WorkableManager")
        
        root_workable = self.manager.get_workable(root_uuid)
        if not root_workable:
            raise VisualizationError(f"找不到根Workable: {root_uuid}")
        
        return self._build_tree_node(root_workable, max_depth, 0)
    
    def _build_tree_node(self, workable: Workable, max_depth: int, current_depth: int) -> Dict:
        """
        构建树节点
        
        Args:
            workable: 当前Workable
            max_depth: 最大深度
            current_depth: 当前深度
            
        Returns:
            节点字典
        """
        result = {
            "uuid": workable.uuid,
            "name": workable.name,
            "type": workable.__class__.__name__,
            "children": []
        }
        
        # 达到最大深度则停止
        if current_depth >= max_depth:
            return result
        
        # 添加关系子节点
        for relation in workable.relation_manager.get_all():
            child_uuid = relation.target_uuid
            child_workable = self.manager.get_workable(child_uuid)
            
            if child_workable:
                child_node = self._build_tree_node(
                    child_workable, max_depth, current_depth + 1
                )
                result["children"].append(child_node)
        
        return result
    
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
    
    def export_tree_to_json(self, root_uuid: str, max_depth: int = 3) -> str:
        """
        将树结构导出为JSON
        
        Args:
            root_uuid: 根Workable的UUID
            max_depth: 最大深度
            
        Returns:
            JSON字符串
            
        Raises:
            VisualizationError: 如果根Workable不存在
        """
        tree = self.generate_tree(root_uuid, max_depth)
        try:
            return json.dumps(tree, indent=2)
        except Exception as e:
            raise VisualizationError(f"导出树JSON失败: {e}")
    
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
    
    def generate_ascii_tree(self, root_uuid: str, max_depth: int = 3) -> str:
        """
        生成ASCII格式的树
        
        Args:
            root_uuid: 根Workable的UUID
            max_depth: 最大深度
            
        Returns:
            ASCII树字符串
            
        Raises:
            VisualizationError: 如果根Workable不存在
        """
        if not self.manager:
            raise VisualizationError("未设置WorkableManager")
        
        root_workable = self.manager.get_workable(root_uuid)
        if not root_workable:
            raise VisualizationError(f"找不到根Workable: {root_uuid}")
        
        lines = []
        self._build_ascii_tree(root_workable, "", True, max_depth, 0, lines)
        return "\n".join(lines)
    
    def _build_ascii_tree(self, workable: Workable, prefix: str, is_last: bool, 
                         max_depth: int, current_depth: int, lines: List[str]) -> None:
        """
        构建ASCII树节点
        
        Args:
            workable: 当前Workable
            prefix: 前缀字符串
            is_last: 是否是最后一个子节点
            max_depth: 最大深度
            current_depth: 当前深度
            lines: 输出行列表
        """
        if is_last:
            lines.append(f"{prefix}└── {workable.name} ({workable.__class__.__name__})")
            new_prefix = f"{prefix}    "
        else:
            lines.append(f"{prefix}├── {workable.name} ({workable.__class__.__name__})")
            new_prefix = f"{prefix}│   "
        
        # 达到最大深度则停止
        if current_depth >= max_depth:
            return
        
        # 添加关系子节点
        relations = workable.relation_manager.get_all()
        for i, relation in enumerate(relations):
            is_last_child = (i == len(relations) - 1)
            child_uuid = relation.target_uuid
            child_workable = self.manager.get_workable(child_uuid)
            
            if child_workable:
                self._build_ascii_tree(
                    child_workable, new_prefix, is_last_child, 
                    max_depth, current_depth + 1, lines
                )
            else:
                if is_last_child:
                    lines.append(f"{new_prefix}└── {child_uuid} (未找到)")
                else:
                    lines.append(f"{new_prefix}├── {child_uuid} (未找到)")
    
    def set_manager(self, manager) -> None:
        """
        设置WorkableManager
        
        Args:
            manager: WorkableManager实例
        """
        self.manager = manager
        self.logger.info("设置WorkableManager") 