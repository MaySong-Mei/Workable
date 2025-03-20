"""
测试Workable核心类
"""

import unittest
import logging
import uuid
from unittest.mock import patch, MagicMock

from workable.core.workable import (
    Workable, SimpleWorkable, ComplexWorkable,
    convert_simple_to_complex, convert_complex_to_simple
)
from workable.core.models import WorkableFrame, Message, Relation
from workable.core.exceptions import WorkableError, ConversionError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestSimpleWorkable(unittest.TestCase):
    """测试SimpleWorkable类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.simple = SimpleWorkable(
            name="Test Simple",
            logic_description="Test simple workable",
            content_str="Test content",
            content_type="text"
        )
    
    def test_init(self):
        """测试初始化SimpleWorkable"""
        self.assertEqual(self.simple.name, "Test Simple")
        self.assertEqual(self.simple.logic_description, "Test simple workable")
        self.assertEqual(self.simple.content_str, "Test content")
        self.assertEqual(self.simple.content_type, "text")
        self.assertIsNotNone(self.simple.uuid)
        self.assertTrue(isinstance(self.simple.uuid, str))
    
    def test_to_frame(self):
        """测试to_frame方法"""
        frame = self.simple.to_frame()
        
        self.assertEqual(frame.name, "Test Simple")
        self.assertEqual(frame.logic_description, "Test simple workable")
        self.assertEqual(frame.lnref, self.simple.uuid)
        self.assertIsNone(frame.exref)
    
    def test_update(self):
        """测试update方法"""
        self.simple.update(name="New Name", logic_description="New description")
        
        self.assertEqual(self.simple.name, "New Name")
        self.assertEqual(self.simple.logic_description, "New description")
    
    def test_update_content(self):
        """测试update_content方法"""
        self.simple.update_content("Updated content")
        
        self.assertEqual(self.simple.content_str, "Updated content")
    
    def test_is_atom(self):
        """测试is_atom方法"""
        self.assertTrue(self.simple.is_atom())


class TestComplexWorkable(unittest.TestCase):
    """测试ComplexWorkable类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.complex = ComplexWorkable(
            name="Test Complex",
            logic_description="Test complex workable"
        )
        
        # 创建一些子Workable
        self.child1 = SimpleWorkable(
            name="Child 1",
            logic_description="Child workable 1",
            content_str="Child content 1"
        )
        
        self.child2 = ComplexWorkable(
            name="Child 2",
            logic_description="Child workable 2"
        )
        
        # 创建一些本地Workable
        self.local1 = SimpleWorkable(
            name="Local 1",
            logic_description="Local workable 1",
            content_str="Local content 1"
        )
        
        self.local2 = SimpleWorkable(
            name="Local 2",
            logic_description="Local workable 2",
            content_str="Local content 2"
        )
    
    def test_init(self):
        """测试初始化ComplexWorkable"""
        self.assertEqual(self.complex.name, "Test Complex")
        self.assertEqual(self.complex.logic_description, "Test complex workable")
        self.assertIsNotNone(self.complex.uuid)
        self.assertTrue(isinstance(self.complex.uuid, str))
        self.assertEqual(len(self.complex.child_workables), 0)
        self.assertEqual(len(self.complex.content.workables), 0)
    
    def test_add_child(self):
        """测试add_child方法"""
        self.complex.add_child(self.child1)
        
        self.assertEqual(len(self.complex.child_workables), 1)
        self.assertEqual(len(self.complex.content.frames), 1)
        
        # 验证Frame
        frame = self.complex.content.frames[0]
        self.assertEqual(frame.name, "Child 1")
        self.assertEqual(frame.exref, self.child1.uuid)
        self.assertIsNone(frame.lnref)
        
        # 添加无效的子Workable
        with self.assertRaises(WorkableError):
            self.complex.add_child("not a workable")
    
    def test_add_local(self):
        """测试add_local方法"""
        self.complex.add_local(self.local1)
        
        self.assertEqual(len(self.complex.content.workables), 1)
        self.assertEqual(len(self.complex.content.frames), 1)
        
        # 验证Frame
        frame = self.complex.content.frames[0]
        self.assertEqual(frame.name, "Local 1")
        self.assertEqual(frame.lnref, self.local1.uuid)
        self.assertIsNone(frame.exref)
        
        # 添加无效的本地Workable
        with self.assertRaises(WorkableError):
            self.complex.add_local(self.child2)  # ComplexWorkable不能作为本地Workable
    
    def test_remove_child(self):
        """测试remove_child方法"""
        # 添加子Workable
        self.complex.add_child(self.child1)
        self.complex.add_child(self.child2)
        
        self.assertEqual(len(self.complex.child_workables), 2)
        self.assertEqual(len(self.complex.content.frames), 2)
        
        # 移除子Workable
        result = self.complex.remove_child(self.child1.uuid)
        
        self.assertTrue(result)
        self.assertEqual(len(self.complex.child_workables), 1)
        self.assertEqual(len(self.complex.content.frames), 1)
        
        # 验证剩余Frame
        frame = self.complex.content.frames[0]
        self.assertEqual(frame.name, "Child 2")
        
        # 移除不存在的子Workable
        result = self.complex.remove_child("non-existent-uuid")
        self.assertFalse(result)
    
    def test_remove_local(self):
        """测试remove_local方法"""
        # 添加本地Workable
        self.complex.add_local(self.local1)
        self.complex.add_local(self.local2)
        
        self.assertEqual(len(self.complex.content.workables), 2)
        self.assertEqual(len(self.complex.content.frames), 2)
        
        # 移除本地Workable
        result = self.complex.remove_local(self.local1.uuid)
        
        self.assertTrue(result)
        self.assertEqual(len(self.complex.content.workables), 1)
        self.assertEqual(len(self.complex.content.frames), 1)
        
        # 验证剩余Frame
        frame = self.complex.content.frames[0]
        self.assertEqual(frame.name, "Local 2")
    
    def test_is_atom(self):
        """测试is_atom方法"""
        self.assertFalse(self.complex.is_atom())
    
    def test_get_all_children(self):
        """测试get_all_children方法"""
        # 添加子Workable
        self.complex.add_child(self.child1)
        self.complex.add_child(self.child2)
        
        children = self.complex.get_all_children()
        
        self.assertEqual(len(children), 2)
        self.assertIn(self.child1.uuid, children)
        self.assertIn(self.child2.uuid, children)
        
        # 验证是否为副本
        children[self.child1.uuid] = None
        self.assertEqual(len(self.complex.child_workables), 2)
    
    def test_get_all_locals(self):
        """测试get_all_locals方法"""
        # 添加本地Workable
        self.complex.add_local(self.local1)
        self.complex.add_local(self.local2)
        
        locals_dict = self.complex.get_all_locals()
        
        self.assertEqual(len(locals_dict), 2)
        self.assertIn(self.local1.uuid, locals_dict)
        self.assertIn(self.local2.uuid, locals_dict)
        
        # 验证是否为副本
        locals_dict[self.local1.uuid] = None
        self.assertEqual(len(self.complex.content.workables), 2)


