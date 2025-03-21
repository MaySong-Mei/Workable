"""
测试可视化工具
"""

import unittest
import logging
import json
from unittest.mock import patch, MagicMock, mock_open

from workable.visualizer import WorkableVisualizer
from workable.core.workable import Workable
from workable.core.models import WorkableFrame

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestWorkableVisualizer(unittest.TestCase):
    """测试WorkableVisualizer类"""
    
    def setUp(self):
        """每个测试前执行"""
        # 创建一些测试Workable
        self.atom1 = Workable(
            name="Atom 1",
            logic_description="Atomic workable 1",
            is_atom=True,
            content_str="Content 1",
            content_type="text"
        )
        
        self.atom2 = Workable(
            name="Atom 2",
            logic_description="Atomic workable 2",
            is_atom=True,
            content_str="Content 2",
            content_type="text"
        )
        
        self.composite1 = Workable(
            name="Composite 1",
            logic_description="Composite workable 1",
            is_atom=False
        )
        
        # 为composite1添加子Workable和本地Workable
        self.composite1.add_child(self.atom1)
        
        self.local1 = Workable(
            name="Local 1",
            logic_description="Local workable 1",
            is_atom=True,
            content_str="Local content 1"
        )
        self.composite1.add_local(self.local1)
        
        # 创建更复杂的结构
        self.composite2 = Workable(
            name="Composite 2",
            logic_description="Composite workable 2",
            is_atom=False
        )
        
        self.composite1.add_child(self.composite2)
        self.composite2.add_child(self.atom2)
        
        # 创建可视化器
        self.visualizer = WorkableVisualizer()
    
    def test_init(self):
        """测试初始化WorkableVisualizer"""
        self.assertIsNotNone(self.visualizer.logger)
    
    def test_generate_tree(self):
        """测试generate_tree方法"""
        # 生成树形结构
        tree = self.visualizer.generate_tree(self.composite1)
        
        # 验证树形结构
        self.assertEqual(tree["name"], "Composite 1")
        self.assertEqual(tree["type"], "ComplexWorkable")
        self.assertEqual(tree["uuid"], self.composite1.uuid)
        
        # 验证子节点
        self.assertEqual(len(tree["children"]), 2)
        
        # 验证子节点名称
        child_names = [child["name"] for child in tree["children"]]
        self.assertIn("Atom 1", child_names)
        self.assertIn("Composite 2", child_names)
        
        # 验证本地Workable
        local_workables = tree["locals"]
        self.assertEqual(len(local_workables), 1)
        self.assertEqual(local_workables[0]["name"], "Local 1")
        
        # 验证嵌套结构
        composite2_node = next(child for child in tree["children"] if child["name"] == "Composite 2")
        self.assertEqual(len(composite2_node["children"]), 1)
        self.assertEqual(composite2_node["children"][0]["name"], "Atom 2")
    
    def test_generate_tree_atom_workable(self):
        """测试generate_tree方法用于原子模式Workable"""
        # 生成树形结构
        tree = self.visualizer.generate_tree(self.atom1)
        
        # 验证树形结构
        self.assertEqual(tree["name"], "Atom 1")
        self.assertEqual(tree["type"], "SimpleWorkable")
        self.assertEqual(tree["uuid"], self.atom1.uuid)
        self.assertEqual(tree["content_type"], "text")
        self.assertEqual(tree["children"], [])
        self.assertEqual(tree["locals"], [])
    
    @patch("builtins.open", new_callable=mock_open)
    def test_export_tree_to_json(self, mock_file):
        """测试export_tree_to_json方法"""
        # 导出树形结构到JSON
        self.visualizer.export_tree_to_json(self.composite1, "test.json")
        
        # 验证文件操作
        mock_file.assert_called_once_with("test.json", "w", encoding="utf-8")
        
        # 验证写入的内容
        handle = mock_file()
        self.assertTrue(handle.write.call_count > 0)  # 确保write方法至少被调用一次
    
    def test_generate_ascii_tree(self):
        """测试generate_ascii_tree方法"""
        # 生成ASCII树
        ascii_tree = self.visualizer.generate_ascii_tree(self.composite1)
        
        # 验证ASCII树包含所有节点名称
        self.assertIn("Composite 1", ascii_tree)
        self.assertIn("Atom 1", ascii_tree)
        self.assertIn("Composite 2", ascii_tree)
        self.assertIn("Atom 2", ascii_tree)
        self.assertIn("Local 1", ascii_tree)
        
        # 验证树形结构层次
        lines = ascii_tree.strip().split("\n")
        self.assertTrue(any("Composite 1" in line for line in lines))  # 根节点
        
        # 验证[LOCAL]标记存在于本地工作单元
        self.assertTrue(any("[LOCAL]" in line and "Local 1" in line for line in lines))
    
    @patch("builtins.open", new_callable=mock_open)
    def test_export_ascii_tree_to_file(self, mock_file):
        """测试导出ASCII树到文件"""
        # 导出ASCII树到文件
        ascii_tree = self.visualizer.generate_ascii_tree(self.composite1)
        
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write(ascii_tree)
        
        # 验证文件操作
        mock_file.assert_called_once_with("test.txt", "w", encoding="utf-8")
        
        # 验证写入内容包含所有节点名称
        handle = mock_file()
        args, _ = handle.write.call_args
        written_content = args[0]
        
        self.assertIn("Composite 1", written_content)
        self.assertIn("Atom 1", written_content)
        self.assertIn("Composite 2", written_content)
        self.assertIn("Atom 2", written_content)
    
    def test_workable_state_in_tree(self):
        """测试工作单元状态在树中的表示"""
        # 执行状态转换
        original_atom = Workable(
            name="Original Atom",
            logic_description="Originally atomic workable",
            is_atom=True,
            content_str="Original content"
        )
        
        # 复制原始状态
        original_uuid = original_atom.uuid
        
        # 转换为复合模式
        original_atom.make_complex()
        
        # 添加到复合结构
        self.composite1.add_child(original_atom)
        
        # 生成树并验证
        tree = self.visualizer.generate_tree(self.composite1)
        
        # 查找转换后的节点
        converted_node = None
        for child in tree["children"]:
            if child["uuid"] == original_uuid:
                converted_node = child
                break
        
        self.assertIsNotNone(converted_node)
        self.assertEqual(converted_node["name"], "Original Atom")
        self.assertEqual(converted_node["type"], "ComplexWorkable")  # 应该显示为复合模式


if __name__ == "__main__":
    unittest.main() 