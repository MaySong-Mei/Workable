"""
测试统一Workable类
"""

import unittest
import uuid
import logging
from unittest.mock import patch

from workable.core.workable import Workable
from workable.core.models import WorkableFrame
from workable.core.exceptions import WorkableError, ConversionError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestWorkable(unittest.TestCase):
    """
    测试统一Workable类
    """
    
    def setUp(self):
        """每个测试前执行"""
        # 原子模式Workable
        self.atom_workable = Workable(
            name="Test Atom Workable",
            logic_description="Test atomic workable",
            is_atom=True,
            content_str="Test content",
            content_type="text"
        )
        
        # 复合模式Workable
        self.complex_workable = Workable(
            name="Test Complex Workable",
            logic_description="Test complex workable",
            is_atom=False
        )
        
        # 用于添加的子Workable
        self.child_workable = Workable(
            name="Child Workable",
            logic_description="Child workable for testing",
            is_atom=True,
            content_str="Child content"
        )
        
        # 用于添加的本地Workable
        self.local_workable = Workable(
            name="Local Workable",
            logic_description="Local workable for testing",
            is_atom=True,
            content_str="Local content"
        )
    
    def test_init_atom(self):
        """测试初始化原子模式Workable"""
        self.assertTrue(self.atom_workable.is_atom())
        self.assertTrue(self.atom_workable.is_simple())
        self.assertFalse(self.atom_workable.is_complex())
        self.assertEqual(self.atom_workable.name, "Test Atom Workable")
        self.assertEqual(self.atom_workable.logic_description, "Test atomic workable")
        self.assertEqual(self.atom_workable.content_str, "Test content")
        self.assertEqual(self.atom_workable.content_type, "text")
        self.assertIsNotNone(self.atom_workable.uuid)
    
    def test_init_composite(self):
        """测试初始化复合模式Workable"""
        self.assertFalse(self.complex_workable.is_atom())
        self.assertFalse(self.complex_workable.is_simple())
        self.assertTrue(self.complex_workable.is_complex())
        self.assertEqual(self.complex_workable.name, "Test Complex Workable")
        self.assertEqual(self.complex_workable.logic_description, "Test complex workable")
        self.assertIsNotNone(self.complex_workable.uuid)
        self.assertEqual(len(self.complex_workable.child_workables), 0)
        self.assertEqual(len(self.complex_workable.local_workables), 0)
        
        # 验证复合模式下不能直接访问内容
        with self.assertRaises(AttributeError):
            _ = self.complex_workable.content_str
        with self.assertRaises(AttributeError):
            _ = self.complex_workable.content_type
    
    def test_update(self):
        """测试update方法"""
        self.atom_workable.update(name="Updated Name", logic_description="Updated description")
        self.assertEqual(self.atom_workable.name, "Updated Name")
        self.assertEqual(self.atom_workable.logic_description, "Updated description")
        
        # 仅更新名称
        self.atom_workable.update(name="Only Name Updated")
        self.assertEqual(self.atom_workable.name, "Only Name Updated")
        self.assertEqual(self.atom_workable.logic_description, "Updated description")
        
        # 仅更新描述
        self.atom_workable.update(logic_description="Only Description Updated")
        self.assertEqual(self.atom_workable.name, "Only Name Updated")
        self.assertEqual(self.atom_workable.logic_description, "Only Description Updated")
    
    def test_update_content_atom(self):
        """测试原子模式下的update_content方法"""
        # 更新内容
        self.atom_workable.update_content("Updated content")
        self.assertEqual(self.atom_workable.content_str, "Updated content")
        
        # 复合模式下不能更新内容
        with self.assertRaises(AttributeError):
            self.complex_workable.update_content("Cannot update complex content")
    
    def test_add_child(self):
        """测试add_child方法"""
        # 复合模式可以添加子Workable
        self.complex_workable.add_child(self.child_workable)
        self.assertEqual(len(self.complex_workable.child_workables), 1)
        self.assertIn(self.child_workable.uuid, self.complex_workable.child_workables)
        
        # 原子模式不能添加子Workable
        with self.assertRaises(AttributeError):
            self.atom_workable.add_child(self.child_workable)
        
        # 添加非Workable对象应该失败
        with self.assertRaises(WorkableError):
            self.complex_workable.add_child("not a workable")
    
    def test_remove_child(self):
        """测试remove_child方法"""
        # 添加并移除子Workable
        self.complex_workable.add_child(self.child_workable)
        self.assertEqual(len(self.complex_workable.child_workables), 1)
        
        result = self.complex_workable.remove_child(self.child_workable.uuid)
        self.assertTrue(result)
        self.assertEqual(len(self.complex_workable.child_workables), 0)
        
        # 移除不存在的子Workable
        result = self.complex_workable.remove_child(str(uuid.uuid4()))
        self.assertFalse(result)
        
        # 原子模式不能移除子Workable
        with self.assertRaises(AttributeError):
            self.atom_workable.remove_child(self.child_workable.uuid)
    
    def test_get_all_children(self):
        """测试get_all_children方法"""
        # 添加子Workable
        self.complex_workable.add_child(self.child_workable)
        
        # 获取所有子Workable
        children = self.complex_workable.get_all_children()
        self.assertEqual(len(children), 1)
        self.assertIn(self.child_workable.uuid, children)
        
        # 原子模式不能获取子Workable
        with self.assertRaises(AttributeError):
            self.atom_workable.get_all_children()
    
    def test_add_local(self):
        """测试add_local方法"""
        # 添加本地Workable
        self.complex_workable.add_local(self.local_workable)
        self.assertEqual(len(self.complex_workable.local_workables), 1)
        self.assertIn(self.local_workable.uuid, self.complex_workable.local_workables)
        
        # 原子模式也可以添加本地Workable
        self.atom_workable.add_local(self.local_workable)
        self.assertEqual(len(self.atom_workable.local_workables), 1)
        self.assertIn(self.local_workable.uuid, self.atom_workable.local_workables)
        
        # 添加非Workable对象应该失败
        with self.assertRaises(AttributeError):
            self.complex_workable.add_local("not a workable")
    
    def test_remove_local(self):
        """测试remove_local方法"""
        # 添加并移除本地Workable
        self.complex_workable.add_local(self.local_workable)
        self.assertEqual(len(self.complex_workable.local_workables), 1)
        
        result = self.complex_workable.remove_local(self.local_workable.uuid)
        self.assertTrue(result)
        self.assertEqual(len(self.complex_workable.local_workables), 0)
        
        # 移除不存在的本地Workable
        result = self.complex_workable.remove_local(str(uuid.uuid4()))
        self.assertFalse(result)
    
    def test_get_all_locals(self):
        """测试get_all_locals方法"""
        # 添加本地Workable
        self.complex_workable.add_local(self.local_workable)
        
        # 获取所有本地Workable
        locals_dict = self.complex_workable.get_all_locals()
        self.assertEqual(len(locals_dict), 1)
        self.assertIn(self.local_workable.uuid, locals_dict)
    
    def test_to_frame(self):
        """测试to_frame方法"""
        frame = self.atom_workable.to_frame()
        self.assertIsInstance(frame, WorkableFrame)
        self.assertEqual(frame.name, self.atom_workable.name)
        self.assertEqual(frame.logic_description, self.atom_workable.logic_description)
        self.assertEqual(frame.lnref, self.atom_workable.uuid)
    
    def test_make_complex(self):
        """测试make_complex方法 - 将原子模式转换为复合模式"""
        # 转换前检查
        self.assertTrue(self.atom_workable.is_atom())
        original_content = self.atom_workable.content_str
        original_content_type = self.atom_workable.content_type
        original_uuid = self.atom_workable.uuid
        
        # 执行转换
        converted = self.atom_workable.make_complex()
        self.assertIs(converted, self.atom_workable)  # 返回self
        
        # 转换后检查
        self.assertFalse(self.atom_workable.is_atom())
        self.assertTrue(self.atom_workable.is_complex())
        self.assertEqual(self.atom_workable.uuid, original_uuid)  # UUID不变
        
        # 内容应该转移到本地Workable
        self.assertEqual(len(self.atom_workable.local_workables), 1)
        local_uuid = next(iter(self.atom_workable.local_workables.keys()))
        local_workable = self.atom_workable.local_workables[local_uuid]
        self.assertEqual(local_workable.content_str, original_content)
        self.assertEqual(local_workable.content_type, original_content_type)
    
    def test_make_simple(self):
        """测试make_simple方法 - 将复合模式转换为原子模式"""
        # 创建一个包含单个本地Workable的复合Workable
        complex_w = Workable(name="Complex for conversion", 
                            logic_description="Test conversion", 
                            is_atom=False)
        
        local_w = Workable(name="Local content", 
                          logic_description="Local content",
                          is_atom=True,
                          content_str="Local content for conversion",
                          content_type="text")
        
        complex_w.add_local(local_w)
        original_uuid = complex_w.uuid
        
        # 执行转换
        converted = complex_w.make_simple()
        self.assertIs(converted, complex_w)  # 返回self
        
        # 转换后检查
        self.assertTrue(complex_w.is_atom())
        self.assertFalse(complex_w.is_complex())
        self.assertEqual(complex_w.uuid, original_uuid)  # UUID不变
        
        # 内容应该从本地Workable转移
        self.assertEqual(complex_w.content_str, "Local content for conversion")
        self.assertEqual(complex_w.content_type, "text")
        self.assertEqual(len(complex_w.local_workables), 0)  # 本地Workable应该被移除
    
    def test_state_preservation_after_conversion(self):
        """测试转换前后状态的保存"""
        # 原始状态
        original_name = "Original"
        original_desc = "Original description"
        original_content = "Original content"
        
        # 创建一个原子模式Workable
        workable = Workable(
            name=original_name,
            logic_description=original_desc,
            is_atom=True,
            content_str=original_content
        )
        
        # 转换为复合模式
        workable.make_complex()
        
        # 基本属性应该保持不变
        self.assertEqual(workable.name, original_name)
        self.assertEqual(workable.logic_description, original_desc)
        
        # 检查是否只有一个本地Workable (包含了原始内容)
        self.assertEqual(len(workable.local_workables), 1)
        
        # 转换回原子模式
        workable.make_simple()
        
        # 检查所有属性
        self.assertEqual(workable.name, original_name)
        self.assertEqual(workable.logic_description, original_desc)
        self.assertEqual(workable.content_str, original_content)
        

if __name__ == '__main__':
    unittest.main() 