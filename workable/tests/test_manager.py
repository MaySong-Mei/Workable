"""
测试Workable管理器
"""

import unittest
import logging
import uuid
from unittest.mock import patch, MagicMock

from workable.core.manager import WorkableManager
from workable.core.workable import SimpleWorkable, ComplexWorkable
from workable.core.exceptions import WorkableError, ManagerError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestWorkableManager(unittest.TestCase):
    """测试WorkableManager类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.manager = WorkableManager()
        
        # 创建一些测试Workable
        self.simple1 = SimpleWorkable(
            name="Simple 1",
            logic_description="Simple workable 1",
            content_str="Content 1",
            content_type="text"
        )
        
        self.simple2 = SimpleWorkable(
            name="Simple 2",
            logic_description="Simple workable 2",
            content_str="Content 2",
            content_type="text"
        )
        
        self.complex1 = ComplexWorkable(
            name="Complex 1",
            logic_description="Complex workable 1"
        )
        
        self.complex2 = ComplexWorkable(
            name="Complex 2",
            logic_description="Complex workable 2"
        )
    
    def test_register_workable(self):
        """测试register_workable方法"""
        # 注册SimpleWorkable
        self.manager.register_workable(self.simple1)
        
        # 验证是否已注册
        self.assertEqual(len(self.manager.workables), 1)
        self.assertIn(self.simple1.uuid, self.manager.workables)
        
        # 注册ComplexWorkable
        self.manager.register_workable(self.complex1)
        
        # 验证是否已注册
        self.assertEqual(len(self.manager.workables), 2)
        self.assertIn(self.complex1.uuid, self.manager.workables)
        
        # 重复注册同一个Workable
        with self.assertRaises(ManagerError):
            self.manager.register_workable(self.simple1)
        
        # 注册无效Workable
        with self.assertRaises(WorkableError):
            self.manager.register_workable("not a workable")
    
    def test_unregister_workable(self):
        """测试unregister_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.simple1)
        self.manager.register_workable(self.complex1)
        
        # 验证是否已注册
        self.assertEqual(len(self.manager.workables), 2)
        
        # 注销Workable
        result = self.manager.unregister_workable(self.simple1.uuid)
        
        # 验证是否已注销
        self.assertTrue(result)
        self.assertEqual(len(self.manager.workables), 1)
        self.assertNotIn(self.simple1.uuid, self.manager.workables)
        
        # 注销不存在的Workable
        result = self.manager.unregister_workable("non-existent-uuid")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_get_workable(self):
        """测试get_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.simple1)
        
        # 获取Workable
        workable = self.manager.get_workable(self.simple1.uuid)
        
        # 验证获取的Workable
        self.assertEqual(workable, self.simple1)
        
        # 获取不存在的Workable
        workable = self.manager.get_workable("non-existent-uuid")
        
        # 验证结果
        self.assertIsNone(workable)
    
    def test_get_all_workables(self):
        """测试get_all_workables方法"""
        # 注册Workable
        self.manager.register_workable(self.simple1)
        self.manager.register_workable(self.simple2)
        self.manager.register_workable(self.complex1)
        
        # 获取所有Workable
        workables = self.manager.get_all_workables()
        
        # 验证获取的Workables
        self.assertEqual(len(workables), 3)
        self.assertIn(self.simple1.uuid, workables)
        self.assertIn(self.simple2.uuid, workables)
        self.assertIn(self.complex1.uuid, workables)
        
        # 验证返回的是副本
        workables[self.simple1.uuid] = None
        self.assertEqual(len(self.manager.workables), 3)
    
    def test_get_workables_by_type(self):
        """测试get_workables_by_type方法"""
        # 注册Workable
        self.manager.register_workable(self.simple1)
        self.manager.register_workable(self.simple2)
        self.manager.register_workable(self.complex1)
        self.manager.register_workable(self.complex2)
        
        # 获取SimpleWorkable
        simples = self.manager.get_workables_by_type(SimpleWorkable)
        
        # 验证获取的SimpleWorkables
        self.assertEqual(len(simples), 2)
        self.assertIn(self.simple1.uuid, simples)
        self.assertIn(self.simple2.uuid, simples)
        self.assertNotIn(self.complex1.uuid, simples)
        self.assertNotIn(self.complex2.uuid, simples)
        
        # 获取ComplexWorkable
        complexes = self.manager.get_workables_by_type(ComplexWorkable)
        
        # 验证获取的ComplexWorkables
        self.assertEqual(len(complexes), 2)
        self.assertIn(self.complex1.uuid, complexes)
        self.assertIn(self.complex2.uuid, complexes)
        self.assertNotIn(self.simple1.uuid, complexes)
        self.assertNotIn(self.simple2.uuid, complexes)
    
    def test_create_simple_workable(self):
        """测试create_simple_workable方法"""
        # 创建SimpleWorkable
        simple_uuid = self.manager.create_simple_workable(
            name="New Simple",
            logic_description="New simple workable",
            content_str="New content",
            content_type="text"
        )
        
        # 验证创建的SimpleWorkable
        self.assertEqual(len(self.manager.workables), 1)
        self.assertIn(simple_uuid, self.manager.workables)
        
        workable = self.manager.get_workable(simple_uuid)
        self.assertEqual(workable.name, "New Simple")
        self.assertEqual(workable.logic_description, "New simple workable")
        self.assertEqual(workable.content_str, "New content")
        self.assertEqual(workable.content_type, "text")
        self.assertTrue(isinstance(workable, SimpleWorkable))
    
    def test_create_complex_workable(self):
        """测试create_complex_workable方法"""
        # 创建ComplexWorkable
        complex_uuid = self.manager.create_complex_workable(
            name="New Complex",
            logic_description="New complex workable"
        )
        
        # 验证创建的ComplexWorkable
        self.assertEqual(len(self.manager.workables), 1)
        self.assertIn(complex_uuid, self.manager.workables)
        
        workable = self.manager.get_workable(complex_uuid)
        self.assertEqual(workable.name, "New Complex")
        self.assertEqual(workable.logic_description, "New complex workable")
        self.assertTrue(isinstance(workable, ComplexWorkable))
    
    def test_update_workable(self):
        """测试update_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.simple1)
        
        # 更新Workable
        result = self.manager.update_workable(
            self.simple1.uuid,
            name="Updated Simple",
            logic_description="Updated description"
        )
        
        # 验证更新结果
        self.assertTrue(result)
        
        # 验证更新的Workable
        workable = self.manager.get_workable(self.simple1.uuid)
        self.assertEqual(workable.name, "Updated Simple")
        self.assertEqual(workable.logic_description, "Updated description")
        
        # 更新不存在的Workable
        result = self.manager.update_workable(
            "non-existent-uuid",
            name="Updated Name"
        )
        
        # 验证结果
        self.assertFalse(result)
    
    def test_update_simple_workable_content(self):
        """测试update_simple_workable_content方法"""
        # 注册SimpleWorkable
        self.manager.register_workable(self.simple1)
        
        # 更新SimpleWorkable内容
        result = self.manager.update_simple_workable_content(
            self.simple1.uuid,
            "Updated content"
        )
        
        # 验证更新结果
        self.assertTrue(result)
        
        # 验证更新的SimpleWorkable
        workable = self.manager.get_workable(self.simple1.uuid)
        self.assertEqual(workable.content_str, "Updated content")
        
        # 更新ComplexWorkable内容（应该失败）
        self.manager.register_workable(self.complex1)
        
        result = self.manager.update_simple_workable_content(
            self.complex1.uuid,
            "Updated content"
        )
        
        # 验证结果
        self.assertFalse(result)
        
        # 更新不存在的Workable
        result = self.manager.update_simple_workable_content(
            "non-existent-uuid",
            "Updated content"
        )
        
        # 验证结果
        self.assertFalse(result)
    
    def test_delete_workable(self):
        """测试delete_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.simple1)
        self.manager.register_workable(self.complex1)
        
        # 验证注册
        self.assertEqual(len(self.manager.workables), 2)
        
        # 删除Workable
        result = self.manager.delete_workable(self.simple1.uuid)
        
        # 验证删除结果
        self.assertTrue(result)
        self.assertEqual(len(self.manager.workables), 1)
        self.assertNotIn(self.simple1.uuid, self.manager.workables)
        
        # 删除不存在的Workable
        result = self.manager.delete_workable("non-existent-uuid")
        
        # 验证结果
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 