class TestConversionFunctions(unittest.TestCase):
    """测试转换函数"""
    
    def setUp(self):
        """每个测试前执行"""
        self.simple = SimpleWorkable(
            name="Test Simple",
            logic_description="Test simple workable",
            content_str="Test content",
            content_type="text"
        )
        
        self.complex = ComplexWorkable(
            name="Test Complex",
            logic_description="Test complex workable"
        )
        
        # 为complex添加一个本地Workable
        self.local = SimpleWorkable(
            name="Local",
            logic_description="Local workable",
            content_str="Local content"
        )
        self.complex.add_local(self.local)
        
        # 添加一些消息和关系
        self.message = Message(
            content="Test message",
            sender="sender-uuid",
            receiver=self.simple.uuid
        )
        self.simple.message_manager.append(self.message)
        
        self.relation = Relation(target_uuid="target-uuid")
        self.simple.relation_manager.add(self.relation)
    
    def test_convert_simple_to_complex(self):
        """测试convert_simple_to_complex函数"""
        complex_work = convert_simple_to_complex(self.simple)
        
        # 验证基本属性
        self.assertEqual(complex_work.name, "Test Simple")
        self.assertEqual(complex_work.logic_description, "Test simple workable")
        self.assertTrue(isinstance(complex_work, ComplexWorkable))
        
        # 验证本地Workable
        self.assertEqual(len(complex_work.content.workables), 1)
        
        local_uuid = next(iter(complex_work.content.workables.keys()))
        local_work = complex_work.content.workables[local_uuid]
        
        self.assertEqual(local_work.name, "Test Simple_content")
        self.assertEqual(local_work.content_str, "Test content")
        self.assertEqual(local_work.content_type, "text")
        
        # 验证消息和关系
        self.assertEqual(len(complex_work.message_manager.get_all_messages()), 1)
        self.assertEqual(len(complex_work.relation_manager.relations), 1)
        
        # 测试无效输入
        with self.assertRaises(ConversionError):
            convert_simple_to_complex(self.complex)
    
    def test_convert_complex_to_simple(self):
        """测试convert_complex_to_simple函数"""
        simple_work = convert_complex_to_simple(self.complex)
        
        # 验证基本属性
        self.assertEqual(simple_work.name, "Test Complex")
        self.assertEqual(simple_work.logic_description, "Test complex workable")
        self.assertTrue(isinstance(simple_work, SimpleWorkable))
        
        # 验证内容
        self.assertEqual(simple_work.content_str, "Local content")
        
        # 添加子Workable，此时应该无法转换
        child = SimpleWorkable(
            name="Child",
            logic_description="Child workable",
            content_str="Child content"
        )
        self.complex.add_child(child)
        
        simple_work = convert_complex_to_simple(self.complex)
        self.assertIsNone(simple_work)
        
        # 添加第二个本地Workable，此时应该无法转换
        self.complex.remove_child(child.uuid)  # 先移除子Workable
        
        local2 = SimpleWorkable(
            name="Local 2",
            logic_description="Local workable 2",
            content_str="Local content 2"
        )
        self.complex.add_local(local2)
        
        simple_work = convert_complex_to_simple(self.complex)
        self.assertIsNone(simple_work)
        
        # 测试无效输入
        with self.assertRaises(ConversionError):
            convert_complex_to_simple(self.simple)


if __name__ == "__main__":
    unittest.main() 